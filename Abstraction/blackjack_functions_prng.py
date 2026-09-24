"""
Blackjack implemented using only functions, with switchable PRNG.

Two PRNG options:
  - LCG  : Linear Congruential Generator (custom implementation)
  - MT   : Mersenne Twister (Python's built-in random module)

To switch algorithm, change the ACTIVE_PRNG line near the top of the file,
or choose interactively when the game starts.
"""

import random

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# ---------------------------------------------------------------------------
# PRNG factories
# Each factory returns a callable: rand(n) -> int in [0, n-1]
# Using factories (instead of plain functions) lets each PRNG carry its own
# private state without leaking it into global scope.
# ---------------------------------------------------------------------------

def make_lcg(seed=42):
    """
    Linear Congruential Generator.
    Formula: x_{n+1} = (a * x_n + c) mod m

    Parameters are taken from glibc — a widely used standard library —
    which makes this LCG comparable to what C programs use by default.
    """
    a, c, m = 1103515245, 12345, 2 ** 31
    # The state is kept in a one-element list so the inner function can
    # update it. (Plain variables in a closure are read-only in Python 2;
    # a list works in both Python 2 and 3 without needing 'nonlocal'.)
    state = [seed]

    def rand(n):
        state[0] = (a * state[0] + c) % m
        # Map the full-range output into [0, n-1] with modulo.
        return state[0] % n

    return rand


def make_mersenne_twister():
    """
    Mersenne Twister via Python's built-in random module.

    Python's random module uses MT19937 — a high-quality PRNG with a
    period of 2^19937-1, far larger than the LCG's 2^31 period.
    We wrap it so it has the same rand(n) interface as the LCG.
    """
    rng = random.Random()   # isolated instance, not the module-level shared state

    def rand(n):
        return rng.randint(0, n - 1)

    return rand


# ---------------------------------------------------------------------------
# Active PRNG — change this one line to switch the shuffle algorithm.
# ---------------------------------------------------------------------------
ACTIVE_PRNG = make_mersenne_twister()   # <-- swap to make_lcg() to use LCG


def shuffle_deck(deck):
    """
    Fisher-Yates shuffle using the active PRNG.

    Fisher-Yates produces an unbiased permutation: every possible ordering
    of the deck is equally likely, provided the underlying PRNG is uniform.
    """
    deck = deck[:]   # copy so we don't mutate the caller's list
    for i in range(len(deck) - 1, 0, -1):
        # Pick a random position from 0..i and swap it with position i.
        j = ACTIVE_PRNG(i + 1)
        deck[i], deck[j] = deck[j], deck[i]
    return deck


# ---------------------------------------------------------------------------
# Game functions — identical logic to blackjack_functions.py
# ---------------------------------------------------------------------------

def create_deck():
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def card_value(card):
    rank = card[0]
    if rank in ('J', 'Q', 'K'):
        return 10
    if rank == 'A':
        # Aces start at 11; hand_value reduces them to 1 if the total busts.
        return 11
    return int(rank)


def hand_value(hand):
    value = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c[0] == 'A')
    # Re-score each Ace from 11 to 1 (subtract 10) as needed to avoid busting.
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def deal_card(deck):
    # Return the top card and the remaining deck as a new list.
    # Returning a new list keeps the function side-effect-free.
    return deck[0], deck[1:]


def card_str(card):
    return f"{card[0]} of {card[1]}"


def display_hand(name, hand, hide_first=False):
    # hide_first=True conceals the dealer's hole card during the player's turn.
    if hide_first:
        cards = ['[Hidden]'] + [card_str(c) for c in hand[1:]]
        print(f"{name}: {', '.join(cards)}")
    else:
        cards = [card_str(c) for c in hand]
        print(f"{name}: {', '.join(cards)}  (value: {hand_value(hand)})")


def player_turn(hand, deck):
    # Stop early if the player hits exactly 21 — no reason to keep asking.
    while hand_value(hand) < 21:
        display_hand("Your hand", hand)
        choice = input("Hit or Stand? (h/s): ").strip().lower()
        if choice == 'h':
            card, deck = deal_card(deck)
            hand = hand + [card]   # build a new list rather than mutating the argument
            if hand_value(hand) > 21:
                display_hand("Your hand", hand)
                print("Bust!")
                break
        elif choice == 's':
            break
    return hand, deck


def dealer_turn(hand, deck):
    # Casino rule: dealer must hit on 16 or below, stand on 17 or above.
    while hand_value(hand) < 17:
        card, deck = deal_card(deck)
        hand = hand + [card]
    return hand, deck


def determine_winner(player_hand, dealer_hand):
    p = hand_value(player_hand)
    d = hand_value(dealer_hand)
    # Check player bust first — a busted player loses even if the dealer also busts.
    if p > 21:
        return "Dealer wins! You busted."
    if d > 21:
        return "You win! Dealer busted."
    if p > d:
        return "You win!"
    if d > p:
        return "Dealer wins!"
    return "It's a tie!"


def play_game():
    deck = shuffle_deck(create_deck())

    # Deal alternately: player, dealer, player, dealer — standard casino order.
    card, deck = deal_card(deck)
    player_hand = [card]
    card, deck = deal_card(deck)
    dealer_hand = [card]
    card, deck = deal_card(deck)
    player_hand = player_hand + [card]
    card, deck = deal_card(deck)
    dealer_hand = dealer_hand + [card]

    print("\n--- Initial Deal ---")
    # Show only one dealer card; the hole card stays hidden.
    display_hand("Dealer", dealer_hand, hide_first=True)

    # Natural Blackjack on the first two cards wins immediately.
    if hand_value(player_hand) == 21:
        display_hand("Your hand", player_hand)
        print("Blackjack! You win!")
        return

    player_hand, deck = player_turn(player_hand, deck)

    # Dealer only plays if the player hasn't already busted.
    if hand_value(player_hand) <= 21:
        print("\n--- Dealer's Turn ---")
        display_hand("Dealer", dealer_hand)
        dealer_hand, deck = dealer_turn(dealer_hand, deck)
        if len(dealer_hand) > 2:   # only reprint if the dealer actually drew cards
            display_hand("Dealer", dealer_hand)

    print("\n--- Result ---")
    print(determine_winner(player_hand, dealer_hand))


def choose_prng():
    """Reassign ACTIVE_PRNG based on the user's choice at runtime."""
    global ACTIVE_PRNG   # required to rebind the module-level name
    print("Choose PRNG algorithm:")
    print("  1. Mersenne Twister (Python built-in)")
    print("  2. Linear Congruential Generator (LCG)")
    choice = input("Enter 1 or 2: ").strip()
    if choice == '2':
        seed = input("Enter LCG seed (or press Enter for 42): ").strip()
        seed = int(seed) if seed.isdigit() else 42
        ACTIVE_PRNG = make_lcg(seed)
        print(f"Using LCG (seed={seed})")
    else:
        ACTIVE_PRNG = make_mersenne_twister()
        print("Using Mersenne Twister")


def main():
    print("=== Blackjack (switchable PRNG) ===")
    choose_prng()
    while True:
        play_game()
        if input("\nPlay again? (y/n): ").strip().lower() != 'y':
            break
    print("Thanks for playing!")


if __name__ == '__main__':
    main()
