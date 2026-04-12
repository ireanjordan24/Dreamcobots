"""
DreamCo Event Bus — Abstract Base

Defines the contract that every event bus implementation must fulfil.
"""

from __future__ import annotations

import abc
from typing import Any, Callable


class BaseEventBus(abc.ABC):
    """
    Abstract event bus contract.

    All concrete event bus implementations (in-process, Redis, HTTP, etc.)
    must extend this class and implement :meth:`publish` and
    :meth:`subscribe`.
    """

    @abc.abstractmethod
    def publish(self, event_type: str, data: Any) -> None:
        """
        Emit *event_type* with *data* to all subscribers.

        Parameters
        ----------
        event_type : str
            The event category (e.g. ``"deal_found"``).
        data : Any
            Arbitrary payload passed to each subscriber.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Register *handler* to be called when *event_type* is published.

        Parameters
        ----------
        event_type : str
            The event category to listen for.
        handler : Callable
            Function invoked with the event data as its sole argument.
        """
        raise NotImplementedError
