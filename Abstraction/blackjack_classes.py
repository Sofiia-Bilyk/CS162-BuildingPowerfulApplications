"""
Blackjack implemented using classes.

Each concept in the game maps to a class:
  Card  — a single playing card with a rank and suit
  Deck  — a shuffled collection of 52 cards
  Hand  — the cards held by one player, with scoring logic
  Game  — orchestrates turns and determines the winner
"""

import random


class Card:
    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        if self.rank in ('J', 'Q', 'K'):
            return 10
        if self.rank == 'A':
            # Aces default to 11; Hand.value() reduces them to 1 if the total busts.
            return 11
        return int(self.rank)

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        # Build all 52 cards and shuffle immediately so the deck is ready to deal.
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
        random.shuffle(self.cards)

    def deal(self):
        # Pop from the end of the list — the shuffled order makes this equivalent
        # to drawing from the top of a real deck.
        return self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def value(self):
        total = sum(c.value() for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == 'A')
        # Re-score each Ace from 11 to 1 (subtract 10) as needed to avoid busting.
        # We do this at most once per Ace in the hand.
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_bust(self):
        return self.value() > 21

    def is_blackjack(self):
        # A natural Blackjack requires exactly two cards totalling 21.
        # A later 21 (e.g. after hitting) is not a Blackjack.
        return len(self.cards) == 2 and self.value() == 21

    def display(self, hide_first=False):
        # hide_first=True conceals the dealer's hole card during the player's turn.
        if hide_first:
            cards = ['[Hidden]'] + [str(c) for c in self.cards[1:]]
        else:
            cards = [str(c) for c in self.cards]
        return ', '.join(cards)


class Game:
    def play(self):
        deck = Deck()
        player = Hand()
        dealer = Hand()

        # Deal alternately: player, dealer, player, dealer — standard casino order.
        for _ in range(2):
            player.add(deck.deal())
            dealer.add(deck.deal())

        print("\n--- Initial Deal ---")
        # Show only one dealer card; the hole card stays hidden.
        print(f"Dealer: {dealer.display(hide_first=True)}")
        print(f"You: {player.display()}  (value: {player.value()})")

        # Natural Blackjack wins immediately without further play.
        if player.is_blackjack():
            print("Blackjack! You win!")
            return

        # Player's turn: keep asking until the player stands or busts.
        while not player.is_bust():
            choice = input("\nHit or Stand? (h/s): ").strip().lower()
            if choice == 'h':
                player.add(deck.deal())
                print(f"You: {player.display()}  (value: {player.value()})")
                if player.is_bust():
                    print("Bust!")
            elif choice == 's':
                break

        # Dealer only plays if the player is still in the game.
        if not player.is_bust():
            print("\n--- Dealer's Turn ---")
            print(f"Dealer: {dealer.display()}  (value: {dealer.value()})")
            # Casino rule: dealer must hit on 16 or below, stand on 17 or above.
            while dealer.value() < 17:
                dealer.add(deck.deal())
                print(f"Dealer: {dealer.display()}  (value: {dealer.value()})")

        print("\n--- Result ---")
        print(self._winner(player, dealer))

    def _winner(self, player, dealer):
        p, d = player.value(), dealer.value()
        # Check player bust first — a busted player loses even if dealer also busts.
        if p > 21:
            return "Dealer wins! You busted."
        if d > 21:
            return "You win! Dealer busted."
        if p > d:
            return "You win!"
        if d > p:
            return "Dealer wins!"
        return "It's a tie!"

    def run(self):
        print("=== Blackjack ===")
        while True:
            self.play()
            if input("\nPlay again? (y/n): ").strip().lower() != 'y':
                break
        print("Thanks for playing!")


if __name__ == '__main__':
    Game().run()
