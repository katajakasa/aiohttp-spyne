from zeep import Client
from zeep.asyncio import AsyncTransport
from zeep.cache import InMemoryCache
import time
import asyncio

# Spyne SOAP client using Zeep and async transport. Run with python -m examples.test_client


def main():
    loop = asyncio.get_event_loop()
    transport = AsyncTransport(loop, cache=InMemoryCache())
    client = Client('http://localhost:8080/say_hello/?WSDL', transport=transport)

    tasks = []
    for m in range(10000):
        fut = asyncio.ensure_future(client.service.say_hello(name='Tester', times=1))
        tasks.append(fut)

    start = time.time()
    future = asyncio.gather(*tasks, return_exceptions=True)
    loop.run_until_complete(future)
    print(time.time() - start)

    loop.run_until_complete(transport.session.close())


if __name__ == '__main__':
    main()
