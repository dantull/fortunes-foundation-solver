# cards 0-21 tarot, 2-10,TJQK Wands, Cups, Swords, Coins (12 * 4) + 22 = 70 cards, 10 stacks of 7
#
# play area: 11 stacks, one starts empty. slot for a single card on top of foundations (blocks foundation card plays while used)
#
# foundations:
# * 2 tarot foundations, both start empty; one goes from 0 upward, second goes from 21 downward
# * 4 suit foundations: all start with ace in play, build upward in order, ending with K
#
# valid moves: always 1 card at a time, matching types (movement of all "stacked" items at once to an empty stack may be worth representing)
from random import randrange

SEGMENT = 16
suits = ["Thorns", "Goblets", "Swords", "Coins"]
suit_indexes = dict(zip(suits, range(0, len(suits))))
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

def make_card(rank, suit):
    if suit == TAROT_NAME:
        return int(rank) + TAROT_BASE
    else:
        si = suit_indexes[suit]
        ri = ranks.index(rank) + 1

        return si * SEGMENT + ri

def make_deck():
    cards = []
    for s in suits:
        cards.extend(map(lambda r: make_card(r, s), ranks[2:]))

    cards.extend(range(TAROT_BASE, TAROT_BASE + TAROT_COUNT))

    return cards

def card(n):
    d = n // SEGMENT

    if d < len(suits):
        return (ranks[n % 16 - 1], suits[d])
    else:
        return (str(n - TAROT_BASE), TAROT_NAME)

def short_card(n):
    if n == TAROT_BASE - 1 or n == TAROT_COUNT + TAROT_BASE:
        return ""
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

def first(arr, pred):
    for i, e in enumerate(arr):
        if pred(e):
            return i

def first_empty(arr):
    return first(arr, lambda e: len(e) == 0)

def make_stacks():
    deck = make_deck()
    fisher_yates_shuffle(deck)
    stacks = split(deck, 7)
    stacks.insert(5, [])

    return stacks

class GameState:
    def __init__(self, stacks):
        self.foundations = list(map(lambda f: [f], foundations))
        self.stacks = stacks
        self.stash = None
        self.changes = []

    def __repr__(self):
        return (SEPARATOR +
            "stash: " + (self.stash is not None and short_card(self.stash) or "") + "\n\n"
            + "\n".join(map(card_list, self.foundations)) + "\n"
            + "\n".join(map(card_list, self.stacks))
            + SEPARATOR)

    def update_foundations(self):
        # generate a list of updates to apply to move cards from stacks to foundations, each
        # update is like a move (below): a pair of functions, one to perform the move and the
        # other to undo it (to do all updates, the undo has to be done in reverse order)

        def move_top_to_foundation(si, fi):
            self.foundations[fi].append(self.stacks[si].pop())

        def return_to_stack(si, fi):
            def fn():
                self.foundations[fi].append(self.stacks[si].pop())
            return fn

        updates = []
        
        while True:
            start = len(updates)
            for i, s in enumerate(self.stacks):
                for j, f in enumerate(self.foundations):
                    if len(s) > 0:
                        if playable_on(s[-1], f[-1]):
                            move_top_to_foundation(i, j)
                            updates.append(return_to_stack(i, j))

            # continue until no more moves exist
            if len(updates) == start:
                break

        updates.reverse()

        def undo_all():
            if len(updates) > 0:
                # FIXME: write unit tests for this, it is currently buggy
                pass

            for fn in updates:
                fn()

        return undo_all

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

        def move_to_stash(i):
            def fn():
                self.stash = self.stacks[i].pop()
            return fn

        def move_stack_top(i, j):
            def fn():
                self.stacks[j].append(self.stacks[i].pop())
            return fn

        def pop_stash(i):
            def fn():
                self.stacks[i].append(self.stash)
                self.stash = None
            return fn

        # moves for each stack top to the foundation stash
        if self.stash is None:
            for i, t in enumerate(self.stacks):
                if len(t) > 0:
                    moves.append((move_to_stash(i), pop_stash(i)))

        empty = first_empty(self.stacks)

        # move each top to the first empty stack
        if empty is not None:
            def move_empty_pair(i):
                return (move_stack_top(i, empty), move_stack_top(empty, i))

            for i, t in enumerate(self.stacks):
                if len(t) > 0:
                    moves.append(move_empty_pair(i))

        # collect moves of top cards
        for i, s1 in enumerate(self.stacks):
            for j, s2 in enumerate(self.stacks):
                # only consider each pair once, but since playable_on is always symmetric, each
                # found pair implies two possible (but opposite) moves
                if i > j and len(s1) > 0 and len(s2) > 0 and playable_on(s1[-1], s2[-1]):
                    move_to_s2 = move_stack_top(i, j)
                    move_to_s1 = move_stack_top(j, i)
                    moves.append((move_to_s1, move_to_s2))
                    moves.append((move_to_s2, move_to_s1))

        return moves

if __name__ == "__main__":
    gs = GameState(make_stacks())

    print(gs)
    uf = gs.update_foundations()

    for dm, um in gs.all_moves():
        dm()
        ufm = gs.update_foundations()
        print(gs)
        ufm()
        um()

    uf()
    print(gs)
