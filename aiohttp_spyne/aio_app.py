from aiohttp import web
from aiohttp.signals import Signal

from .aio_base import AioBase


class AioApplication(web.Application):
    """
    Asynchronous application base for spyne framework.
    """

    def __init__(self, spyne_app, client_max_size=1024**2, **kwargs):
        super(AioApplication, self).__init__(client_max_size=client_max_size, **kwargs)
        self._base = AioBase(spyne_app, client_max_size=client_max_size, aiohttp_app=self)
        self.router.add_get('/{tail:.*}', self.handle_get)
        self.router.add_post('/{tail:.*}', self.handle_post)
        self._on_rpc_request_prepare = Signal(self)
        self._on_rpc_request_finish = Signal(self)

    async def handle_post(self, request):
        return await self._base.handle_rpc_request(request)

    async def handle_get(self, request):
        url = str(request.url).lower()
        if url.endswith('?wsdl') or url.endswith('.wsdl'):
            return await self._base.handle_wsdl_request(request)
        return await self._base.handle_rpc_request(request)

    def freeze(self):
        super(AioApplication, self).freeze()
        self._on_rpc_request_prepare.freeze()
        self._on_rpc_request_finish.freeze()

    @property
    def on_rpc_request_prepare(self):
        return self._on_rpc_request_prepare

    @property
    def on_rpc_request_finish(self):
        return self._on_rpc_request_finish

    async def rpc_request_prepare(self, app, context):
        await self.on_rpc_request_prepare.send(app, context)

    async def rpc_request_finish(self, app, context):
        await self.on_rpc_request_finish.send(app, context)

