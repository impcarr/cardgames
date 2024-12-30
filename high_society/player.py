from random import random, choices
from typing import List, Optional
from numpy import exp
from collections import Counter
from itertools import combinations
from auction_card import AuctionCardHand, AuctionCard


class Player:
    def __init__(self, name: str, custom_funds: Optional[List[int]] = None):
        self._name = name
        # Standard money cards in the game
        if custom_funds is None:
            self._funds = [
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
            self._funds = custom_funds
        self._cards_won = AuctionCardHand()
        self._bid: List[int] = []

    def __repr__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        """Get the player's name."""
        return self._name

    @property
    def funds(self) -> List[int]:
        """Get the player's money cards."""
        return self._funds

    @property
    def total_money(self) -> int:
        """Get the total value of all money cards the player has remaining."""
        return sum(self._funds)

    @property
    def bid(self) -> List[int]:
        """Get the current bid."""
        return self._bid

    @bid.setter
    def bid(self, bid: List[int]) -> None:
        """Set the current bid."""
        if not self.bid_is_valid(bid):
            raise ValueError("Invalid bid: player does not have requisite cards")
        else:
            self._bid = bid

    def can_afford(self, max_bid: int) -> bool:
        """Check if the player can afford a given bid."""
        return max_bid <= self.total_money

    def reset_bid(self) -> None:
        """Reset the current bid to empty."""
        self._bid = []

    def pass_bid(self) -> None:
        """Pass on the current bid."""
        self.bid = [-1]

    def raise_bid(self, raise_amount: List[int]) -> None:
        """Raises the players bid by the amount specified."""
        raised_bid = self.bid + raise_amount
        if not self.bid_is_valid(raised_bid):
            raise ValueError(
                f"Invalid bid: player does not have requisite cards. Has {self.funds} available, previously bid {self.bid}, and is trying to raise by {raise_amount} for a total raised bid of {raised_bid}"
            )
        else:
            self.bid = raised_bid

    def spend_bid(self) -> None:
        """Remove current bid from funds and reset current bid to empty."""
        for card in self.bid:
            self._funds.remove(card)
        self.reset_bid()

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
        available_fund_counts = Counter(self._funds)
        bid_counts = Counter(bid)
        for denomination, count in bid_counts.items():
            if available_fund_counts[denomination] < count:
                return False
        return True

    def bid_or_pass(self, current_highest_bid: List[int]) -> List[int]:
        self.pass_bid()
        return self.bid

    def get_available_raises(self) -> List[int]:
        fund_counter = Counter(self.funds)
        bid_counter = Counter(self.bid)
        return list((fund_counter - bid_counter).elements())

    def get_valid_bids(self, current_highest_bid: List[int]) -> List[List[int]]:
        """Get all valid bids given the current highest bid and the player's current bid."""
        valid_bids = []
        current_highest_bid_sum = sum(current_highest_bid)
        most_recent_bid_sum = sum(self.bid)
        raise_minimum = current_highest_bid_sum - most_recent_bid_sum

        funds_available = self.get_available_raises()

        for length in range(1, len(funds_available) + 1):
            for combo in combinations(funds_available, length):
                if sum(combo) > raise_minimum:
                    valid_bids.append(list(combo))

        return sorted(valid_bids, key=sum)

    @property
    def cards_won(self) -> AuctionCardHand:
        """Get the player's auction cards."""
        return self._cards_won

    def win_card(self, card: AuctionCard) -> None:
        """Add a card to the player's collection."""
        self._cards_won.win_card(card)

    def get_total_score(self) -> float:
        """Get the total value of the player's auction cards."""
        return self._cards_won.get_score()
    

class RandomPlayer(Player):

    def __init__(self, name: str, custom_funds: Optional[List[int]] = None):
        super().__init__(name, custom_funds)

    def bid_or_pass(self, current_highest_bid: List[int]) -> List[int]:
        return self.bid_or_pass_randomly(current_highest_bid)

    def bid_or_pass_randomly(self, current_highest_bid: List[int]) -> List[int]:
        """Randomly pass or return a valid bid based on the current bid."""
        if self.bid == [-1]:
            return self.bid
        current_highest_bid_sum = sum(current_highest_bid)
        if current_highest_bid_sum >= self.total_money:
            self.pass_bid()
        else:
            if random() < 0.33:
                self.pass_bid()
            else:
                self.raise_bid(self.get_random_valid_raise(current_highest_bid))
        return self.bid

    def get_random_valid_raise(self, current_highest_bid: List[int] = []) -> List[int]:
        """Uses a nice exponential decay function to choose a bid from the list of valid bids.
        Weights the lower bids more heavily."""
        valid_bids = self.get_valid_bids(current_highest_bid)
        weights = [exp(-0.5 * i) for i in range(len(valid_bids))]
        total = sum(weights)
        weights = [w / total for w in weights]
        return choices(valid_bids, weights=weights, k=1)[0]