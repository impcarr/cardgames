from typing import List, Optional, Set
from random import shuffle
from dataclasses import dataclass, field
from player import Player
from auction_card import AuctionCardDeck, AuctionCard

DEFAULT_GAME_LENGTH = 4

class NoActivePlayerError(Exception):
    """Raised when there are no active players."""
    pass

# TODO: add player bids for training purposes
@dataclass
class AuctionState:
    passed_players: Set[Player] = field(default_factory=set)
    current_bid: List[int] = field(default_factory=list)

class HighSociety:
    def __init__(self, player_names: List[str]):
        self._players = [Player(name) for name in player_names]
        shuffle(self._players)
        self._deck = AuctionCardDeck()
        self._game_progress = 0
        self._current_card: AuctionCard
        self.auction_state = AuctionState()
        self._scores: dict[Player, float] = {}

    @property
    def players(self) -> List[Player]:
        """Get the list of players"""
        return self._players

    @property
    def current_card(self) -> AuctionCard:
        """Get the current auction card, if there is one"""
        return self._current_card

    @current_card.setter
    def current_card(self, new_card: AuctionCard) -> None:
        """Sets a new card to be bid on"""
        self._current_card = new_card

    @property
    def game_progress(self) -> int:
        """Get the current game progress"""
        return self._game_progress

    @property
    def current_player(self) -> Player:
        """Get the current player"""
        return self._players[0]
    
    @property
    def deck(self) -> AuctionCardDeck:
        """Get the undrawn AuctionCardDeck"""
        return self._deck

    @property
    def passed_players(self) -> set[Player]:
        """Returns the set of passed players"""
        return self.auction_state.passed_players
    
    def mark_player_passed(self, player: Player) -> None:
        """Mark a player as having passed the current auction.
        
        Args:
            player: The player who passed
            
        Raises:
            ValueError: If player is not in the game
        """
        if player not in self.players:
            raise ValueError("Cannot mark unknown player as passed")
        self.auction_state.passed_players.add(player)
    
    @property
    def scores(self) -> dict[Player, float]:
        """Returns the current players and their scores. Does not perform logic to disqualify the player(s) who have spent the most money"""
        return self._scores

    def reset_auction(self) -> None:
        """Reset the auction for a new round.
        
        Resets the current max bid and all players' pass status and bids"""
        self.auction_state = AuctionState()
        for player in self.players:
            player.reset_bid()

    def increment_game_progress(self) -> None:
        """Increment the game progress"""
        self._game_progress += 1

    def draw_new_auction_card(self) -> Optional[AuctionCard]:
        """Start a new auction by revealing the top card
        Returns the current card or None if the current card ends the game."""
        self.current_card = self.deck.draw()
        if self.current_card.is_end_game():
            self.increment_game_progress()
        if self.game_progress == DEFAULT_GAME_LENGTH:
            return None
        return self.current_card

    def hold_auction(self) -> Player:
        """Hold an auction for the current card
        Returns the player who won the auction"""
        if self.current_card is None:
            raise ValueError("No card to auction")
        self.reset_auction()
        if self.current_card.is_disgrace():
            return self.hold_auction_to_avoid()
        else:
            return self.hold_auction_to_win()

    def hold_auction_to_win(self) -> Player:
        """Hold an auction to win the current card.
        Returns the player who obtains the auctioned card."""
        while len(self.passed_players) < len(self.players) - 1:
            print(f"{len(self.passed_players)} have passed out of {len(self.players)}")
            print(f"{self.current_player} now bidding...")
            player_bid = self.current_player.bid_or_pass_randomly(
                self.auction_state.current_bid
            )
            print(f"{self.current_player} bids {player_bid}")
            if player_bid == [-1]:
                self.mark_player_passed(self.current_player)
            else:
                self.auction_state.current_bid = player_bid
            self._next_player()
        for player in self.players:
            print(f"{player.name} has bid {player.bid}")
        print(f"{self.passed_players} have all passed")
        self._next_player()
        print(f"{self.current_player} wins the auction!")
        self.current_player.win_card(self.current_card)
        self.current_player.spend_bid()
        return self.current_player

    def hold_auction_to_avoid(self) -> Player:
        """Hold an auction to avoid the current card.
        Returns the player who obtains the auctioned card."""
        while len(self.passed_players) == 0:
            print(f"{len(self.passed_players)} have passed.")
            player_bid = self.current_player.bid_or_pass_randomly(
                self.auction_state.current_bid
            )
            print(self.current_player.name)
            print(player_bid)
            if player_bid == [-1]:
                self.mark_player_passed(self.current_player)
            else:
                self.auction_state.current_bid = player_bid
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
        
        Rotates the player list until reaching a player who hasn't passed.
        
        Raises:
            NoActivePlayerError: If all players have passed or no players exist
        Side Effects:
            Modifies self.players list order
        """
        if not self.players:
            raise NoActivePlayerError("No players in game")
        if self.passed_players.issuperset(self.players):
            raise NoActivePlayerError("All players have passed")
        
        rotations = 0
        while rotations < len(self.players):
            self.players.append(self.players.pop(0))
            if self.players[0] not in self.passed_players:
                return
            rotations+=1
        
        raise NoActivePlayerError("No active players found after full rotation")
        

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
            f"This round of the auction we are bidding {'to win' if not game.current_card.is_disgrace() else 'to avoid'} the card: {game.current_card.name}"
        )
        print(
            f"This card {'makes' if game.current_card.is_end_game() else 'does not make'} progress towards ending the game."
        )
        print(
            f"We have seen {game.game_progress} out of {DEFAULT_GAME_LENGTH} game ending cards."
        )

        print(f"{game.hold_auction()} has won {game.current_card}")
        for player in game.players:
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

    for player in game.players:
        print(
            f"{player.name}: {player.get_total_score()} with {player.total_money} remaining funds."
        )
    return game.get_winner()


if __name__ == "__main__":
    play_sample_game()
