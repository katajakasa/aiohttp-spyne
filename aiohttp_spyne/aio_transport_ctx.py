import typing

from spyne import Address
from spyne.server.http import HttpTransportContext
from spyne.util.address import address_parser

if typing.TYPE_CHECKING:
    from aiohttp.web import Request  # noqa: F401

    from .aio_base import AioBase  # noqa: F401
    from .aio_method_ctx import AioMethodContext  # noqa: F401


class AioTransportContext(HttpTransportContext):
    def __init__(
        self,
        parent: "AioMethodContext",
        transport: "AioBase",
        req_env: "Request",
        content_type: str,
    ) -> None:
        super(AioTransportContext, self).__init__(
            parent, transport, req_env, content_type
        )
        self.req_env = req_env
        self.content_type = content_type

    def get_path(self) -> str:
        return self.req_env.path

    def get_path_and_qs(self) -> str:
        return self.req_env.path_qs

    def get_cookie(self, key) -> str:
        return self.req_env.cookies[key]

    def get_request_method(self) -> str:
        return self.req_env.method

    def get_request_content_type(self) -> str:
        return self.content_type

    def get_peer(self) -> typing.Optional[Address]:
        if not self.req_env.transport:
            return None

        peer = self.req_env.transport.get_extra_info("peername")
        if not peer:
            return None
        host, port = peer

        if address_parser.is_valid_ipv4(host):
            return Address(type=Address.TCP4, host=host, port=port)

        if address_parser.is_valid_ipv6(host):
            return Address(type=Address.TCP6, host=host, port=port)

        return None
