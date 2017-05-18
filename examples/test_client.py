from zeep import Client
from zeep.asyncio import AsyncTransport
from zeep.cache import InMemoryCache
import time
import asyncio

"""
Spyne SOAP client using Zeep and async transport

python -m examples.aio.test_client
"""


def main():
    loop = asyncio.get_event_loop()
    transport = AsyncTransport(loop, cache=InMemoryCache())
    client = Client('http://localhost:8080/say_hello/?WSDL', transport=transport)

    start = time.time()
    tasks = []
    for m in range(10000):
        fut = asyncio.ensure_future(client.service.say_hello(times=1))
        tasks.append(fut)
    future = asyncio.gather(*tasks, return_exceptions=True)
    loop.run_until_complete(future)
    print(time.time() - start)

    loop.run_until_complete(transport.session.close())

if __name__ == '__main__':
    main()
