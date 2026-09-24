"""
Blackjack implemented using only functions.

All state is passed explicitly as arguments and return values —
there are no classes or global variables.
"""

import random

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def create_deck():
    # Build a standard 52-card deck as a list of (rank, suit) tuples.
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def shuffle_deck(deck):
    # Copy first so we don't mutate the original list passed in.
    deck = deck[:]
    random.shuffle(deck)
    return deck


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
    # Each Ace can be re-scored as 1 (subtract 10) to avoid busting.
    # We only do this as many times as there are Aces in the hand.
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
    # hide_first=True is used for the dealer's initial display:
    # in real Blackjack one dealer card is face-down (the "hole card").
    if hide_first:
        cards = ['[Hidden]'] + [card_str(c) for c in hand[1:]]
        print(f"{name}: {', '.join(cards)}")
    else:
        cards = [card_str(c) for c in hand]
        print(f"{name}: {', '.join(cards)}  (value: {hand_value(hand)})")


def player_turn(hand, deck):
    # Stop the loop if the player reaches exactly 21 — no reason to keep asking.
    while hand_value(hand) < 21:
        display_hand("Your hand", hand)
        choice = input("Hit or Stand? (h/s): ").strip().lower()
        if choice == 'h':
            card, deck = deal_card(deck)
            hand = hand + [card]   # build a new list to avoid mutating the argument
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


def play_game():
    deck = shuffle_deck(create_deck())

    # Deal alternately: player, dealer, player, dealer — standard casino dealing order.
    card, deck = deal_card(deck)
    player_hand = [card]
    card, deck = deal_card(deck)
    dealer_hand = [card]
    card, deck = deal_card(deck)
    player_hand = player_hand + [card]
    card, deck = deal_card(deck)
    dealer_hand = dealer_hand + [card]

    print("\n--- Initial Deal ---")
    # Show only one dealer card so the player can't see the hole card.
    display_hand("Dealer", dealer_hand, hide_first=True)

    # A natural Blackjack (21 on the first two cards) wins immediately —
    # the player doesn't need to take any more turns.
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


def main():
    print("=== Blackjack ===")
    while True:
        play_game()
        if input("\nPlay again? (y/n): ").strip().lower() != 'y':
            break
    print("Thanks for playing!")


if __name__ == '__main__':
    main()
