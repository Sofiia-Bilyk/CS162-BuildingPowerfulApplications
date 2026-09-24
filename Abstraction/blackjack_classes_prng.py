"""
Blackjack implemented using classes, with switchable PRNG.

Two PRNG options:
  - LCG            : Linear Congruential Generator (custom implementation)
  - MersenneTwister: Wraps Python's built-in random module

The PRNG is injected into Game and Deck as a dependency, so switching
algorithms requires changing only one line in __main__:
    Game(LCG(seed=42)).run()
    Game(MersenneTwister()).run()
"""

import random


# ---------------------------------------------------------------------------
# PRNG classes
# ---------------------------------------------------------------------------

class PRNG:
    """
    Abstract base for pseudo-random number generators.

    Defining a shared interface here means the rest of the code only
    depends on randint(n) and doesn't care which algorithm is underneath.
    Swapping algorithms is then a matter of passing a different subclass.
    """

    def randint(self, n):
        """Return a random integer in [0, n-1]."""
        raise NotImplementedError


class LCG(PRNG):
    """
    Linear Congruential Generator.
    Formula: x_{n+1} = (a * x_n + c) mod m

    Parameters are taken from glibc — a widely used standard library —
    which makes this LCG comparable to what C programs use by default.
    The period is 2^31, which is sufficient for shuffling a 52-card deck.
    """

    def __init__(self, seed=42):
        self.a = 1103515245
        self.c = 12345
        self.m = 2 ** 31
        self.state = seed   # the seed determines the entire sequence of numbers

    def randint(self, n):
        self.state = (self.a * self.state + self.c) % self.m
        # Map the full-range output into [0, n-1] with modulo.
        return self.state % n


class MersenneTwister(PRNG):
    """
    Mersenne Twister via Python's built-in random module.

    Python's random module uses MT19937 — a high-quality PRNG with a
    period of 2^19937-1, far larger than the LCG's 2^31 period.
    We wrap it in a PRNG subclass so it shares the same randint(n) interface.
    """

    def __init__(self):
        # Use an isolated Random instance rather than the module-level shared
        # state, so this PRNG doesn't interfere with other code using random.
        self._rng = random.Random()

    def randint(self, n):
        return self._rng.randint(0, n - 1)


# ---------------------------------------------------------------------------
# Game classes
# ---------------------------------------------------------------------------

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
    def __init__(self, prng):
        # Build all 52 cards then immediately shuffle so the deck is ready to deal.
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
        self._shuffle(prng)

    def _shuffle(self, prng):
        """
        Fisher-Yates shuffle using the injected PRNG.

        Fisher-Yates produces an unbiased permutation: every possible ordering
        is equally likely, provided the underlying PRNG is uniform.
        The algorithm works backwards, swapping each position with a random
        earlier (or equal) position.
        """
        cards = self.cards
        for i in range(len(cards) - 1, 0, -1):
            j = prng.randint(i + 1)   # pick a random index from 0..i
            cards[i], cards[j] = cards[j], cards[i]

    def deal(self):
        # Pop from the end of the list — equivalent to drawing from the top
        # of a real deck because the list was already shuffled.
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
        # We only do this as many times as there are Aces in the hand.
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_bust(self):
        return self.value() > 21

    def is_blackjack(self):
        # A natural Blackjack requires exactly two cards totalling 21.
        # A later 21 reached by hitting is not counted as a Blackjack.
        return len(self.cards) == 2 and self.value() == 21

    def display(self, hide_first=False):
        # hide_first=True conceals the dealer's hole card during the player's turn.
        if hide_first:
            cards = ['[Hidden]'] + [str(c) for c in self.cards[1:]]
        else:
            cards = [str(c) for c in self.cards]
        return ', '.join(cards)


class Game:
    def __init__(self, prng):
        # Store the PRNG so the same algorithm is reused across all rounds.
        self.prng = prng

    def play(self):
        # A fresh deck is created (and shuffled with the stored PRNG) each round.
        deck = Deck(self.prng)
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

        # Natural Blackjack on the first two cards wins immediately.
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
        print("=== Blackjack (switchable PRNG) ===")
        while True:
            self.play()
            if input("\nPlay again? (y/n): ").strip().lower() != 'y':
                break
        print("Thanks for playing!")


def choose_prng():
    """Prompt the user to select a PRNG and return the configured instance."""
    print("Choose PRNG algorithm:")
    print("  1. Mersenne Twister (Python built-in)")
    print("  2. Linear Congruential Generator (LCG)")
    choice = input("Enter 1 or 2: ").strip()
    if choice == '2':
        seed = input("Enter LCG seed (or press Enter for 42): ").strip()
        seed = int(seed) if seed.isdigit() else 42
        print(f"Using LCG (seed={seed})")
        return LCG(seed)
    print("Using Mersenne Twister")
    return MersenneTwister()


if __name__ == '__main__':
    prng = choose_prng()
    Game(prng).run()
