import platform
import asyncio
import random

from aiohttp_spyne import AioApplication

from aiohttp.web import Application as WebApplication, run_app
from spyne import Application as SpyneApplication, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11

# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.hello_world


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == 'Windows':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def run_in_main_loop(text, number):
    t = random.random()
    await asyncio.sleep(t)
    print("Sleep done {}".format(t))
    return "{} {}".format(text, number)


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, name, times):
        app = self.get_aiohttp_app()  # This is the AioApplication object
        fut = asyncio.run_coroutine_threadsafe(run_in_main_loop(name, times), app.loop)
        yield fut.result()


def main():
    application = SpyneApplication(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())

    spyne_app = AioApplication(application, threads=50)

    app = WebApplication()
    app.add_subapp('/say_hello/', spyne_app)
    run_app(app, port=8080)


if __name__ == '__main__':
    main()
