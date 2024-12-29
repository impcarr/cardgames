import random
from typing import List, Optional


class AuctionCard:
    def __init__(self, name: str, card_type: str):
        self._card_type = card_type
        self._name = name
        self._value = 0.0
        self._end_game = False
        self._disgrace = False
        self._theft = False
        self._is_multiplier = False

    def __repr__(self) -> str:
        return f"{self._name} ({self._card_type}) : {self._value}"

    @property
    def type(self) -> str:
        return self._card_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> float:
        return self._value
    
    @value.setter
    def value(self, value: float):
        self._value = value

    def is_end_game(self) -> bool:
        return self._end_game

    def is_disgrace(self) -> bool:
        return self._disgrace

    def is_theft(self) -> bool:
        return self._theft

    def is_multiplier(self) -> bool:
        return self._is_multiplier


class LuxuryCard(AuctionCard):
    def __init__(self, name: str, value: float):
        super().__init__(name, "Luxury")
        self._value = value


class MultiplierCard(AuctionCard):
    def __init__(self, name: str, value: float):
        super().__init__(name, "Multiplier")
        self._is_multiplier = True
        self._end_game = True
        self._value = value
        self._disgrace = (self._value < 1)


class FauxPasCard(AuctionCard):
    def __init__(self, name: str):
        super().__init__(name, "Faux Pas")
        self._theft = True
        self._disgrace = True


class PasseCard(AuctionCard):
    def __init__(self, name: str, value: float):
        super().__init__(name, "Passe")
        self._value = -abs(value)
        self._disgrace = True


class AuctionCardDeck:
    def __init__(self, cards: Optional[List[AuctionCard]] = None):
        if (
            cards is None
        ):  # Use None as default instead of [] to avoid mutable default argument errors
            self._create_default_deck()
        else:
            self.cards = cards
        self.shuffle()

    def _create_default_deck(self) -> None:
        """Create a default deck of auction cards"""
        faux_pas = FauxPasCard("Faux Pas")
        passe = PasseCard("Passe", -5)
        scandale = MultiplierCard("Scandale", value=0.5)
        avant_garde = MultiplierCard("Avant Garde", value=2)
        bon_vivant = MultiplierCard("Bon Vivant", value=2)
        joie_de_vivre = MultiplierCard("Joie de Vivre", value=2)
        one = LuxuryCard("One", value=1)
        two = LuxuryCard("Two", value=2)
        three = LuxuryCard("Three", value=3)
        four = LuxuryCard("Four", value=4)
        five = LuxuryCard("Five", value=5)
        six = LuxuryCard("Six", value=6)
        seven = LuxuryCard("Seven", value=7)
        eight = LuxuryCard("Eight", value=8)
        nine = LuxuryCard("Nine", value=9)
        ten = LuxuryCard("Ten", value=10)
        self.cards = [
            faux_pas,
            passe,
            scandale,
            avant_garde,
            bon_vivant,
            joie_de_vivre,
            one,
            two,
            three,
            four,
            five,
            six,
            seven,
            eight,
            nine,
            ten,
        ]

    def __repr__(self) -> str:
        return str(self.cards)

    def shuffle(self) -> None:
        """Shuffle the deck"""
        random.shuffle(self.cards)

    def draw(self) -> AuctionCard:
        """Draw the top card from the deck"""
        if not self.cards:
            raise Exception("No cards left in the deck.")
        return self.cards.pop(0)


class AuctionCardHand:
    def __init__(self, cards: Optional[List[AuctionCard]] = None):
        # Use None as default instead of [] to avoid mutable default argument errors
        self.cards: List[AuctionCard] = [] if cards is None else cards

    def __str__(self) -> str:
        return ", ".join([str(card) for card in self.cards])

    def __len__(self) -> int:
        return len(self.cards)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, AuctionCardHand):
            return self.cards == other.cards
        elif isinstance(other, List):
            return self.cards == other
        return NotImplemented

    def win_card(self, card: AuctionCard) -> None:
        """Add a card to the hand, handling special cases for Faux Pas and Luxury cards"""
        if card.type == "Faux Pas":
            if self.has_luxury_cards():
                print(
                    "You have won a Faux Pas card. You will be able to select a card to be stolen when I implement that "
                    "feature. For now, you will lose your smallest luxury card."
                )
                self.remove_smallest_luxury_card()
            else:
                self.cards.append(card)
        elif self.has_faux_pas_cards() and card.type == "Luxury":
            print(
                "You previously won a Faux Pas card but did not have any luxury cards to steal. You do not receive this card, but "
                "you do lose the Faux Pas card."
            )
            self.remove_faux_pas_card()
        else:
            self.cards.append(card)

    def has_luxury_cards(self) -> bool:
        """Check if the hand has any luxury cards"""
        for card in self.cards:
            if card.type == "Luxury":
                return True
        return False

    def has_faux_pas_cards(self) -> bool:
        """Check if the hand has any Faux Pas cards"""
        for card in self.cards:
            if card.type == "Faux Pas":
                return True
        return False

    def remove_faux_pas_card(self) -> None:
        """Remove a Faux Pas card from the hand"""
        faux_pas_cards = [card for card in self.cards if card.type == "Faux Pas"]
        if not faux_pas_cards:
            raise Exception("No Faux Pas cards to remove.")
        self.cards.remove(faux_pas_cards[0])

    def remove_smallest_luxury_card(self) -> None:
        """Remove the smallest luxury card from the hand"""
        luxury_cards = [card for card in self.cards if card.type == "Luxury"]
        smallest_card = min(luxury_cards, key=lambda x: x.value)
        self.cards.remove(smallest_card)

    def get_score(self) -> float:
        """Calculate the total score of the hand"""
        base_score = sum(
            [
                card.value
                for card in self.cards
                if card.type == "Luxury" or card.type == "Passe"
            ]
        )
        mult = 1.0
        for card in self.cards:
            if card.is_multiplier():
                mult *= card.value
        return base_score * mult
