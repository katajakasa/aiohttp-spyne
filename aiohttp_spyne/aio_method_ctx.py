from aiohttp.web import Application
from spyne.server.http import HttpMethodContext

from .aio_transport_ctx import AioTransportContext


class AioMethodContext(HttpMethodContext):
    HttpTransportContext = AioTransportContext

    def __init__(self, *args, **kwargs) -> None:
        self._aiohttp_app: Application = kwargs.pop("aiohttp_app")
        super(AioMethodContext, self).__init__(*args, **kwargs)

    def get_aiohttp_app(self) -> Application:
        return self._aiohttp_app
