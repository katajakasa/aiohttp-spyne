from aiohttp_spyne import AioApplication

from aiohttp import web
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11

# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.aio.hello_world


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, name, times):
        app = self.get_aiohttp_app()
        for i in range(times):
            yield app['test_text'] % name


def main():
    application = Application(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())

    spyne_app = AioApplication(application)
    spyne_app['test_text'] = "Hello, %s"

    app = web.Application()
    app.add_subapp('/say_hello/', spyne_app)
    web.run_app(app, port=8080)


if __name__ == '__main__':
    main()
