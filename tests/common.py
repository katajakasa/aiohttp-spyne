import random
import string

import zeep
from aiohttp import web
from spyne import Application, ServiceBase, Unicode, rpc
from spyne.protocol.soap import Soap11

from aiohttp_spyne import AIOSpyne

HOSTNAME = "127.0.0.1"
PORT = 49555


def generate_random_str(size: int = 1024**2):
    k = "".join(random.sample(string.ascii_letters, 32))

    out = ""
    for m in range(int(size / 32) + 1):
        out += k

    if len(out) > size:
        return out[:size]
    return out


def get_client():
    return zeep.Client(f"http://{HOSTNAME}:{PORT}/?wsdl")


def spyne_app_process():
    class TestService(ServiceBase):
        @rpc(Unicode, _returns=Unicode)
        def ping(self, data):
            return data

    spyne_app = Application(
        [TestService],
        tns="aiohttp_spyne.tests.test",
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )

    handler = AIOSpyne(spyne_app)

    app = web.Application(client_max_size=1024**2 * 2)
    app.router.add_get("/{tail:.*}", handler.get)
    app.router.add_post("/{tail:.*}", handler.post)
    web.run_app(app, host="0.0.0.0", port=PORT)
