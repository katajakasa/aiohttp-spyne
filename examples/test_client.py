import time
import asyncio
import platform

from zeep import Client
from zeep.asyncio import AsyncTransport
from zeep.cache import InMemoryCache

# Spyne SOAP client using Zeep and async transport. Run with python -m examples.test_client


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == 'Windows':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def do_call(client, text, number):
    result = await client.service.say_hello(text=text, number=number)
    return result == "{} {}".format(text, number)


def generate_tasks(client):
    tasks = []
    for m in range(10000):
        tasks.append(asyncio.ensure_future(do_call(client, 'Tester', m)))
    return tasks


async def send_messages(client):
    start = time.time()
    results = await asyncio.gather(*generate_tasks(client))
    delta_time = time.time() - start
    print("Result: ", all(results))
    print(delta_time)


def main():
    loop = asyncio.get_event_loop()
    client = Client(
        wsdl='http://localhost:8080/say_hello/?WSDL',
        transport=AsyncTransport(
            loop=loop,
            cache=InMemoryCache(timeout=None)
        )
    )
    loop.run_until_complete(send_messages(client))
    loop.run_until_complete(client.transport.session.close())


if __name__ == '__main__':
    main()
