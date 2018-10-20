import platform
import asyncio

from aiohttp_spyne import AioApplication

from aiohttp.web import run_app
from spyne import Application as SpyneApplication, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11

# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.hello_world_threads


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == 'Windows':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def run_in_main_loop(text, number):
    return "{} {}".format(text, number)


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, text, number):
        app = self.get_aiohttp_app()  # This is the AioApplication object

        # Since this function is threaded, we can run tasks asynchronously in the main loop.
        # Note that they need to be run in a thread-safe manner!
        fut = asyncio.run_coroutine_threadsafe(run_in_main_loop(text, number), app.loop)
        yield fut.result()


def main():
    spyne_app = SpyneApplication(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())

    app = AioApplication(spyne_app, route_prefix='/say_hello/', threads=25)
    run_app(app, port=8080)


if __name__ == '__main__':
    main()
