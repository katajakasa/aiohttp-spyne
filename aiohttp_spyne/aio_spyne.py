import typing

from aiohttp import web
from spyne import Application

from .aio_base import AioBase


class AIOSpyne:
    """
    AioHttp base for spyne framework.
    """

    def __init__(self,
                 spyne_app: Application,
                 client_max_size: int = 1024**2,
                 chunked: bool = True,
                 threads: typing.Optional[int] = None):
        """
        Initialize Spyne aiohttp base.

        Args:
            spyne_app: Spyne application
            client_max_size: Maximum payload size
            chunked: Enable chunked encoding
            threads: Thread count if thread pool is wanted for execution.
                     None if no threads are wanted.
        """
        self._base = AioBase(
            spyne_app,
            client_max_size=client_max_size,
            chunked=chunked,
            threads=threads)

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
        if url.endswith('?wsdl') or url.endswith('.wsdl'):
            return await self._base.handle_wsdl_request(request, request.app)
        return await self._base.handle_rpc_request(request, request.app)
