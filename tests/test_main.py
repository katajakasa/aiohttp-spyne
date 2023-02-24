import pytest
import zeep
import zeep.exceptions


async def test_simple_request(test_client):
    assert await test_client.service.ping("data") == "data"


async def test_big_request(test_client, normal_sized_string):
    assert await test_client.service.ping(normal_sized_string) == normal_sized_string


async def test_too_bit_request(test_client, pretty_big_string):
    with pytest.raises(zeep.exceptions.TransportError):
        await test_client.service.ping(pretty_big_string)
