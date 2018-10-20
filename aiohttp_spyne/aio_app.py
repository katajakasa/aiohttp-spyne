import typing
import urllib.parse

from aiohttp import web
import spyne

from .aio_base import AioBase


class AioApplication(web.Application):
    """
    Asynchronous application base for spyne framework.
    """

    def __init__(self,
                 spyne_app: spyne.Application,
                 route_prefix: str = '/',
                 client_max_size: int = 1024**2,
                 chunked: bool = True,
                 threads: typing.Optional[int] = None):
        """
        Initialize spyne aiohttp application.

        Args:
            spyne_app: Spyne application
            client_max_size: Maximum payload size
            chunked: Enable chunked encoding
            threads: Thread count if thread pool is wanted for execution.
                     None if no threads are wanted.
        """
        super(AioApplication, self).__init__(
            client_max_size=client_max_size)
        self._base = AioBase(
            spyne_app,
            client_max_size=client_max_size,
            chunked=chunked,
            threads=threads)
        route_path = urllib.parse.urljoin(route_prefix, '{tail:.*}')
        self.router.add_get(route_path, self._handle_get)
        self.router.add_post(route_path, self._handle_post)

    async def _handle_post(self, request: web.Request) -> web.StreamResponse:
        return await self._base.handle_rpc_request(request, self)

    async def _handle_get(self, request: web.Request) -> web.StreamResponse:
        url = str(request.url).lower()
        if url.endswith('?wsdl') or url.endswith('.wsdl'):
            return await self._base.handle_wsdl_request(request, self)
        return await self._base.handle_rpc_request(request, self)
