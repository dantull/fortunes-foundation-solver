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
from typing import Callable, Optional, TypeVar

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

Card = int

def make_card(rank: str, suit: str) -> Card:
    if suit == TAROT_NAME:
        return Card(rank) + TAROT_BASE
    else:
        si = suit_indexes[suit]
        ri = ranks.index(rank) + 1

        return si * SEGMENT + ri

def make_deck() -> list[Card]:
    cards:list[Card] = []
    for s in suits:
        cards.extend(map(lambda r: make_card(r, s), ranks[1:]))

    cards.extend(range(TAROT_BASE, TAROT_BASE + TAROT_COUNT))

    return cards

def suit(n:Card) -> int:
    return n // SEGMENT

def is_tarot(n:Card) -> bool:
    return suit(n) >= len(suits)

def card(n:Card) -> tuple[str, str]:
    d = suit(n)

    if d < len(suits):
        return (ranks[n % 16 - 1], suits[d])
    else:
        return (str(n - TAROT_BASE), TAROT_NAME)

def short_card(n:Card) -> str:
    if n == TAROT_BASE - 1 or n == TAROT_COUNT + TAROT_BASE:
        return ""
    (r, s) = card(n)
    if s == TAROT_NAME:
        return r
    else:
        return r + short_suits[s]

def playable_on(c1:Card, c2:Card) -> bool:
    return abs(c1 - c2) == 1

def fisher_yates_shuffle(arr:list[Card]) -> None:
    for i in range(len(arr)-1, 0, -1):
        j = randrange(i + 1)
        arr[i], arr[j] = arr[j], arr[i]

def split(arr:list[Card], n:int) -> list[list[Card]]:
    return [arr[i:i + n] for i in range(0, len(arr), n)]

deck = make_deck()
fisher_yates_shuffle(deck)

def card_list(arr:list[Card]) -> str:
    return " ".join(map(str, map(short_card, arr)))

T = TypeVar('T')

def first(arr:list[T], pred:Callable[[T], bool]) -> Optional[int]:
    for i, e in enumerate(arr):
        if pred(e):
            return i
        
    return None

def first_empty(arr:list[list[T]]) -> Optional[int]:
    return first(arr, lambda e: len(e) == 0)

def make_stacks() -> list[list[Card]]:
    deck = make_deck()
    fisher_yates_shuffle(deck)
    stacks = split(deck, 7)
    stacks.insert(5, [])

    return stacks

ZeroParamFunction = Callable[[], None]
UndoRedoPair = tuple[ZeroParamFunction, ZeroParamFunction]

class GameState:
    def __init__(self, stacks:list[list[Card]]):
        self.foundations = list(map(lambda f: [f], foundations))
        self.stacks = stacks
        self.stash:Optional[Card] = None

    def __repr__(self) -> str:
        return (SEPARATOR +
            "stash: " + (self.stash is not None and short_card(self.stash) or "") + "\n\n"
            + "\n".join(map(card_list, self.foundations)) + "\n"
            + "\n".join(map(card_list, self.stacks))
            + SEPARATOR)

    def state_rep(self) -> str:
        canon_stacks = sorted(filter(lambda t: len(t) > 0, self.stacks), key=lambda t: t[0])
        return repr({'stacks': canon_stacks, 'stash': self.stash})

    def update_foundations(self) -> ZeroParamFunction:
        # generate a list of updates to apply to move cards from stacks to foundations, each
        # update is like a move (below): a pair of functions, one to perform the move and the
        # other to undo it (to do all updates, the undo has to be done in reverse order)

        def move_top_to_foundation(si:int, fi:int) -> None:
            self.foundations[fi].append(self.stacks[si].pop())

        def return_to_stack(si:int, fi:int) -> ZeroParamFunction:
            def fn() -> None:
                self.stacks[si].append(self.foundations[fi].pop())
            return fn
        
        def return_to_stash(fi:int) -> ZeroParamFunction:
            def fn() -> None:
                self.stash = self.foundations[fi].pop()
            return fn

        updates:list[ZeroParamFunction] = []

        while True:
            start = len(updates)
            for j, f in enumerate(self.foundations):
                if self.stash is not None and playable_on(self.stash, f[-1]):
                    self.foundations[j].append(self.stash)
                    self.stash = None
                    updates.append(return_to_stash(j))

                for i, s in enumerate(self.stacks):
                    if len(s) > 0:
                        if (self.stash is None or is_tarot(self.stash)) and playable_on(s[-1], f[-1]):
                            move_top_to_foundation(i, j)
                            updates.append(return_to_stack(i, j))

            # continue until no more moves exist
            if len(updates) == start:
                break

        updates.reverse()

        def undo_all() -> None:
            for fn in updates:
                fn()

        return undo_all

    def move_to_stash(self, si:int) -> None:
        if self.stash is not None:
            raise TypeError("stash must have a value")
        self.stash = self.stacks[si].pop()

    def pop_stash(self, si:int) -> None:
        if self.stash is None:
            raise TypeError("stash must have a value")
        self.stacks[si].append(self.stash)
        self.stash = None

    def is_solved(self) -> bool:
        return self.stash == None and len(list(filter(lambda s: len(s) > 0, self.stacks))) == 0

    def all_moves(self) -> list[UndoRedoPair]:
        # kinds of moves:
        # * play a top card onto a top card (implies an inverse move exists)
        # * play a top card onto the stash (foundation) if available
        # * play a top card onto an empty stack if there is one
        # * play the stash card onto another top card
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

        # FIXME: optimize: treat moving "clumps" of cards as a single move
        moves:list[UndoRedoPair] = []

        def move_to_stash(i:int) -> ZeroParamFunction:
            def fn() -> None:
                self.move_to_stash(i)
            return fn

        def move_stack_top(i:int, j:int) -> ZeroParamFunction:
            def fn() -> None:
                self.stacks[j].append(self.stacks[i].pop())
            return fn

        def pop_stash(i:int) -> ZeroParamFunction:
            def fn() -> None:
                self.pop_stash(i)
            return fn

        empty = first_empty(self.stacks)

        # moves for each stack top to the foundation stash
        if self.stash is None:
            for i, t in enumerate(self.stacks):
                if len(t) > 0:
                    moves.append((move_to_stash(i), pop_stash(i)))
        else:
            # moves of the stash card onto a stack
            for i, t in enumerate(self.stacks):
                if (len(t) == 0 and empty == i) or (len(t) > 0 and playable_on(self.stash, t[-1])):
                    moves.append((pop_stash(i), move_to_stash(i)))

        # move each top to the first empty stack
        if empty is not None:
            def move_empty_pair(i:int) -> UndoRedoPair:
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

MovesWithUndo = tuple[list[UndoRedoPair], ZeroParamFunction, str]

def try_solve(gs:GameState, out_fn:Callable[[str], None] = print) -> bool:
    # basic solving strategy is to enumerate possible moves and try each
    # one, stashing the remaining moves for backtracking and continue
    # after each move, let foundations update, but also preserve that
    # undo script to get back to original state
    #
    # One key issue is that it will be necessary to avoid immediately
    # undoing the previous move (or maybe more generally returning to
    # any already processed state?)
    stack:list[MovesWithUndo] = []
    reps:set[str] = set([gs.state_rep()])

    def compose(um:ZeroParamFunction, undo_fd:ZeroParamFunction) -> ZeroParamFunction:
        def fn() -> None:
            undo_fd()
            um()

        return fn

    moves = None

    while True:
        out_fn(repr(gs))
        out_fn(f"states: {len(reps)}")
        
        moves = moves or gs.all_moves()

        while moves and len(moves) > 0:
            (dm, um) = moves.pop()
            dm()

            rep = gs.state_rep()

            # use the reps set to avoid looping back to an earlier state
            if not rep in reps:
                reps.add(rep)
                stack.append((moves, compose(um, gs.update_foundations()), rep))
                moves = None
            else:
                um() # undo the move and try the next one

        if gs.is_solved():
            out_fn(repr(gs))
            out_fn(f"success! (visited {len(reps)} states, took {len(stack)} moves)")
            return True

        if len(stack) == 0:
            out_fn(f"failed! (visited {len(reps)} states)")
            return False

        # we never found a move
        if moves is not None:
            (moves, undo, rep) = stack.pop()
            out_fn(repr(gs))
            out_fn(f"backtracking: {len(stack)}")
            # undo the last move and its updates
            undo()

if __name__ == "__main__":
    gs:GameState = GameState(make_stacks())
    undo = gs.update_foundations()

    try_solve(gs)
