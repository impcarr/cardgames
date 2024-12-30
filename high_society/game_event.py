from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Protocol
from auction_card import AuctionCard


class GameEventType(Enum):
    AUCTION_STARTED = auto()
    PLAYER_BID = auto()
    PLAYER_PASSED = auto()
    AUCTION_WON = auto()
    CARD_DRAWN = auto()
    GAME_ENDED = auto()
    PLAYER_FUNDS_UPDATED = auto()
    CARD_ADDED_TO_HAND = auto()
    CARD_REMOVED_FROM_HAND = auto()


@dataclass
class GameEvent:
    """Represents a game event with its type and associated data."""

    type: GameEventType
    data: Dict[str, Any]


class EventHandler(Protocol):
    """Protocol defining what an event handler should look like."""

    def handle_event(self, event: GameEvent) -> None: ...


class ConsoleEventHandler:
    """Default event handler that prints events to console."""

    def handle_event(self, event: GameEvent) -> None:
        if event.type == GameEventType.AUCTION_STARTED:
            card: AuctionCard = event.data["card"]
            print(f"\nStarting auction for: {card.name} ({card.type})")
            print(
                f"This card {'makes' if card.is_end_game() else 'does not make'} progress towards ending the game."
            )

        elif event.type == GameEventType.PLAYER_BID:
            print(f"{event.data['player'].name} bids {event.data['bid']}")

        elif event.type == GameEventType.PLAYER_PASSED:
            print(f"{event.data['player'].name} passes")

        elif event.type == GameEventType.AUCTION_WON:
            print(f"{event.data['player'].name} wins {event.data['card'].name}")

        elif event.type == GameEventType.PLAYER_FUNDS_UPDATED:
            print(f"{event.data['player'].name} has {event.data['funds']} remaining")

        elif event.type == GameEventType.CARD_ADDED_TO_HAND:
            print(
                f"{event.data['player'].name} adds {event.data['card'].name} to their hand"
            )
        elif event.type == GameEventType.GAME_ENDED:
            print(
                f"{event.data['player'].name} has won with a score of {event.data['score']}"
            )
