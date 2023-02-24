import asyncio
import secrets
from functools import partial

import zeep
from aiohttp import web
from aiohttp.test_utils import TestServer
from pytest import fixture
from spyne import ServiceBase, Unicode, rpc, Application
from spyne.protocol.soap import Soap11

from aiohttp_spyne import AIOSpyne


def generate_random_str(size: int = 1024**2) -> str:
    out = secrets.token_urlsafe(24) * int(size / 32 + 1)
    return out[:size]


class TestService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def ping(self, data):
        return data


@fixture
def application():
    return Application(
        [TestService],
        tns="aiohttp_spyne.tests.test",
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )


@fixture
def async_application(application):
    return AIOSpyne(application)


@fixture
def spyne_app(async_application):
    app = web.Application(client_max_size=1024**2 * 2)
    app.router.add_get("/{tail:.*}", async_application.get)
    app.router.add_post("/{tail:.*}", async_application.post)
    return app


@fixture
async def test_client(spyne_app, unused_tcp_port):
    server = TestServer(spyne_app, host="127.0.0.1", port=unused_tcp_port)
    async with server:
        address = str(server.make_url("/?wsdl"))
        client = await asyncio.get_running_loop().run_in_executor(
            None, partial(zeep.AsyncClient, address)
        )
        yield client


@fixture
def pretty_big_string():
    return generate_random_str(1024**2 * 2)


@fixture
def normal_sized_string():
    return generate_random_str(1024**2)
