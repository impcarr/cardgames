import random
from typing import List, Optional


class AuctionCard:
    def __init__(self, name: str, card_type: str):
        self.card_type = card_type
        self.name = name
        self.value = 0.0
        self.end_game = False
        self.disgrace = False
        self.theft = False
        self.multiplier = False

    def __str__(self) -> str:
        return f"{self.name} ({self.card_type}) : {self.value}"

    def get_type(self) -> str:
        return self.card_type

    def get_name(self) -> str:
        return self.name

    def get_value(self) -> float:
        return self.value

    def is_end_game(self) -> bool:
        return self.end_game

    def is_disgrace(self) -> bool:
        return self.disgrace

    def is_theft(self) -> bool:
        return self.theft

    def is_multiplier(self) -> bool:
        return self.multiplier


class LuxuryCard(AuctionCard):
    def __init__(self, name: str, value: float):
        super().__init__(name, "Luxury")
        self.value = value


class MultiplierCard(AuctionCard):
    def __init__(self, name: str, value: float):
        super().__init__(name, "Multiplier")
        self.multiplier = True
        self.value = value


class FauxPasCard(AuctionCard):
    def __init__(self, name: str):
        super().__init__(name, "Faux Pas")
        self.theft = True
        self.disgrace = True


class PasseCard(AuctionCard):
    def __init__(self, name: str, value: float):
        super().__init__(name, "Passe")
        self.value = -abs(value)
        self.disgrace = True


class AuctionCardDeck:
    def __init__(self, cards: Optional[List[AuctionCard]] = None):
        if cards is None:
            self._create_default_deck()
        else:
            self.cards = cards

    def _create_default_deck(self) -> None:
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

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> AuctionCard:
        if not self.cards:
            raise Exception("No cards left in the deck.")
        return self.cards.pop()


class AuctionCardHand:
    def __init__(self, cards: Optional[List[AuctionCard]] = None):
        self.cards: List[AuctionCard] = [] if cards is None else cards

    def __str__(self) -> str:
        return ", ".join([str(card) for card in self.cards])

    def __len__(self) -> int:
        return len(self.cards)

    def win_card(self, card: AuctionCard) -> None:
        if card.get_type() == "Faux Pas":
            if self.has_luxury_cards():
                print(
                    "You have won a Faux Pas card. You will be able to select a card to be stolen when I implement that \
                      feature. For now, you will lose your smallest luxury card."
                )
                self.remove_smallest_luxury_card()
            else:
                self.cards.append(card)
        elif self.has_faux_pas_cards() and card.get_type() == "Luxury":
            print(
                "You previously won a Faux Pas card but did not have any luxury cards to steal. You do not receive this card, but \
                  you do lose the Faux Pas card. Press Enter to contine."
            )
            self.remove_faux_pas_card()
        else:
            self.cards.append(card)

    def has_luxury_cards(self) -> bool:
        for card in self.cards:
            if card.get_type() == "Luxury":
                return True
        return False

    def has_faux_pas_cards(self) -> bool:
        for card in self.cards:
            if card.get_type() == "Faux Pas":
                return True
        return False

    def remove_faux_pas_card(self) -> None:
        faux_pas_cards = [card for card in self.cards if card.get_type() == "Faux Pas"]
        if not faux_pas_cards:
            raise Exception("No Faux Pas cards to remove.")
        self.cards.remove(faux_pas_cards[0])

    def remove_smallest_luxury_card(self) -> None:
        luxury_cards = [card for card in self.cards if card.get_type() == "Luxury"]
        smallest_card = min(luxury_cards, key=lambda x: x.get_value())
        self.cards.remove(smallest_card)

    def get_score(self) -> float:
        base_score = sum(
            [
                card.get_value()
                for card in self.cards
                if card.get_type() == "Luxury" or card.get_type() == "Passe"
            ]
        )
        mult = 1.0
        for card in self.cards:
            if card.is_multiplier():
                mult *= card.get_value()
        return base_score * mult
