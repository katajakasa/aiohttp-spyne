import platform

from aiohttp_spyne import AioApplication

from aiohttp.web import run_app
from spyne import Application as SpyneApplication, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11

# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.hello_world


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == 'Windows':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, text, number):
        app = self.get_aiohttp_app()  # This is the AioApplication object
        yield app['text'] % (text, number)


def main():
    spyne_app = SpyneApplication(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())

    app = AioApplication(spyne_app, route_prefix='/say_hello/')
    app['text'] = '%s %s'
    run_app(app, port=8080)


if __name__ == '__main__':
    main()
