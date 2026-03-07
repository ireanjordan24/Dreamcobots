"""
BuddyAI — Buddy Bot

Orchestrator bot that registers, routes messages to, and broadcasts across
all DreamCo ecosystem bots.  Any bot that exposes a ``chat(message)`` method
can be registered.
"""

from BuddyAI.event_bus import EventBus


class BuddyBot:
    """
    Central orchestrator for the DreamCo bot ecosystem.

    Registered bots must expose a ``chat(message: str) -> dict`` method.
    BuddyBot routes messages to individual bots or broadcasts to all of them.

    Attributes
    ----------
    event_bus : EventBus
        Shared event bus for inter-bot communication.
    """

    def __init__(self) -> None:
        self.event_bus: EventBus = EventBus()
        self._bots: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Bot registry
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot_instance: object) -> None:
        """
        Register a bot under *name*.

        Parameters
        ----------
        name : str
            Unique identifier for the bot (e.g. 'dreamco_payments').
        bot_instance : object
            Bot instance exposing a ``chat()`` method.
        """
        self._bots[name] = bot_instance
        self.event_bus.publish("bot_registered", {"name": name})

    def unregister_bot(self, name: str) -> None:
        """
        Remove a previously registered bot.

        Parameters
        ----------
        name : str
            Name of the bot to remove.
        """
        if name in self._bots:
            del self._bots[name]
            self.event_bus.publish("bot_unregistered", {"name": name})

    def list_bots(self) -> list:
        """
        Return the names of all registered bots.

        Returns
        -------
        list[str]
            Sorted list of registered bot names.
        """
        return sorted(self._bots.keys())

    # ------------------------------------------------------------------
    # Message routing
    # ------------------------------------------------------------------

    def route_message(self, bot_name: str, message: str) -> dict:
        """
        Route *message* to a specific registered bot.

        Parameters
        ----------
        bot_name : str
            Target bot name.
        message : str
            Message to send.

        Returns
        -------
        dict
            Response from the target bot's ``chat()`` method.

        Raises
        ------
        KeyError
            If *bot_name* is not registered.
        AttributeError
            If the registered bot does not expose a ``chat()`` method.
        """
        if bot_name not in self._bots:
            raise KeyError(f"Bot '{bot_name}' is not registered.")

        bot = self._bots[bot_name]
        if not callable(getattr(bot, "chat", None)):
            raise AttributeError(
                f"Bot '{bot_name}' does not expose a chat() method."
            )

        response = bot.chat(message)
        self.event_bus.publish(
            "message_routed", {"bot_name": bot_name, "message": message}
        )
        return response

    def broadcast(self, message: str) -> dict:
        """
        Send *message* to all registered bots that expose ``chat()``.

        Parameters
        ----------
        message : str
            Message to broadcast.

        Returns
        -------
        dict
            Mapping of bot_name -> response dict from each bot's ``chat()``.
        """
        results: dict[str, dict] = {}
        for name, bot in self._bots.items():
            if callable(getattr(bot, "chat", None)):
                results[name] = bot.chat(message)

        self.event_bus.publish("broadcast_sent", {"message": message})
        return results
