"""Multi-provider support for nano runtime.

Provides ProviderManager class for configuring and switching between LLM
providers at runtime. Reads provider configuration from config dict and
supports runtime provider selection.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# ProviderManager
# ---------------------------------------------------------------------------


class ProviderManager:
    """Multi-provider configuration and runtime switching for nano agents.

    Reads a ``providers`` list from the config dict, where each entry has::

        name: "anthropic"
        model: "anthropic/claude-sonnet-4-20250514"
        api_key_env: "ANTHROPIC_API_KEY"

    Falls back to a single provider derived from the top-level ``model`` key
    if no ``providers`` list is present.

    Supports runtime provider switching via ``select_provider()`` and
    ``set_provider()``.

    Usage::

        manager = ProviderManager(config)
        model = manager.get_model()
        api_key = manager.get_api_key()
        manager.select_provider("openai")
        names = manager.list_providers()
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialise the ProviderManager from a config dict.

        Args:
            config: Config dict. May contain a ``providers`` list with
                ``name/model/api_key_env`` dicts, or a top-level ``model``
                key for single-provider fallback.
        """
        self._config = config
        self._providers: list[dict[str, Any]] = []
        self._current_index: int = 0

        # Load providers list from config, or fall back to single provider
        raw_providers = config.get("providers")
        if isinstance(raw_providers, list) and raw_providers:
            for entry in raw_providers:
                if isinstance(entry, dict) and "name" in entry:
                    self._providers.append(
                        {
                            "name": str(entry.get("name", "")),
                            "model": str(
                                entry.get(
                                    "model",
                                    config.get(
                                        "model", "anthropic/claude-sonnet-4-20250514"
                                    ),
                                )
                            ),
                            "api_key_env": str(entry.get("api_key_env", "")),
                        }
                    )
        else:
            # Single-provider fallback from top-level model key
            model = str(config.get("model", "anthropic/claude-sonnet-4-20250514"))
            # Infer provider name from model prefix (e.g. "anthropic/..." -> "anthropic")
            name = model.split("/")[0] if "/" in model else "default"
            self._providers.append(
                {
                    "name": name,
                    "model": model,
                    "api_key_env": "",
                }
            )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def current_provider(self) -> dict[str, Any]:
        """Return the currently selected provider dict.

        Returns:
            Dict with ``name``, ``model``, ``api_key_env`` keys.
        """
        return self._providers[self._current_index]

    def get_model(self) -> str:
        """Return the model string for the current provider.

        Returns:
            litellm-compatible model string.
        """
        return self.current_provider()["model"]

    def get_api_key(self) -> str | None:
        """Return the API key for the current provider from the environment.

        Reads the value of the ``api_key_env`` environment variable name
        from the OS environment.

        Returns:
            API key string if the env var is set; ``None`` otherwise.
        """
        import os

        api_key_env = self.current_provider().get("api_key_env", "")
        if not api_key_env:
            return None
        return os.environ.get(api_key_env)

    def list_providers(self) -> list[str]:
        """Return a list of all configured provider names.

        Returns:
            List of provider name strings.
        """
        return [p["name"] for p in self._providers]

    # ------------------------------------------------------------------
    # Provider switching
    # ------------------------------------------------------------------

    def select_provider(self, name: str) -> None:
        """Switch the active provider by name.

        Args:
            name: Provider name to select.

        Raises:
            ValueError: If no provider with that name exists.
        """
        for i, provider in enumerate(self._providers):
            if provider["name"] == name:
                self._current_index = i
                return
        available = ", ".join(self.list_providers())
        raise ValueError(
            f"Provider {name!r} not found. Available providers: {available}"
        )

    def set_provider(self, name: str) -> None:
        """Alias for ``select_provider()`` — switch active provider by name.

        Args:
            name: Provider name to activate.

        Raises:
            ValueError: If no provider with that name exists.
        """
        self.select_provider(name)
