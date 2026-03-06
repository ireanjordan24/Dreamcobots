"""
core/config_loader.py

Loads JSON configuration files with support for environment-variable overrides
and basic schema validation.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any


def _get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


class ConfigValidationError(Exception):
    """Raised when a loaded configuration fails validation."""


class ConfigLoader:
    """
    Loads JSON configuration files and merges environment-variable overrides.

    Environment variables of the form ``DREAMCOBOTS_<KEY>`` (upper-cased)
    override the matching top-level key from the JSON file.

    Example::

        loader = ConfigLoader()
        config = loader.load("bots/config.json")
    """

    ENV_PREFIX: str = "DREAMCOBOTS_"

    def __init__(self, required_keys: list[str] | None = None) -> None:
        """
        Initialise the ConfigLoader.

        Args:
            required_keys: Optional list of top-level keys that *must* be
                           present after loading. A :class:`ConfigValidationError`
                           is raised if any are missing.
        """
        self.required_keys: list[str] = required_keys or []
        self.logger: logging.Logger = _get_logger("ConfigLoader")

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self, config_path: str) -> dict[str, Any]:
        """
        Load a JSON configuration file and apply environment-variable overrides.

        Args:
            config_path: Path to the JSON configuration file.

        Returns:
            The merged configuration dict.

        Raises:
            FileNotFoundError: If *config_path* does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            ConfigValidationError: If required keys are missing.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        self.logger.info("Loading config: %s", config_path)
        with path.open("r", encoding="utf-8") as fh:
            config: dict[str, Any] = json.load(fh)

        config = self._apply_env_overrides(config)
        self.validate(config)

        self.logger.info(
            "Config loaded successfully from %s (%d keys).",
            config_path,
            len(config),
        )
        return config

    def load_from_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Accept a pre-built dict, apply env overrides, and validate.

        Args:
            data: A dict to use as the base configuration.

        Returns:
            The merged, validated configuration dict.
        """
        config = self._apply_env_overrides(dict(data))
        self.validate(config)
        return config

    # ------------------------------------------------------------------
    # Environment-variable overrides
    # ------------------------------------------------------------------

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Scan the environment for ``DREAMCOBOTS_<KEY>`` variables and apply
        them as overrides to *config*.

        Args:
            config: The base configuration dict.

        Returns:
            The config dict with overrides applied.
        """
        for env_key, env_val in os.environ.items():
            if env_key.startswith(self.ENV_PREFIX):
                config_key = env_key[len(self.ENV_PREFIX) :].lower()
                self.logger.debug(
                    "Applying env override: %s -> %s=%r",
                    env_key,
                    config_key,
                    env_val,
                )
                config[config_key] = env_val
        return config

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, config: dict[str, Any]) -> None:
        """
        Validate that all required keys are present in *config*.

        Args:
            config: The configuration dict to validate.

        Raises:
            ConfigValidationError: If any required key is missing.
        """
        missing = [k for k in self.required_keys if k not in config]
        if missing:
            raise ConfigValidationError(
                f"Missing required config keys: {missing}"
            )
        self.logger.debug("Config validation passed.")

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get(
        self, config: dict[str, Any], key: str, default: Any = None
    ) -> Any:
        """
        Safely retrieve a value from a config dict.

        Args:
            config: The configuration dict.
            key: The key to retrieve.
            default: Value to return if *key* is absent.

        Returns:
            The value associated with *key*, or *default*.
        """
        return config.get(key, default)
