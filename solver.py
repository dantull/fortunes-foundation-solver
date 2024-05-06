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
from random import randrange

SEGMENT = 16
suits = ["Thorns", "Goblets", "Swords", "Coins"]
ranks = list(map(str, list(range(2, 11))))
ranks.extend(["J", "Q", "K"])
TAROT_BASE = (len(suits) + 1) * SEGMENT 
TAROT_NAME = "Tarot"

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
        return (str(n - TAROT_BASE), TAROT_NAME)

def playable_on(c1, c2):
    return abs(c1 - c2) == 1

def fisher_yates_shuffle(arr):
    for i in range(len(arr)-1, 0, -1):
        j = randrange(i + 1)
        arr[i], arr[j] = arr[j], arr[i]

def split(arr, n):
    return [arr[i:i + n] for i in range(0, len(arr), n)]

deck = make_deck()
fisher_yates_shuffle(deck)

pprint(split(list(map(card, deck)), 7))


print(card(deck[0]), list(map(card, filter(lambda c: playable_on(deck[0], c), deck))))

