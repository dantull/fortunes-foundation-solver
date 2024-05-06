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
short_suits = dict(zip(suits, ["/", "v", "t", "*"]))
ranks = ["A"]
ranks.extend(list(map(str, list(range(2, 11)))))
ranks.extend(["J", "Q", "K"])
TAROT_BASE = len(suits) * SEGMENT
TAROT_COUNT = 22
TAROT_NAME = "Tarot"
STACKS = 11 # deck is 70, initial deal is 10 stacks of 7

SEPARATOR = "\n" +  ("-" * 40) + "\n"

# one ace of each suit and the bottom and top tarot cards
foundations = list(map(lambda n: n * 16 + 1, range(0, len(suits))))
foundations.append(TAROT_BASE - 1)
foundations.append(TAROT_COUNT + TAROT_BASE)

def make_deck():
    cards = []
    for s in range(0, len(suits)):
        s = s * SEGMENT
        cards.extend(range(2 + s, 14 + s))

    cards.extend(range(TAROT_BASE, TAROT_BASE + TAROT_COUNT))

    return cards

def card(n):
    d = n // SEGMENT

    if d < len(suits):
        return (ranks[n % 16 - 1], suits[d])
    else:
        return (str(n - TAROT_BASE), TAROT_NAME)

def short_card(n):
    (r, s) = card(n)
    if s == TAROT_NAME:
        return r
    else:
        return r + short_suits[s]

def playable_on(c1, c2):
    return abs(c1 - c2) == 1

def fisher_yates_shuffle(arr):
    for i in range(len(arr)-1, 0, -1):
        j = randrange(i + 1)
        arr[i], arr[j] = arr[j], arr[i]

def split(arr, n):
    return [arr[i:i + n] for i in range(0, len(arr), n)]

def top(arr):
    return len(arr) > 0 and arr[-1] or None

deck = make_deck()
fisher_yates_shuffle(deck)

def card_list(arr):
    return " ".join(map(str, map(short_card, arr)))

class GameState:
    def __init__(self):
        self.foundations = foundations.copy()
        deck = make_deck()
        fisher_yates_shuffle(deck)
        self.stacks = split(deck, 7)
        self.stacks.insert(5, [])
        self.stash = None
        self.moves = []

    def __repr__(self):
        return (SEPARATOR +
            "stash: " + (self.stash is not None and short_card(self.stash) or "") + "\n\n" +
            "\n".join(map(card_list, self.stacks))
            + SEPARATOR)

    def all_moves(self):
        # kinds of moves:
        # * play a top card onto a top card (implies an inverse move exists)
        # * play a top card onto the stash (foundation) if available
        # * play a top card onto an empty stack if there is one
        #
        # might consider moving a whole stack of cards as one move if
        # they are already assembled and moving to a stack since that's
        # common and is _way_ less expensive to compute
        #
        # note that if there are multiple empty stacks there's still
        # only one move to consider per top (no sense in distinguishing
        # between moving to one open stack over another)
        #
        # a move is a pair of functions, one that performs the move and
        # one that restores the GameState back to its former state.
        moves = []

        def move_to_stash(self, i):
            def fn():
                self.stash = self.stacks[i].pop()
            return fn

        def pop_stash(self, i):
            def fn():
                self.stacks[i].append(self.stash)
                self.stash = None
            return fn

        if self.stash is None:
            for i, t in enumerate(self.stacks):
                if len(t) > 0:
                    moves.append((move_to_stash(self, i), pop_stash(self, i)))

        return moves

gs = GameState()

print(gs)
for dm, um in gs.all_moves():
    dm()
    print(gs)
    um()

print(gs)