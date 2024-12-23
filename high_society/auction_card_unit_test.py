import unittest
import unittest.mock
from auction_card import AuctionCard, LuxuryCard, MultiplierCard, FauxPasCard, PasseCard, AuctionCardDeck, AuctionCardHand

class TestBaseAuctionCard(unittest.TestCase):
    def setUp(self):
        self.base_card = AuctionCard("Test Card", "Test Type")

    def test_base_card_initialization(self):
        """Test if base card is initialized with correct attributes"""
        self.assertEqual(self.base_card.get_name(), "Test Card")
        self.assertEqual(self.base_card.get_type(), "Test Type")
        self.assertEqual(self.base_card.get_value(), 0.0)
        self.assertFalse(self.base_card.is_end_game())
        self.assertFalse(self.base_card.is_disgrace())
        self.assertFalse(self.base_card.is_theft())
        self.assertFalse(self.base_card.is_multiplier())

class TestLuxuryCard(unittest.TestCase):
    def setUp(self):
        self.luxury_card = LuxuryCard("Luxury Test", 10.0)
        self.second_luxury_card = LuxuryCard("Luxury Test 2", 20.0)

    def test_luxury_card_initialization(self):
        """Test if luxury card is initialized correctly"""
        self.assertEqual(self.luxury_card.get_name(), "Luxury Test")
        self.assertEqual(self.luxury_card.get_type(), "Luxury")
        self.assertEqual(self.luxury_card.get_value(), 10.0)
        self.assertFalse(self.luxury_card.is_multiplier())
        self.assertFalse(self.luxury_card.is_theft())
        self.assertFalse(self.luxury_card.is_disgrace())

class TestMultiplierCard(unittest.TestCase):
    def setUp(self):
        self.multiplier_card = MultiplierCard("Multiplier Test", 2.0)

    def test_multiplier_card_initialization(self):
        """Test if multiplier card is initialized correctly"""
        self.assertEqual(self.multiplier_card.get_name(), "Multiplier Test")
        self.assertEqual(self.multiplier_card.get_type(), "Multiplier")
        self.assertEqual(self.multiplier_card.get_value(), 2.0)
        self.assertTrue(self.multiplier_card.is_multiplier())

class TestFauxPasCard(unittest.TestCase):
    def setUp(self):
        self.faux_pas_card = FauxPasCard("Faux Pas Test")

    def test_faux_pas_card_initialization(self):
        """Test if faux pas card is initialized correctly"""
        self.assertEqual(self.faux_pas_card.get_name(), "Faux Pas Test")
        self.assertEqual(self.faux_pas_card.get_type(), "Faux Pas")
        self.assertTrue(self.faux_pas_card.is_theft())
        self.assertTrue(self.faux_pas_card.is_disgrace())

class TestPasseCard(unittest.TestCase):
    def setUp(self):
        self.passe_card = PasseCard("Passe Test", 5.0)

    def test_passe_card_initialization(self):
        """Test if passe card is initialized correctly"""
        self.assertEqual(self.passe_card.get_name(), "Passe Test")
        self.assertEqual(self.passe_card.get_type(), "Passe")
        self.assertEqual(self.passe_card.get_value(), -5.0)
        self.assertTrue(self.passe_card.is_disgrace())

class TestAuctionCardDeck(unittest.TestCase):
    def setUp(self):
        self.deck = AuctionCardDeck()

    def test_default_deck_initialization(self):
        """Test if default deck is created with correct number of cards"""
        self.assertEqual(len(self.deck.cards), 16)  # Based on _create_default_deck method

    def test_default_deck_composition(self):
        """Test if default deck contains correct card types"""
        card_types = [card.get_type() for card in self.deck.cards]
        self.assertIn("Faux Pas", card_types)
        self.assertIn("Passe", card_types)
        self.assertIn("Multiplier", card_types)
        self.assertIn("Luxury", card_types)

    def test_draw_card(self):
        """Test if drawing a card removes it from deck and returns correct card"""
        initial_length = len(self.deck.cards)
        drawn_card = self.deck.draw()
        
        self.assertEqual(len(self.deck.cards), initial_length - 1)
        self.assertIsInstance(drawn_card, AuctionCard)

class TestAuctionCardHand(unittest.TestCase):
    def setUp(self):
        self.hand = AuctionCardHand()
        self.luxury_card = LuxuryCard("Luxury", 10.0)
        self.second_luxury_card = LuxuryCard("Luxury", 20.0)
        self.multiplier_card = MultiplierCard("Multiplier", 2.0)
        self.theft_card = FauxPasCard("Faux Pas")
        self.passe_card = PasseCard("Passe", 5.0)

    def test_win_luxury_card(self):
        """Test winning a luxury card"""
        self.hand.win_card(self.luxury_card)
        print(self.hand)
        self.assertEqual(len(self.hand.cards), 1)

    def test_win_multiplier_card(self):
        """Test winning a multiplier card"""
        self.hand.win_card(self.multiplier_card)
        self.assertEqual(len(self.hand.cards), 1)

    def test_win_theft_card_with_no_luxury_cards(self):
        """Test winning a theft card when hand has no luxury cards"""
        self.hand.win_card(self.theft_card)
        self.assertEqual(len(self.hand.cards), 1)
    
    def test_win_luxury_card_with_theft_card(self):
        """Test winning a luxury card when hand has a theft card"""
        self.hand.win_card(self.theft_card)  # First win theft card
        self.hand.win_card(self.luxury_card)  # Then win luxury card
        self.assertEqual(len(self.hand.cards), 0)  # Both cards should be absent

    def test_win_theft_card_with_multiple_luxury_cards(self):
        """Test winning a theft card when hand has multiple luxury cards"""
        self.hand.win_card(self.luxury_card)
        self.hand.win_card(self.second_luxury_card)
        self.hand.win_card(self.theft_card)
        self.assertEqual(len(self.hand.cards), 1) # Only second luxury card should be present 
        self.assertAlmostEqual(self.hand.get_score(), 20.0)

    def test_score_calculation(self):
        """Test score calculation with luxury and multiplier cards"""
        self.hand.win_card(LuxuryCard("Luxury1", 10.0))
        self.hand.win_card(LuxuryCard("Luxury2", 20.0))
        initial_score = self.hand.get_score()
        self.assertEqual(initial_score, 30.0)

        self.hand.win_card(PasseCard("Passe", 5.0))
        passe_score = self.hand.get_score()
        self.assertEqual(passe_score, 25.0)

        self.hand.win_card(MultiplierCard("Multiplier", 2.0))
        multiplied_score = self.hand.get_score()
        self.assertEqual(multiplied_score, 50.0)

    def test_multiple_multipliers(self):
        """Test score calculation with multiple multipliers"""
        self.hand.win_card(LuxuryCard("Luxury", 10.0))
        self.hand.win_card(MultiplierCard("Mult1", 2.0))
        self.hand.win_card(MultiplierCard("Mult2", 3.0))
        self.assertEqual(self.hand.get_score(), 60.0)  # 10 * 2 * 3 = 60

if __name__ == '__main__':
    unittest.main()