import platform
import asyncio

from aiohttp import web
from spyne import Application as SpyneApplication, rpc, ServiceBase, Integer, Unicode
from spyne.protocol.soap import Soap11

from aiohttp_spyne import AIOSpyne


# Spyne SOAP server using Aiohttp as transport. Run with python -m examples.hello_world_threads


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == 'Windows':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def run_in_main_loop(text, number):
    return "{} {}".format(text, number)


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Integer, _returns=Unicode)
    def say_hello(self, text, number):
        app = self.get_aiohttp_app()  # This is the web.Application object

        # Since this function is threaded, we can run tasks asynchronously in the main loop.
        # Note that they need to be run in a thread-safe manner!
        fut = asyncio.run_coroutine_threadsafe(run_in_main_loop(text, number), app.loop)
        return fut.result()


def main():
    spyne_app = SpyneApplication(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())

    handler = AIOSpyne(spyne_app, threads=25)

    app = web.Application()
    app.router.add_get('/{tail:.*}', handler.get)
    app.router.add_post('/{tail:.*}', handler.post)
    web.run_app(app, port=8080)


if __name__ == '__main__':
    main()
