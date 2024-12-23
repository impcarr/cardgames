from random import random, choices
from typing import List, Optional
from numpy import exp
from collections import Counter
from itertools import combinations
from auction_card import AuctionCardHand


class Player:
    def __init__(self, name: str, custom_funds: Optional[List[int]] = None):
        self.name = name
        # Standard money cards in the game
        if custom_funds is None:
            self.funds = [
                1000,
                2000,
                3000,
                4000,
                6000,
                8000,
                10000,
                12000,
                15000,
                20000,
                25000,
            ]
        else:
            self.funds = custom_funds
        self.cards_won = AuctionCardHand()
        self.bid: List[int] = []

    def get_total_money(self) -> int:
        """Get the total value of all money cards the player has remaining."""
        return sum(self.funds)

    def get_total_score(self) -> float:
        """Get the total value of the player's auction cards."""
        return self.cards_won.get_score()

    def can_afford(self, max_bid: int) -> bool:
        """Check if the player can afford a given bid."""
        return max_bid <= self.get_total_money()

    def get_bid(self) -> List[int]:
        """Get the current bid."""
        return self.bid

    def set_bid(self, bid: List[int]) -> None:
        """Set the current bid."""
        if not self.bid_is_valid(bid):
            raise ValueError("Invalid bid: player does not have requisite cards")
        else:
            self.bid = bid

    def pass_bid(self) -> None:
        """Pass on the current bid."""
        self.set_bid([-1])

    def bid_is_valid(
        self, bid: list[int], current_highest_bid: Optional[list[int]] = None
    ) -> bool:
        """Check if a bid is valid given the current highest bid."""
        if (
            current_highest_bid is None
        ):  # Use None as default instead of [] to avoid mutable default argument errors
            current_highest_bid = []
        if bid == [-1]:
            return True  # Passing is always valid
        if sum(bid) <= sum(current_highest_bid):
            return False
        available_fund_counts = Counter(self.funds)
        bid_counts = Counter(bid)
        for denomination, count in bid_counts.items():
            if available_fund_counts[denomination] < count:
                return False
        return True

    def bid_or_pass_randomly(self, current_bid: List[int]) -> List[int]:
        """Randomly pass or return a valid bid based on the current bid."""
        current_bid_sum = sum(current_bid)
        if current_bid_sum >= self.get_total_money():
            self.pass_bid()
        else:
            if random() < 0.33:
                self.pass_bid()
            else:
                self.bid = self.get_random_valid_bid(current_bid)
        return self.get_bid()

    def get_random_valid_bid(self, current_bid: List[int] = []) -> List[int]:
        """Uses a nice exponential decay function to chose a bid from the list of valid bids.
        Weights the lower bids more heavily."""
        valid_bids = self.get_valid_bids(current_bid)
        weights = [exp(-0.5 * i) for i in range(len(valid_bids))]
        total = sum(weights)
        weights = [w / total for w in weights]
        return choices(valid_bids, weights=weights, k=1)[0]

    def get_valid_bids(self, current_bid: List[int]) -> List[List[int]]:
        """Get all valid bids given the current highest"""
        valid_bids = []
        current_bid_sum = sum(current_bid)

        for length in range(1, len(self.funds) + 1):
            for combo in combinations(self.funds, length):
                if sum(combo) > current_bid_sum:
                    valid_bids.append(list(combo))

        return sorted(valid_bids, key=sum)

    def reset_bid(self) -> None:
        """Reset the current bid to empty."""
        self.bid = []

    def spend_bid(self) -> None:
        """Remove current bid from funds and reset current bid to empty."""
        for card in self.bid:
            self.funds.remove(card)
        self.reset_bid()
