"""Test HTTP handling with a minimal aiohttp transport double.

This does not emulate Home Assistant or prove aiohttp/HA runtime compatibility.
It tests timeouts, status failures, size limits and shared-session ownership.
"""

import asyncio
from functools import wraps
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components/pogoda_by"


class ClientError(Exception):
    pass


class ClientTimeout:
    def __init__(self, *, total):
        self.total = total


fake_aiohttp = types.ModuleType("aiohttp")
fake_aiohttp.ClientError = ClientError
fake_aiohttp.ClientTimeout = ClientTimeout


def load_api():
    # Load under a private package, without executing the HA-facing __init__.py.
    package = types.ModuleType("_test_pogoda")
    package.__path__ = [str(ROOT)]
    sys.modules[package.__name__] = package
    original = sys.modules.get("aiohttp")
    sys.modules["aiohttp"] = fake_aiohttp
    try:
        name = "_test_pogoda.api"
        spec = importlib.util.spec_from_file_location(name, ROOT / "api.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("aiohttp", None)
        else:
            sys.modules["aiohttp"] = original


api = load_api()


class Response:
    charset = "utf-8"

    def __init__(self, body=b"", error=None):
        self.body = body
        self.error = error
        self.content = self
        self.exited = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.exited = True

    def raise_for_status(self):
        if self.error:
            raise self.error

    async def iter_chunked(self, size):
        for offset in range(0, len(self.body), size):
            yield self.body[offset:offset + size]


class Session:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def immediate(coro_test):
    """Drive our immediate transport doubles without Windows socketpair setup."""
    @wraps(coro_test)
    def run(self):
        coroutine = coro_test(self)
        try:
            coroutine.send(None)
        except StopIteration:
            return
        finally:
            coroutine.close()
        raise AssertionError("Transport double unexpectedly attempted real asynchronous IO")
    return run


class ApiTests(unittest.TestCase):
    @immediate
    async def test_country_catalogue_with_bom(self):
        response = Response('\ufeff{"BY":[{"id":26851,"name":"Минск"}]}'.encode())
        session = Session(response)
        result = await api.PogodaByClient(session).async_catalog()
        self.assertIn("26851", result["BY"])
        self.assertEqual(session.calls[0][1]["timeout"].total, 30)
        self.assertTrue(response.exited)

    @immediate
    async def test_only_selected_station_requested(self):
        body = '<rss><channel><item><description>Температура 0°C</description></item></channel></rss>'
        session = Session(Response(body.encode()))
        result = await api.PogodaByClient(session).async_observation("26851")
        self.assertEqual(session.calls[0][1]["params"], {"station": "26851"})
        self.assertEqual(result.values["temperature"], 0)

    @immediate
    async def test_connection_and_timeout_are_recoverable_errors(self):
        for error in (ClientError("network"), asyncio.TimeoutError()):
            with self.subTest(error=type(error).__name__), self.assertRaises(api.CannotConnect):
                await api.PogodaByClient(Session(error=error)).async_catalog()

    @immediate
    async def test_http_failure_closes_response(self):
        response = Response(error=ClientError("HTTP 503"))
        with self.assertRaises(api.CannotConnect):
            await api.PogodaByClient(Session(response)).async_catalog()
        self.assertTrue(response.exited)

    @immediate
    async def test_response_limit(self):
        response = Response(b"x" * (api.MAX_RESPONSE_BYTES + 1))
        with self.assertRaises(api.InvalidData):
            await api.PogodaByClient(Session(response)).async_catalog()
        self.assertTrue(response.exited)

    @immediate
    async def test_non_json_is_invalid_data(self):
        with self.assertRaises(api.InvalidData):
            await api.PogodaByClient(Session(Response(b"<html>error</html>"))).async_catalog()

    @immediate
    async def test_invalid_encoding_is_connection_error(self):
        with self.assertRaises(api.CannotConnect):
            await api.PogodaByClient(Session(Response(b"\xff"))).async_catalog()


if __name__ == "__main__":
    unittest.main()
