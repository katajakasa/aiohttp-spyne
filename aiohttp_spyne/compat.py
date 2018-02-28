import aiohttp
from distutils.version import LooseVersion


def _use_aiohttp_drain():
    return LooseVersion(aiohttp.__version__) < LooseVersion('3.0.0')


USE_AIOHTTP_DRAIN = _use_aiohttp_drain()
