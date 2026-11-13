"""Test registration with API doubles; does not run a Home Assistant server."""

import ast
import asyncio
from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
import importlib.util
import json
from pathlib import Path
import selectors
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components/pogoda_by"


@dataclass
class StaticPathConfig:
    url_path: str
    path: str
    cache_headers: bool


class ResourceStorageCollection:
    """Match HA's input res_type / output type resource contract."""

    def __init__(self, items=(), *, loaded=False):
        self.loaded = loaded
        self.disk = deepcopy(list(items))
        self.items = deepcopy(list(items)) if loaded else []
        self.operations = []
        self.load_error = None

    async def async_load(self):
        self.operations.append(("load",))
        await asyncio.sleep(0)
        if self.load_error:
            raise self.load_error
        self.items = deepcopy(self.disk)
        self.loaded = True

    def async_items(self):
        if not self.loaded:
            raise AssertionError("Must load disk resources before access")
        return self.items

    async def async_create_item(self, data):
        assert self.loaded
        self.operations.append(("create", deepcopy(data)))
        self.items.append({"id": f"new-{len(self.items)}", "url": data["url"], "type": data["res_type"]})
        await asyncio.sleep(0)

    async def async_update_item(self, item_id, data):
        self.operations.append(("update", item_id, deepcopy(data)))
        item = next(item for item in self.items if item["id"] == item_id)
        item.update(url=data["url"], type=data["res_type"])
        await asyncio.sleep(0)

    async def async_delete_item(self, item_id):
        self.operations.append(("delete", item_id))
        self.items = [item for item in self.items if item["id"] != item_id]
        await asyncio.sleep(0)


def load_dashboard():
    modules = {name: ModuleType(name) for name in (
        "homeassistant", "homeassistant.components", "homeassistant.components.http",
        "homeassistant.components.lovelace", "homeassistant.components.lovelace.resources",
        "homeassistant.core",
    )}
    modules["homeassistant.components.http"].StaticPathConfig = StaticPathConfig
    modules["homeassistant.components.lovelace.resources"].ResourceStorageCollection = ResourceStorageCollection
    modules["homeassistant.core"].HomeAssistant = SimpleNamespace
    package = ModuleType("_test_dashboard_pogoda")
    package.__path__ = [str(COMPONENT)]
    modules[package.__name__] = package
    name = f"{package.__name__}.dashboard"
    spec = importlib.util.spec_from_file_location(name, COMPONENT / "dashboard.py")
    module = importlib.util.module_from_spec(spec)
    modules[name] = module
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


dashboard = load_dashboard()


def make_hass(resources):
    return SimpleNamespace(
        data={"lovelace": SimpleNamespace(resources=resources)},
        http=SimpleNamespace(async_register_static_paths=AsyncMock()),
    )


class _NoIOSelector(selectors.SelectSelector):
    def select(self, timeout=None):
        return []


class _LogicLoop(asyncio.SelectorEventLoop):
    """Schedule real tasks/futures without Windows socketpair initialization.

    These API doubles only yield with sleep(0); no test performs socket I/O.
    """

    def __init__(self):
        super().__init__(selector=_NoIOSelector())

    def _make_self_pipe(self):
        self._ssock = self._csock = None

    def _close_self_pipe(self):
        pass


def async_test(func):
    @wraps(func)
    def run(self):
        with asyncio.Runner(loop_factory=_LogicLoop) as runner:
            runner.run(func(self))
    return run


class RegistrationTests(unittest.TestCase):
    @async_test
    async def test_load_before_write_preserves_unrelated_resources(self):
        original = {"id": "other", "url": "/local/other-card.js", "type": "module"}
        resources = ResourceStorageCollection([original])
        hass = make_hass(resources)
        await dashboard.async_setup_card(hass)
        self.assertEqual(resources.operations[0], ("load",))
        self.assertEqual(resources.items[0], original)
        self.assertEqual(resources.items[1]["url"], dashboard.CARD_URL)
        path = hass.http.async_register_static_paths.call_args.args[0][0]
        self.assertEqual(path.url_path, dashboard.CARD_BASE_URL)
        self.assertTrue(Path(path.path).is_file())
        self.assertFalse(path.cache_headers)

    @async_test
    async def test_repeat_registration_changes_nothing(self):
        resources = ResourceStorageCollection()
        hass = make_hass(resources)
        await dashboard.async_setup_card(hass)
        operations = list(resources.operations)
        await dashboard.async_setup_card(hass)
        self.assertEqual(resources.operations, operations)
        hass.http.async_register_static_paths.assert_awaited_once()

    @async_test
    async def test_concurrent_stations_do_not_create_duplicates(self):
        resources = ResourceStorageCollection()
        hass = make_hass(resources)
        await asyncio.gather(*(dashboard.async_setup_card(hass) for _ in range(8)))
        self.assertEqual(len(resources.items), 1)
        self.assertEqual(sum(op[0] == "create" for op in resources.operations), 1)
        hass.http.async_register_static_paths.assert_awaited_once()

    @async_test
    async def test_update_existing_canonical_resource_keeps_id(self):
        resources = ResourceStorageCollection([
            {"id": "card", "url": dashboard.CARD_BASE_URL + "?v=old", "type": "module"}
        ])
        await dashboard.async_setup_card(make_hass(resources))
        self.assertEqual(resources.items, [{"id": "card", "url": dashboard.CARD_URL, "type": "module"}])
        self.assertFalse(any(op[0] == "create" for op in resources.operations))

    @async_test
    async def test_migrate_previous_manual_install(self):
        resources = ResourceStorageCollection([
            {"id": "manual", "url": "/local/pogoda-by-card.js?v=0.1.0", "type": "module"}
        ])
        await dashboard.async_setup_card(make_hass(resources))
        self.assertEqual(resources.items[0]["id"], "manual")
        self.assertEqual(resources.items[0]["url"], dashboard.CARD_URL)

    @async_test
    async def test_deduplicate_only_our_local_resources(self):
        other = [
            {"id": "external", "url": "https://example.org/local/pogoda-by-card.js", "type": "module"},
            {"id": "network", "url": "//example.org/pogoda_by/pogoda-by-card.js", "type": "module"},
            {"id": "custom", "url": "/local/my/pogoda-by-card.js", "type": "module"},
        ]
        resources = ResourceStorageCollection([
            {"id": "manual", "url": dashboard.LEGACY_CARD_URL, "type": "module"},
            {"id": "canonical", "url": dashboard.CARD_BASE_URL, "type": "module"},
            {"id": "duplicate", "url": dashboard.CARD_BASE_URL + "?v=old", "type": "module"},
            *other,
        ])
        await dashboard.async_setup_card(make_hass(resources))
        self.assertEqual(resources.items, [
            {"id": "canonical", "url": dashboard.CARD_URL, "type": "module"}, *other,
        ])

    @async_test
    async def test_correct_url_with_wrong_type_is_fixed(self):
        resources = ResourceStorageCollection([
            {"id": "card", "url": dashboard.CARD_URL, "type": "css"}
        ])
        await dashboard.async_setup_card(make_hass(resources))
        self.assertEqual(resources.items[0]["type"], "module")

    @async_test
    async def test_already_loaded_resources_are_not_reloaded(self):
        resources = ResourceStorageCollection(loaded=True)
        resources.items.append({"id": "new", "url": "/local/unsaved.js", "type": "module"})
        await dashboard.async_setup_card(make_hass(resources))
        self.assertFalse(any(op[0] == "load" for op in resources.operations))
        self.assertEqual(resources.items[0]["id"], "new")

    @async_test
    async def test_yaml_is_untouched_but_file_is_served(self):
        resources = SimpleNamespace(async_items=Mock(side_effect=AssertionError("YAML is read-only")))
        hass = make_hass(resources)
        with self.assertLogs(dashboard.__name__, level="WARNING") as logs:
            await dashboard.async_setup_card(hass)
        self.assertIn(dashboard.CARD_URL, logs.output[0])
        resources.async_items.assert_not_called()
        hass.http.async_register_static_paths.assert_awaited_once()

    @async_test
    async def test_old_lovelace_dict_is_supported(self):
        resources = ResourceStorageCollection()
        hass = make_hass(resources)
        hass.data["lovelace"] = {"resources": resources}
        await dashboard.async_setup_card(hass)
        self.assertEqual(resources.items[0]["url"], dashboard.CARD_URL)

    @async_test
    async def test_failed_disk_load_never_creates_a_resource(self):
        resources = ResourceStorageCollection([{"id": "other", "url": "/local/other.js", "type": "module"}])
        resources.load_error = OSError("storage unavailable")
        hass = make_hass(resources)
        with self.assertRaises(OSError):
            await dashboard.async_setup_card(hass)
        self.assertEqual(resources.operations, [("load",)])
        resources.load_error = None
        await dashboard.async_setup_card(hass)
        self.assertEqual(resources.items[0]["id"], "other")
        hass.http.async_register_static_paths.assert_awaited_once()

    @async_test
    async def test_failed_static_registration_can_retry(self):
        resources = ResourceStorageCollection()
        hass = make_hass(resources)
        hass.http.async_register_static_paths.side_effect = OSError("static unavailable")
        with self.assertRaises(OSError):
            await dashboard.async_setup_card(hass)
        self.assertEqual(resources.operations, [])
        hass.http.async_register_static_paths.side_effect = None
        await dashboard.async_setup_card(hass)
        self.assertEqual(len(resources.items), 1)

    @async_test
    async def test_frontend_failure_does_not_fail_component_setup(self):
        # Execute the actual setup hook without importing HA's networking stack.
        source = ast.parse((COMPONENT / "__init__.py").read_text(encoding="utf-8"))
        hook = next(node for node in source.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_setup")
        register = AsyncMock(side_effect=OSError("storage unavailable"))
        logger = Mock()
        namespace = {"HomeAssistant": SimpleNamespace, "ConfigType": dict, "async_setup_card": register, "_LOGGER": logger}
        exec(compile(ast.Module(body=[hook], type_ignores=[]), "setup_hook", "exec"), namespace)
        hass = SimpleNamespace()
        self.assertTrue(await namespace["async_setup"](hass, {}))
        register.assert_awaited_once_with(hass)
        logger.exception.assert_called_once()


class PackageTests(unittest.TestCase):
    def test_version_dependencies_and_card_are_bundled(self):
        manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(dashboard.VERSION, manifest["version"])
        self.assertTrue({"http", "frontend", "lovelace"}.issubset(manifest["dependencies"]))
        self.assertEqual(dashboard.CARD_PATH.parent, COMPONENT / "frontend")
        self.assertIn("pogoda-by-card", dashboard.CARD_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
