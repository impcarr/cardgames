from typing import List, Optional
from random import shuffle
from player import Player
from auction_card import AuctionCardDeck, AuctionCard

DEFAULT_GAME_LENGTH = 4


class HighSociety:
    def __init__(self, player_names: List[str]):
        self.players = [Player(name) for name in player_names]
        shuffle(self.players)
        self.deck = AuctionCardDeck()
        self.game_progress = 0
        self.current_card: AuctionCard
        self.passed_players: set[Player] = set()
        self.current_bid: List[int] = [0]
        self.scores: dict[Player, float] = {}

    def get_players(self) -> List[Player]:
        """Get the list of players"""
        return self.players

    def set_auction_card(self, card: AuctionCard) -> None:
        """Set the current auction card"""
        self.current_card = card

    def get_auction_card(self) -> AuctionCard:
        """Get the current auction card"""
        return self.current_card

    def reset_passed_players(self) -> None:
        """Reset the set of passed players"""
        self.passed_players = set()

    def reset_bids(self) -> None:
        """Reset the current bid"""
        self.current_bid = []
        for player in self.players:
            player.reset_bid()

    def increment_game_progress(self) -> None:
        """Increment the game progress"""
        self.game_progress += 1

    def get_game_progress(self) -> int:
        """Get the current game progress"""
        return self.game_progress

    def get_current_player(self) -> Player:
        """Get the current player"""
        return self.players[0]

    def draw_new_auction_card(self) -> Optional[AuctionCard]:
        """Start a new auction by revealing the top card
        Returns the current card or None if the current card ends the game."""
        self.set_auction_card(self.deck.draw())
        if self.get_auction_card().is_end_game():
            self.increment_game_progress()
        if self.get_game_progress() == DEFAULT_GAME_LENGTH:
            return None
        return self.get_auction_card()

    def hold_auction(self) -> Player:
        """Hold an auction for the current card
        Returns the player who won the auction"""
        if self.get_auction_card() is None:
            raise ValueError("No card to auction")
        self.reset_bids()
        self.reset_passed_players()
        if self.get_auction_card().is_disgrace():
            return self.hold_auction_to_avoid()
        else:
            return self.hold_auction_to_win()

    def hold_auction_to_win(self) -> Player:
        """Hold an auction to win the current card.
        Returns the player who obtains the auctioned card."""
        self.current_bid = [0]
        while len(self.passed_players) < len(self.players) - 1:
            print(f"{len(self.passed_players)} have passed out of {len(self.players)}")
            print(f"{self.get_current_player()} now bidding...")
            player_bid = self.get_current_player().bid_or_pass_randomly(
                self.current_bid
            )
            print(f"{self.get_current_player()} bids {player_bid}")
            if player_bid == [-1]:
                self.passed_players.add(self.get_current_player())
            else:
                self.current_bid = player_bid
            self._next_player()
        for player in self.players:
            print(f"{player.name} has bid {player.bid}")
        print(f"{self.passed_players} have all passed")
        self._next_player()
        print(f"{self.get_current_player()} wins the auction!")
        self.get_current_player().win_card(self.current_card)
        self.get_current_player().spend_bid()
        return self.get_current_player()

    def hold_auction_to_avoid(self) -> Player:
        """Hold an auction to avoid the current card.
        Returns the player who obtains the auctioned card."""
        self.current_bid = [0]
        while len(self.passed_players) == 0:
            print(f"{len(self.passed_players)} have passed.")
            player_bid = self.get_current_player().bid_or_pass_randomly(
                self.current_bid
            )
            print(self.get_current_player().name)
            print(player_bid)
            if player_bid == [-1]:
                self.passed_players.add(self.get_current_player())
            else:
                self.current_bid = player_bid
            self._next_player()
        print(self.passed_players)
        winner = self.passed_players.pop()
        print(winner)
        winner.win_card(self.current_card)
        for player in self.players:
            if player is not winner:
                player.spend_bid()
        return winner

    def _next_player(self) -> None:
        """Move to the next active player.
        Raise exception if there is no active player"""
        if self.passed_players.issuperset(self.players):
            raise Exception("All players have passed")
        self.players.append(self.players.pop(0))
        while self.players[0] in self.passed_players:
            self.players.append(self.players.pop(0))

    def calculate_scores(self) -> dict[Player, float]:
        """Calculate the scores for each player"""
        for player in self.players:
            self.scores[player] = player.get_total_score()
        return self.scores

    def get_scores(self) -> dict[Player, float]:
        """Get the game's current scores"""
        self.calculate_scores()
        return self.scores

    def get_winner(self) -> Optional[Player]:
        """Get the winner of the game"""
        lowest_money = min(player.total_money for player in self.players)
        eligible_winners = [
            player for player in self.players if player.total_money > lowest_money
        ]
        if not eligible_winners:
            return None
        else:
            return max(eligible_winners, key=lambda player: player.get_total_score())


def play_sample_game() -> Optional[Player]:
    """Plays a sample game of high society. Returns the winner if there is one."""
    game = HighSociety(["Alice", "Bob", "Charlie", "David"])
    card_count = 0
    while game.draw_new_auction_card() is not None:
        card_count += 1

        print(
            f"This round of the auction we are bidding {'to win' if not game.get_auction_card().is_disgrace() else 'to avoid'} the card: {game.get_auction_card().name}"
        )
        print(
            f"This card {'makes' if game.get_auction_card().is_end_game() else 'does not make'} progress towards ending the game."
        )
        print(
            f"We have seen {game.get_game_progress()} out of {DEFAULT_GAME_LENGTH} game ending cards."
        )

        print(f"{game.hold_auction()} has won {game.get_auction_card()}")
        for player in game.get_players():
            print(f"{player.name} has the funds {player.funds} remaining.")
            print(f"{player.name} has {player.get_total_score()} points.")
            print(
                f"{player.name} has won {'no cards' if not player.cards_won else player.cards_won} "
                f"and has a total score of {player.get_total_score()} points."
            )

        print("\n")

    scores = game.calculate_scores()
    print(f"\nFinal Scores: {scores}")
    print(f"Winner: {game.get_winner()}")

    for player in game.get_players():
        print(
            f"{player.name}: {player.get_total_score()} with {player.total_money} remaining funds."
        )
    return game.get_winner()


if __name__ == "__main__":
    play_sample_game()
