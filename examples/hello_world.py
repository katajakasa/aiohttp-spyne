from aiohttp_spyne import AioApplication

from aiohttp import web
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11

# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.hello_world


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, name, times):
        app = self.get_aiohttp_app()  # This is the AioApplication object
        for i in range(times):
            yield self.udc['text'] % name


async def on_req_prepare(app, context):
    """
    Prepare request context. This will be called before any RPC requests are handled.
    This is aiohttp implementation specific stuff, not supported in other spyne transports.
    """

    # Save arbitrary context data to udc (=user defined context) variable
    # This can be then accessed in RPC handler
    context.udc = dict(text=app['test_text'])


async def on_req_finish(app, context):
    """
    Finish request context. This will be called, does not matter if request handler succeeded or failed.
    This is aiohttp implementation specific stuff, not supported in other spyne transports.
    """
    del context.udc['text']


def main():
    application = Application(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())

    spyne_app = AioApplication(application)
    spyne_app['test_text'] = "Hello, %s"
    spyne_app.on_rpc_request_prepare.append(on_req_prepare)
    spyne_app.on_rpc_request_finish.append(on_req_finish)

    app = web.Application()
    app.add_subapp('/say_hello/', spyne_app)
    web.run_app(app, port=8080)


if __name__ == '__main__':
    main()
