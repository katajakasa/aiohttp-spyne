from aiohttp_spyne.aio_base import AioBase
from unittest.mock import Mock


async def test_wsdl_generator(application):
    base = AioBase(application, cache_wsdl=False)
    req = Mock(scheme="http", host="localhost", path="/test/a/")
    ret = await base._get_or_create_wsdl(req)

    assert ret.startswith("<?xml".encode())
    assert base._wsdl_cache == {}


async def test_wsdl_cache(application):
    base = AioBase(application, cache_wsdl=True)

    # Generate two separate WSDL docs to the cache
    assert await base._get_or_create_wsdl(
        Mock(scheme="http", host="localhost", path="/test/a/")
    )
    assert await base._get_or_create_wsdl(
        Mock(scheme="http", host="localhost", path="/test/b/")
    )

    # Find the correct keys
    assert "http://localhost/test/a/" in base._wsdl_cache
    assert "http://localhost/test/b/" in base._wsdl_cache

    # The same urls should also be in the WSDL content
    assert (
        "http://localhost/test/a/"
        in base._wsdl_cache["http://localhost/test/a/"].decode()
    )
    assert (
        "http://localhost/test/b/"
        in base._wsdl_cache["http://localhost/test/b/"].decode()
    )


async def test_wsdl_cache_match(application):
    base = AioBase(application, cache_wsdl=True)

    # Generate two WSDL files with matching URL
    assert await base._get_or_create_wsdl(
        Mock(scheme="http", host="localhost", path="/test/a/")
    )
    assert await base._get_or_create_wsdl(
        Mock(scheme="http", host="localhost", path="/test/a/")
    )

    # Should only contain one cache instance
    assert len(base._wsdl_cache) == 1
