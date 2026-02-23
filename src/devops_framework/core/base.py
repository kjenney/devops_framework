"""Abstract base client for all integrations."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from devops_framework.core.config import Config
from devops_framework.core.logging import get_logger


class IntegrationBaseClient(ABC):
    """
    Abstract root for all integration clients.

    Subclasses receive a shared :class:`Config` instance and a logger.
    """

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()
        self._logger: logging.Logger = get_logger(self.__class__.__module__)

    @property
    def config(self) -> Config:
        return self._config

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the integration is reachable and authenticated."""
