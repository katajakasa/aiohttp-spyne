.. image:: https://travis-ci.org/katajakasa/aiohttp-spyne.svg?branch=master
    :target: https://travis-ci.org/katajakasa/aiohttp-spyne
    :alt: Build status

About
=====

Aiohttp transport for Spyne RPC library.

Requirements:

* Python >= 3.7
* Aiohttp >= 3.7.0
* Spyne >= 2.13.16

Spyne alpha versions should also work.

Installation
------------

Just run ``pip install aiohttp-spyne`` :)

Examples
--------

* Test server: ``python -m examples.hello_world``
* Threaded test server: ``python -m examples.hello_world_threads``
* Test client: ``python -m examples.test_client``

Usage
-----

First, initialize your spyne application as normal. Here's an example
for a simple SOAP service (See examples for a more complete service setup).

::

    spyne_app = spyne.Application(
        [HelloWorldService],
        tns='aiohttp_spyne.examples.hello',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11())


Next, wrap your Spyne application with AIOSpyne. Note that you can run
your application entrypoints in a thread by setting the threads parameter.
If you want to keep your entrypoints running in the same thread as the
main application, just leave this None. If you DO run your entrypoints
in threads, be aware that some signals sent by spyne will also be run
in threads, and be extra careful of using your main loop!

::

    handler = AIOSpyne(spyne_app, threads=25)


Lastly, make an aiohttp application as usual, and just bind GET and POST
entrypoints from AIOSpyne to wherever. Note that both paths need to be
the same.

With GET, if the request address ends ?wsdl or .wsdl, a WSDL schema is
returned in a response. Otherwise requests are redirected to spynes
RPC handler.

::

    app = web.Application()
    app.router.add_get('/{tail:.*}', handler.get)
    app.router.add_post('/{tail:.*}', handler.post)
    web.run_app(app, port=8080)

Testing and formatting
----------------------

1. ``pytest``
2. ``mypy -p aiohttp_spyne``
3. ``flake8``
4. ``black aiohttp_spyne/``

License
-------

LGPL-2.1 -- Please see LICENSE for details.
