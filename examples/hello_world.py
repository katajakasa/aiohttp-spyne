import platform
import logging

from aiohttp import web
from spyne import Application as SpyneApplication, rpc, ServiceBase, Integer, Unicode
from spyne.protocol.soap import Soap11

from aiohttp_spyne import AIOSpyne

# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.hello_world


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == "Windows":
    import signal

    signal.signal(signal.SIGINT, signal.SIG_DFL)


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Unicode)
    def say_hello(self, text, number):
        app = self.get_aiohttp_app()  # This is the web.Application object
        return app["text"] % (text, number)


def main():
    logging.basicConfig(level=logging.WARNING)

    spyne_app = SpyneApplication(
        [HelloWorldService],
        tns="aiohttp_spyne.examples.hello",
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )

    handler = AIOSpyne(spyne_app)

    app = web.Application()
    app["text"] = "%s %s"
    app.router.add_get("/say_hello/{tail:.*}", handler.get)
    app.router.add_post("/say_hello/{tail:.*}", handler.post)
    web.run_app(app, port=8080)


if __name__ == "__main__":
    main()
