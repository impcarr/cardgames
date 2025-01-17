import unittest
from player import Player
from auction_card import AuctionCardHand, LuxuryCard


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player("Test Player")
        self.custom_player = Player("Custom Player", [1000, 2000, 3000])

    def test_player_initialization(self):
        """Test if player is initialized with correct attributes"""
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(len(self.player.funds), 11)  # Default funds list length
        self.assertIsInstance(self.player.cards_won, AuctionCardHand)
        self.assertEqual(self.player.bid, [])

    def test_repr(self):
        """Test that the ___repr___ method works correctly"""
        self.assertEqual(repr(self.custom_player), "Custom Player")

    def test_custom_funds_initialization(self):
        """Test if player can be initialized with custom funds"""
        self.assertEqual(len(self.custom_player.funds), 3)
        self.assertEqual(self.custom_player.funds, [1000, 2000, 3000])

    def test_get_total_money(self):
        """Test calculation of total money"""
        self.assertEqual(self.custom_player.total_money, 6000)

    def test_get_total_score(self):
        """Test calculation of total score"""
        # Add some cards to test scoring
        luxury_card = LuxuryCard("Test Luxury", 10.0)
        self.player.cards_won.win_card(luxury_card)
        self.assertEqual(self.player.get_total_score(), 10.0)

    def test_can_afford(self):
        """Test if player can afford specific bid amounts"""
        self.custom_player = Player("Custom Player", [1000, 2000])
        self.assertTrue(self.custom_player.can_afford(3000))
        self.assertFalse(self.custom_player.can_afford(4000))

    def test_bid_is_valid(self):
        """Test bid validity checks"""
        self.custom_player = Player("Custom Player", [1000, 2000, 3000])
        self.assertTrue(self.custom_player.bid_is_valid([2000], [1000]))  # Valid bid
        self.assertTrue(
            self.custom_player.bid_is_valid([-1], [1000])
        )  # Passing is valid
        self.assertFalse(self.custom_player.bid_is_valid([1000], [1000]))  # Too low
        self.assertFalse(
            self.custom_player.bid_is_valid([7000], [1000])
        )  # Don't have any 7000 cards
        self.assertFalse(
            self.custom_player.bid_is_valid([1000, 1000], [1000])
        )  # Not enough of given denomination

    def test_get_set_bid(self):
        """Test getting and setting bids"""
        self.custom_player = Player("Custom Player", [1000, 2000, 3000])
        test_bid = [1000, 2000]
        self.custom_player.bid = test_bid
        self.assertEqual(self.custom_player.bid, test_bid)

    def test_set_invalid_bid(self):
        """Test setting invalid bid raises ValueError"""
        self.custom_player = Player("Custom Player", [1000, 2000])
        with self.assertRaises(ValueError):
            self.custom_player.bid = [3000]  # Card not in funds

    def test_pass_bid(self):
        """Test passing on a bid"""
        self.player.pass_bid()
        self.assertEqual(self.player.bid, [-1])

    def test_get_valid_bids(self):
        """Test generation of valid bids"""
        self.custom_player = Player("Custom Player", [1000, 2000])
        current_bid = [500]
        valid_bids = self.custom_player.get_valid_bids(current_bid)

        # Should include [1000], [2000], [1000, 2000]
        self.assertEqual(len(valid_bids), 3)
        self.assertIn([1000], valid_bids)
        self.assertIn([2000], valid_bids)
        self.assertIn([1000, 2000], valid_bids)

    def test_reset_bid(self):
        """Test resetting bid"""
        self.player.bid = [1000]
        self.player.reset_bid()
        self.assertEqual(self.player.bid, [])

    def test_spend_bid(self):
        """Test spending bid removes cards from funds"""
        self.custom_player = Player("Custom Player", [1000, 2000, 3000])
        initial_total = self.custom_player.total_money

        self.custom_player.bid = [1000, 2000]
        self.custom_player.spend_bid()

        # Check funds were reduced
        self.assertEqual(self.custom_player.total_money, initial_total - 3000)
        # Check bid was reset
        self.assertEqual(self.custom_player.bid, [])
        # Check specific cards were removed
        self.assertNotIn(1000, self.custom_player.funds)
        self.assertNotIn(2000, self.custom_player.funds)
        self.assertIn(3000, self.custom_player.funds)

    def test_get_random_valid_raise(self):
        """Test random valid raise generation"""
        self.custom_player = Player("Custom Player", [1000, 2000])
        current_bid = [500]

        random_bid = self.custom_player.get_random_valid_raise(current_bid)

        # Check bid is valid
        self.assertTrue(sum(random_bid) > sum(current_bid))
        self.assertTrue(all(card in self.custom_player.funds for card in random_bid))

    def test_raise_bid(self):
        """Test bid raising functionality"""
        self.custom_player = Player("Custom Player", [1000, 2000, 3000])
        self.custom_player.bid = [1000]

        # Test a successful raise
        self.custom_player.raise_bid([2000])
        self.assertEqual(self.custom_player.bid, [1000, 2000])

        # Test that the method will throw when given an invalid raise
        with self.assertRaises(ValueError):
            self.custom_player.raise_bid([4000])

    def test_bid_or_pass_randomly(self):
        """Test random bidding functionality"""
        self.custom_player = Player("Custom Player", [1000, 2000])

        # Test passing when can't afford current bid
        result = self.custom_player.bid_or_pass_randomly([3000])
        self.assertEqual(result, [-1])

        # Test that random bid is valid when possible
        result = self.custom_player.bid_or_pass_randomly([500])
        if result != [-1]:  # If not passing
            self.assertTrue(sum(result) > 500)
            self.assertTrue(all(card in self.custom_player.funds for card in result))

    def test_win_card(self):
        """Tests that the player wins cards as expected"""
        self.custom_player = Player("Custom Player", [1000,2000])
        self.custom_card = LuxuryCard("Two", 10)
        self.custom_player.win_card(self.custom_card)
        self.custom_hand = AuctionCardHand([self.custom_card])

        self.assertEqual(self.custom_player.cards_won, self.custom_hand)


if __name__ == "__main__":
    unittest.main()
