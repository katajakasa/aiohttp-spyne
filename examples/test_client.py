import asyncio
import platform
import time

from zeep import AsyncClient
from zeep.cache import InMemoryCache
from zeep.transports import AsyncTransport

# Spyne SOAP client using Zeep and async transport. Run with python -m examples.test_client


# Allow CTRL+C on windows console w/ asyncio
if platform.system() == "Windows":
    import signal

    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def do_call(client, text, number):
    result = await client.service.say_hello(text=text, number=number)
    return result == "{} {}".format(text, number)


def generate_tasks(client):
    tasks = []
    for m in range(10000):
        tasks.append(asyncio.ensure_future(do_call(client, "Tester", m)))
    return tasks


async def send_messages(client):
    start = time.time()
    results = await asyncio.gather(*generate_tasks(client))
    delta_time = time.time() - start
    print("Result: ", all(results))
    print(delta_time)


async def main():
    client = AsyncClient(
        wsdl="http://localhost:8080/say_hello/?WSDL",
        transport=AsyncTransport(cache=InMemoryCache(timeout=None)),
    )
    await send_messages(client)
    await client.transport.aclose()


if __name__ == "__main__":
    asyncio.run(main())
