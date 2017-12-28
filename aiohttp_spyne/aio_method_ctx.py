from spyne.server.http import HttpMethodContext

from .aio_transport_ctx import AioTransportContext


class AioMethodContext(HttpMethodContext):
    default_transport_context = AioTransportContext

    def __init__(self, *args, **kwargs):
        self._aiohttp_app = kwargs.pop('aiohttp_app')
        super(AioMethodContext, self).__init__(*args, **kwargs)

    def get_aiohttp_app(self):
        return self._aiohttp_app
