import typing

from aiohttp import web
from spyne import Application

from .aio_base import AioBase


class AIOSpyne:
    """
    AioHttp base for spyne framework.
    """

    def __init__(
        self,
        spyne_app: Application,
        chunked: bool = False,
        cache_wsdl: bool = True,
        threads: typing.Optional[int] = None,
    ) -> None:
        """
        Initialize Spyne aiohttp base.

        Args:
            spyne_app: Spyne application
            chunked: Enable chunked encoding
            cache_wsdl: Cache generated WSDL document
            threads: Thread count if thread pool is wanted for execution.
                     None if no threads are wanted.
        """
        self._base = AioBase(
            spyne_app, chunked=chunked, cache_wsdl=cache_wsdl, threads=threads
        )

    async def post(self, request: web.Request) -> web.StreamResponse:
        """
        Accepts POST SOAP requests and handles them.
        Returns standard AioHTTP response objects.

        Args:
            request: AioHttp Request object

        Returns:
            AioHttp response object
        """
        return await self._base.handle_rpc_request(request, request.app)

    async def get(self, request: web.Request) -> web.StreamResponse:
        """
        Accepts GET SOAP requests and handles them. If path is postfixed
        with either '.wsdl' or '?WSDL', request is handled as a WSDL
        fetch request.

        Args:
            request: Request object

        Returns:
            AioHttp response object
        """
        url = str(request.url).lower()
        if url.endswith("?wsdl") or url.endswith(".wsdl"):
            return await self._base.handle_wsdl_request(request, request.app)
        return await self._base.handle_rpc_request(request, request.app)
