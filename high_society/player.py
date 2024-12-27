from random import random, choices
from typing import List, Optional
from numpy import exp
from collections import Counter
from itertools import combinations
from auction_card import AuctionCardHand, AuctionCard


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

    def __repr__(self) -> str:
        return self.name

    def get_name(self) -> str:
        """Get the player's name."""
        return self.name

    def get_funds(self) -> List[int]:
        """Get the player's money cards."""
        return self.funds

    def get_cards_won(self) -> AuctionCardHand:
        """Get the player's auction cards."""
        return self.cards_won

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

    def raise_bid(self, raise_amount: List[int]) -> None:
        raised_bid = self.get_bid() + raise_amount
        if not self.bid_is_valid(raised_bid):
            raise ValueError(f"Invalid bid: player does not have requisite cards. Has {self.get_funds()} available, previously bid {self.get_bid()}, and is trying to raise by {raise_amount} for a total raised bid of {raised_bid}")
        else:
            self.set_bid(raised_bid)

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

    def bid_or_pass_randomly(self, current_highest_bid: List[int]) -> List[int]:
        """Randomly pass or return a valid bid based on the current bid."""
        if self.get_bid() == [-1]:
            return self.get_bid()
        current_highest_bid_sum = sum(current_highest_bid)
        if current_highest_bid_sum >= self.get_total_money():
            self.pass_bid()
        else:
            if random() < 0.33:
                self.pass_bid()
            else:
                self.raise_bid(self.get_random_valid_raise(current_highest_bid))
        return self.get_bid()

    def get_random_valid_raise(self, current_highest_bid: List[int] = []) -> List[int]:
        """Uses a nice exponential decay function to choose a bid from the list of valid bids.
        Weights the lower bids more heavily."""
        valid_bids = self.get_valid_bids(current_highest_bid)
        weights = [exp(-0.5 * i) for i in range(len(valid_bids))]
        total = sum(weights)
        weights = [w / total for w in weights]
        return choices(valid_bids, weights=weights, k=1)[0]

    def get_available_raises(self) -> List[int]:
        funds_to_raise = [fund for fund in self.get_funds()] # Can't just do a simple 'if fund not in self.get_bid()' because 
        for fund in self.get_bid():                          # we only want to remove single copies
            try:
                funds_to_raise.remove(fund)
            except ValueError:
                print(f"Tried to remove {fund} from {funds_to_raise} and failed.")
        return funds_to_raise

    def get_valid_bids(self, current_highest_bid: List[int]) -> List[List[int]]:
        """Get all valid bids given the current highest bid and the player's current bid."""
        valid_bids = []
        current_highest_bid_sum = sum(current_highest_bid)
        most_recent_bid_sum = sum(self.get_bid())
        raise_minimum = current_highest_bid_sum - most_recent_bid_sum

        funds_available = self.get_available_raises()

        for length in range(1, len(funds_available) + 1):
            for combo in combinations(funds_available, length):
                if sum(combo) > raise_minimum:
                    valid_bids.append(list(combo))

        return sorted(valid_bids, key=sum)

    def reset_bid(self) -> None:
        """Reset the current bid to empty."""
        self.bid = []

    def spend_bid(self) -> None:
        """Remove current bid from funds and reset current bid to empty."""
        for card in self.get_bid():
            self.funds.remove(card)
        self.reset_bid()

    def win_card(self, card: AuctionCard) -> None:
        """Add a card to the player's collection."""
        self.cards_won.win_card(card)
