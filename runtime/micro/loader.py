"""Plugin loader for micro runtime.

Provides PluginLoader that dynamically discovers and loads .py plugin files
from a plugins directory. Each plugin can expose:
  - get_tools(): returns list of tool definitions
  - get_constraints(): returns list of constraint functions

Usage::

    loader = PluginLoader(plugins_dir="plugins/")
    loader.discover()
    tools = loader.discover_tools()
    constraints = loader.discover_constraints()
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# PluginLoader
# ---------------------------------------------------------------------------


class PluginLoader:
    """Dynamically discovers and loads .py plugin files from a directory.

    Scans the plugins_dir for Python files (skipping those prefixed with ``_``),
    loads each module via importlib, and collects tools and constraints from
    modules that expose the required interfaces.

    Usage::

        loader = PluginLoader(plugins_dir="plugins/")
        loaded = loader.discover()   # loads all non-underscore .py files
        tools = loader.discover_tools()        # collect get_tools() results
        constraints = loader.discover_constraints()  # collect get_constraints() results
    """

    def __init__(self, plugins_dir: str = "plugins") -> None:
        """Initialize PluginLoader.

        Args:
            plugins_dir: Path to the directory containing plugin .py files.
        """
        self.plugins_dir = plugins_dir
        self._loaded_modules: list[Any] = []

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self) -> list[Any]:
        """Scan plugins_dir for .py files and load each via importlib.

        Files prefixed with ``_`` (like ``__init__.py``, ``_private.py``)
        are skipped.

        Uses ``Path.iterdir()`` to scan the directory for ``.py`` files.

        Returns:
            List of loaded module objects.
        """
        self._loaded_modules = []
        plugins_path = Path(self.plugins_dir)

        if not plugins_path.is_dir():
            return []

        # Use Path.iterdir() to scan directory for .py files
        for entry in sorted(plugins_path.iterdir()):
            if not entry.is_file():
                continue
            if entry.suffix != ".py":
                continue
            if entry.name.startswith("_"):
                continue  # skip _private.py, __init__.py, etc.

            module = self._load_module(entry)
            if module is not None:
                self._loaded_modules.append(module)

        return self._loaded_modules

    def _load_module(self, path: Path) -> Any | None:
        """Load a single Python file as a module via importlib.

        Uses ``importlib.util.spec_from_file_location`` to load the module
        without requiring it to be on sys.path.

        Args:
            path: Path to the .py file to load.

        Returns:
            Loaded module object, or None if loading fails.
        """
        module_name = f"micro_plugin_{path.stem}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            return module
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Interface collection
    # ------------------------------------------------------------------

    def discover_tools(self) -> list[Any]:
        """Collect tool definitions from all loaded plugin modules.

        Calls ``get_tools()`` on each loaded module that exposes it.
        Results are flattened into a single list.

        Returns:
            Combined list of tool definitions from all plugins.
        """
        tools: list[Any] = []
        for module in self._loaded_modules:
            if hasattr(module, "get_tools"):
                try:
                    module_tools = module.get_tools()
                    if isinstance(module_tools, list):
                        tools.extend(module_tools)
                except Exception:
                    pass
        return tools

    def discover_constraints(self) -> list[Any]:
        """Collect constraint definitions from all loaded plugin modules.

        Calls ``get_constraints()`` on each loaded module that exposes it.
        Results are flattened into a single list.

        Returns:
            Combined list of constraint functions/objects from all plugins.
        """
        constraints: list[Any] = []
        for module in self._loaded_modules:
            if hasattr(module, "get_constraints"):
                try:
                    module_constraints = module.get_constraints()
                    if isinstance(module_constraints, list):
                        constraints.extend(module_constraints)
                except Exception:
                    pass
        return constraints
