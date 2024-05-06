# cards 0-21 tarot, 2-10,TJQK Wands, Cups, Swords, Coins (12 * 4) + 22 = 70 cards, 10 stacks of 7
#
# play area: 11 stacks, one starts empty. slot for a single card on top of foundations (blocks foundation card plays while used)
#
# foundations:
# * 2 tarot foundations, both start empty; one goes from 0 upward, second goes from 21 downward
# * 4 suit foundations: all start with ace in play, build upward in order, ending with K
#
# valid moves: always 1 card at a time, matching types (movement of all "stacked" items at once to an empty stack may be worth representing)
from pprint import pprint

SEGMENT = 16
suits = ["Thorns", "Goblets", "Swords", "Coins"]
ranks = list(map(str, list(range(2, 11))))
ranks.extend(["Jack", "Queen", "King"])
TAROT_BASE = (len(suits) + 1) * SEGMENT 

def make_deck():
    cards = []
    for s in range(0, len(suits)):
        s = s * SEGMENT
        cards.extend(range(2 + s, 14 + s))

    cards.extend(range(TAROT_BASE, TAROT_BASE + 22))

    return cards

def card(n):
    d = n // SEGMENT

    if d < len(suits):
        return (ranks[n % 16 - 2], suits[d])
    else:
        return (str(n - TAROT_BASE), "Tarot")

pprint(list(map(card, make_deck())))
