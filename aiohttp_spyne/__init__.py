import logging
import threading
from urllib.parse import urlunparse

from aiohttp import web

from spyne.model.fault import Fault
from spyne.application import get_fault_string_from_exception
from spyne.protocol.http import HttpRpc
from spyne.auxproc import process_contexts
from spyne.server.http import HttpBase
from spyne.server.http import HttpMethodContext
from spyne.server.http import HttpTransportContext

logger = logging.getLogger(__name__)


class AioTransportContext(HttpTransportContext):
    def __init__(self, parent, transport, req_env, content_type):
        super(AioTransportContext, self).__init__(parent, transport, req_env, content_type)
        self.req_env = req_env
        self.content_type = content_type

    def get_path(self):
        return self.req_env.path

    def get_path_and_qs(self):
        return self.req_env.path_qs

    def get_cookie(self, key):
        return self.req_env.cookies[key]

    def get_request_method(self):
        return self.req_env.method

    def get_request_content_type(self):
        return self.content_type


class AioMethodContext(HttpMethodContext):
    default_transport_context = AioTransportContext

    def __init__(self, *args, **kwargs):
        self._aiohttp_app = kwargs.pop('aiohttp_app')
        super(AioMethodContext, self).__init__(*args, **kwargs)

    def get_aiohttp_app(self):
        return self._aiohttp_app


class AioBase(HttpBase):
    def __init__(self, app, client_max_size, aiohttp_app):
        super(AioBase, self).__init__(app, max_content_length=client_max_size)
        self._mtx_build_interface_document = threading.Lock()
        self._wsdl = None
        self._aiohttp_app = aiohttp_app
        if self.doc.wsdl11 is not None:
            self._wsdl = self.doc.wsdl11.get_interface_document()

    @classmethod
    def make_direct_response(cls, code, headers=None, content=None):
        if not headers:
            headers = []
        if not content:
            content = ''
        return web.Response(status=code, headers=headers, body=content)

    @staticmethod
    async def make_streaming_response(req, code, content, headers=None):
        if not headers:
            headers = []

        response = web.StreamResponse(status=code, headers=headers)
        await response.prepare(req)
        for chunk in content:
            response.write(chunk)
            await response.drain()
        return response

    async def response(self, req, p_ctx, others, error=None):
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
            code=status_code,
            headers=p_ctx.transport.resp_headers)

    async def handle_error(self, req, p_ctx, others, error):
        if p_ctx.transport.resp_code is None:
            p_ctx.transport.resp_code = p_ctx.out_protocol.fault_to_http_response_code(error)
        self.get_out_string(p_ctx)
        return await self.response(req, p_ctx, others, error)

    async def handle_wsdl_request(self, req):
        ctx = AioMethodContext(self, req, 'text/xml; charset=utf-8',
                               aiohttp_app=self._aiohttp_app)

        if self.doc.wsdl11 is None:
            raise web.HTTPNotFound(headers=ctx.transport.resp_headers)

        if self._wsdl is None:
            self._wsdl = self.doc.wsdl11.get_interface_document()

        ctx.transport.wsdl = self._wsdl

        if ctx.transport.wsdl is None:
            with self._mtx_build_interface_document:
                try:
                    ctx.transport.wsdl = self._wsdl
                    if ctx.transport.wsdl is None:
                        actual_url = urlunparse([req.scheme, req.host, req.path, '', '', ''])
                        self.doc.wsdl11.build_interface_document(actual_url)
                        ctx.transport.wsdl = self._wsdl = self.doc.wsdl11.get_interface_document()
                except Exception as e:
                    logger.exception(e)
                    ctx.transport.wsdl_error = e
                    self.event_manager.fire_event('wsdl_exception', ctx)
                    raise web.HTTPInternalServerError(headers=ctx.transport.resp_headers)

        self.event_manager.fire_event('wsdl', ctx)

        ctx.transport.resp_headers['Content-Length'] = str(len(ctx.transport.wsdl))
        ctx.close()

        return await self.make_streaming_response(
            req=req,
            code=200,
            headers=ctx.transport.resp_headers,
            content=[ctx.transport.wsdl])

    async def handle_rpc_request(self, req):
        body = await req.read()
        initial_ctx = AioMethodContext(self, req, self.app.out_protocol.mime_type,
                                       aiohttp_app=self._aiohttp_app)
        initial_ctx.in_string = [body]
        contexts = self.generate_contexts(initial_ctx)
        p_ctx, others = contexts[0], contexts[1:]

        if p_ctx.in_error:
            return await self.handle_error(req, p_ctx, others, p_ctx.in_error)

        self.get_in_object(p_ctx)
        if p_ctx.in_error:
            logger.error(p_ctx.in_error)
            return await self.handle_error(req, p_ctx, others, p_ctx.in_error)

        self.get_out_object(p_ctx)
        if p_ctx.out_error:
            return await self.handle_error(req, p_ctx, others, p_ctx.out_error)

        try:
            self.get_out_string(p_ctx)
        except Exception as e:
            logger.exception(e)
            p_ctx.out_error = Fault('Server', get_fault_string_from_exception(e))
            return await self.handle_error(req, p_ctx, others, p_ctx.out_error)

        have_protocol_headers = (isinstance(p_ctx.out_protocol, HttpRpc) and
                                 p_ctx.out_header_doc is not None)

        if have_protocol_headers:
            p_ctx.transport.resp_headers.update(p_ctx.out_header_doc)

        if p_ctx.descriptor and p_ctx.descriptor.mtom:
            raise NotImplementedError

        return await self.response(req, p_ctx, others)


class AioApplication(web.Application):
    def __init__(self, spyne_app, client_max_size=1024**2, **kwargs):
        super(AioApplication, self).__init__(client_max_size=client_max_size, **kwargs)
        self.base = AioBase(spyne_app, client_max_size=client_max_size, aiohttp_app=self)
        self.router.add_get('/{tail:.*}', self.handle_get)
        self.router.add_post('/{tail:.*}', self.handle_post)

    async def handle_post(self, request):
        return await self.base.handle_rpc_request(request)

    async def handle_get(self, request):
        url = str(request.url).lower()
        if url.endswith('?wsdl') or url.endswith('.wsdl'):
            return await self.base.handle_wsdl_request(request)
        return await self.base.handle_rpc_request(request)
