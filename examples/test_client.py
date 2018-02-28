from zeep import Client
from zeep.asyncio import AsyncTransport
from zeep.cache import InMemoryCache
import time
import asyncio

# Spyne SOAP client using Zeep and async transport. Run with python -m examples.test_client
# Note that at the time of writing, Zeep only works with aiohttp>=2.00,<3.0.0 !


def make_client(loop, endpoint):
    return


def generate_tasks(client):
    tasks = []
    for m in range(10000):
        tasks.append(asyncio.ensure_future(client.service.say_hello(name='Tester', times=m % 10)))
    return tasks


async def send_messages(client):
    start = time.time()
    await asyncio.gather(*generate_tasks(client), return_exceptions=True)
    print(time.time() - start)


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
