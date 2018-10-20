import typing

from spyne.server.http import HttpMethodContext

from .aio_transport_ctx import AioTransportContext

if typing.TYPE_CHECKING:
    from .aio_app import AioApplication  # noqa: F401


class AioMethodContext(HttpMethodContext):
    default_transport_context = AioTransportContext

    def __init__(self, *args, **kwargs):
        self._aiohttp_app: 'AioApplication' = kwargs.pop('aiohttp_app')
        super(AioMethodContext, self).__init__(*args, **kwargs)

    def get_aiohttp_app(self) -> 'AioApplication':
        return self._aiohttp_app
