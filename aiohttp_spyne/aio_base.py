import asyncio
import functools
import logging
import typing
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlunparse

from aiohttp import web
from spyne import Application
from spyne.application import get_fault_string_from_exception
from spyne.auxproc import process_contexts
from spyne.interface import AllYourInterfaceDocuments
from spyne.model.fault import Fault
from spyne.protocol.http import HttpRpc
from spyne.server import ServerBase

from .aio_method_ctx import AioMethodContext

logger = logging.getLogger(__name__)


class AioBase(ServerBase):
    transport = "http://schemas.xmlsoap.org/soap/http"

    def __init__(
        self,
        app: Application,
        chunked: bool = False,
        cache_wsdl: bool = True,
        threads: typing.Optional[int] = None,
    ) -> None:
        super(AioBase, self).__init__(app)
        self._chunked: bool = chunked
        self._cache_wsdl: bool = cache_wsdl
        self._wsdl: typing.Optional[bytes] = None
        self._thread_pool: typing.Optional[ThreadPoolExecutor] = None
        if threads:
            self._thread_pool = ThreadPoolExecutor(max_workers=threads)

    @staticmethod
    async def make_streaming_response(
        req: web.Request,
        status: int,
        content: typing.Iterable[bytes],
        chunked: bool = False,
        headers: typing.Optional[dict] = None,
    ) -> web.StreamResponse:
        response = web.StreamResponse(status=status, headers=headers)

        # If chunked encoding is requested, then enable it and leave
        # content-length unset. If we're not using chunked, set the
        # content-length by summing size of all content blocks.
        if chunked:
            response.enable_chunked_encoding()
        else:
            response.content_length = sum(len(c) for c in content)

        await response.prepare(req)
        for chunk in content:
            await response.write(chunk)
        return response

    async def response(
        self,
        req: web.Request,
        p_ctx: AioMethodContext,
        others: list,
        error: typing.Optional[Fault] = None,
    ) -> web.StreamResponse:
        status_code = 200
        if p_ctx.transport.resp_code:
            status_code = int(p_ctx.transport.resp_code[:3])

        try:
            process_contexts(self, others, p_ctx, error=error)
        except Exception as e:
            logger.exception(e)

        p_ctx.close()

        return await self.make_streaming_response(
            req=req,
            content=p_ctx.out_string,
            status=status_code,
            chunked=self._chunked,
            headers=p_ctx.transport.resp_headers,
        )

    async def handle_error(
        self,
        req: web.Request,
        p_ctx: AioMethodContext,
        others: list,
        error: typing.Optional[Fault],
    ) -> web.StreamResponse:
        if p_ctx.transport.resp_code is None:
            p_ctx.transport.resp_code = p_ctx.out_protocol.fault_to_http_response_code(
                error
            )
        self.get_out_string(p_ctx)
        return await self.response(req, p_ctx, others, error)

    def _generate_wsdl(self, req: web.Request) -> bytes:
        """Requests spyne to generate a new WSDL document"""
        actual_url = urlunparse([req.scheme, req.host, req.path, "", "", ""])
        doc = AllYourInterfaceDocuments(self.app.interface)
        doc.wsdl11.build_interface_document(actual_url)
        return doc.wsdl11.get_interface_document()

    async def _get_or_create_wsdl(self, req: web.Request) -> bytes:
        """
        Gets a cached WSDL document, or generates a new one. If caching is
        disabled, always generates a new one.
        """
        if self._wsdl:
            return self._wsdl
        wsdl_doc = self._generate_wsdl(req)
        if self._cache_wsdl:
            self._wsdl = wsdl_doc
        return wsdl_doc

    async def handle_wsdl_request(
        self, req: web.Request, app: web.Application
    ) -> web.StreamResponse:
        """Handle WSDL document requests"""
        ctx = AioMethodContext(self, req, "text/xml; charset=utf-8", aiohttp_app=app)
        if self.doc.wsdl11 is None:
            raise web.HTTPNotFound(headers=ctx.transport.resp_headers)

        # Generate or get cached wsdl
        try:
            ctx.transport.wsdl = await self._get_or_create_wsdl(req)
        except Exception as e:
            logger.exception(e)
            ctx.transport.wsdl_error = e
            self.event_manager.fire_event("wsdl_exception", ctx)
            raise web.HTTPInternalServerError(headers=ctx.transport.resp_headers)

        self.event_manager.fire_event("wsdl", ctx)
        ctx.close()

        return await self.make_streaming_response(
            req=req,
            status=200,
            headers=ctx.transport.resp_headers,
            chunked=False,
            content=[ctx.transport.wsdl],
        )

    async def handle_rpc_request(
        self, req: web.Request, app: web.Application
    ) -> web.StreamResponse:
        # First, read content from aiohttp
        body = await req.read()

        # Create the spyne context
        initial_ctx = AioMethodContext(
            self, req, self.app.out_protocol.mime_type, aiohttp_app=app
        )
        initial_ctx.in_string = [body]
        contexts = self.generate_contexts(initial_ctx)
        p_ctx, others = contexts[0], contexts[1:]

        # Make sure that context creation was okay. Respond with error if not.
        if p_ctx.in_error:
            return await self.handle_error(req, p_ctx, others, p_ctx.in_error)

        # Run in thread pool if enabled, otherwise skip
        if self._thread_pool:
            loop = asyncio.get_event_loop()
            error = await loop.run_in_executor(
                self._thread_pool, functools.partial(self._handle_rpc_body, p_ctx)
            )
        else:
            error = self._handle_rpc_body(p_ctx)

        # If handler made a mess, return error now.
        if error:
            return await self.handle_error(req, p_ctx, others, error)

        # MTOM is not supported. Just raise if it's requested.
        if p_ctx.descriptor and p_ctx.descriptor.mtom:
            raise NotImplementedError

        # Write successful response, that's that
        return await self.response(req, p_ctx, others)

    def _handle_rpc_body(self, p_ctx) -> typing.Optional[Fault]:
        """
        Do the heavy lifting of the request handling here. This can be run in a thread.
        """
        self.get_in_object(p_ctx)
        if p_ctx.in_error:
            logger.error(p_ctx.in_error)
            return p_ctx.in_error

        self.get_out_object(p_ctx)
        if p_ctx.out_error:
            logger.error(p_ctx.out_error)
            return p_ctx.out_error

        try:
            self.get_out_string(p_ctx)
        except Exception as e:
            p_ctx.out_error = Fault("Server", get_fault_string_from_exception(e))
            logger.exception(p_ctx.out_error, exc_info=e)
            return p_ctx.out_error

        have_protocol_headers = (
            isinstance(p_ctx.out_protocol, HttpRpc) and p_ctx.out_header_doc is not None
        )
        if have_protocol_headers:
            p_ctx.transport.resp_headers.update(p_ctx.out_header_doc)

        return None
