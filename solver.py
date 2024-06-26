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

def top_sequence_len(cs:list[Card]) -> int:
    n = 1
    while len(cs) > n and playable_on(cs[-n], cs[-(n+1)]):
        n += 1

    return min(len(cs), n)

def take_sequence(cs:list[Card]) -> list[Card]:
    n = top_sequence_len(cs)
    res = cs[-n:]
    res.reverse()
    del cs[-n:]

    return res

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
MoveItem = tuple[ZeroParamFunction, ZeroParamFunction, str]

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
                        if (self.stash is None or is_tarot(s[-1])) and playable_on(s[-1], f[-1]):
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
            raise TypeError("stash must not have a value")
        self.stash = self.stacks[si].pop()

    def pop_stash(self, si:int) -> None:
        if self.stash is None:
            raise TypeError("stash must have a value")
        self.stacks[si].append(self.stash)
        self.stash = None

    def is_solved(self) -> bool:
        return self.stash == None and len(list(filter(lambda s: len(s) > 0, self.stacks))) == 0

    def all_moves(self) -> list[MoveItem]:
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

        moves:list[MoveItem] = []

        def move_to_stash(i:int) -> ZeroParamFunction:
            def fn() -> None:
                self.move_to_stash(i)
            return fn

        # for stack to stack moves of multiple items in one go (common play pattern)
        def move_stack_top_and_undo(i: int, j:int) -> MoveItem:
            n = top_sequence_len(self.stacks[i])

            def fn() -> None:
                taken = take_sequence(self.stacks[i])
                self.stacks[j] += taken

            def undo() -> None:
                taken = self.stacks[j][-n:]
                taken.reverse()
                del self.stacks[j][-n:]
                self.stacks[i] += taken

            return (fn, undo, f"move items from stack {i + 1} to {j + 1}")

        def pop_stash(i:int) -> ZeroParamFunction:
            def fn() -> None:
                self.pop_stash(i)
            return fn

        empty = first_empty(self.stacks)

        # moves for each stack top to the foundation stash
        if self.stash is None:
            for i, t in enumerate(self.stacks):
                if len(t) > 0:
                    moves.append((move_to_stash(i), pop_stash(i), f"stash top of stack {i + 1}"))
        else:
            # moves of the stash card onto a stack
            for i, t in enumerate(self.stacks):
                if (len(t) == 0 and empty == i) or (len(t) > 0 and playable_on(self.stash, t[-1])):
                    moves.append((pop_stash(i), move_to_stash(i), f"unstash to stack {i + 1}"))

        # move each top to the first empty stack
        if empty is not None:
            def move_empty_pair(i:int) -> MoveItem:
                return (move_stack_top_and_undo(i, empty))

            for i, t in enumerate(self.stacks):
                if len(t) > 0:
                    moves.append(move_empty_pair(i))

        # collect moves of top cards
        for i, s1 in enumerate(self.stacks):
            for j, s2 in enumerate(self.stacks):
                # only consider each pair once, but since playable_on is always symmetric, each
                # found pair implies two possible (but opposite) moves
                if i > j and len(s1) > 0 and len(s2) > 0 and playable_on(s1[-1], s2[-1]):
                    moves.append(move_stack_top_and_undo(i, j))
                    moves.append(move_stack_top_and_undo(j, i))

        return moves

MovesWithUndo = tuple[list[MoveItem], ZeroParamFunction, str, str]
OutputFn = Callable[[str], None]

def noop_output(s:str) -> None:
    pass

def try_solve(gs:GameState, out_fn:OutputFn = print, verbose_fn:Optional[OutputFn] = None) -> bool:
    # basic solving strategy is to enumerate possible moves and try each
    # one, stashing the remaining moves for backtracking and continue
    # after each move, let foundations update, but also preserve that
    # undo script to get back to original state
    #
    # to avoid loops, a set of state_rep instances (canonicalized form of
    # serialized game state) are kept to avoid returning to already visited
    # game states and getting stuck in loops). This can make the process
    # quite memory intensive if a solution takes a long time to find.
    #
    # This has not really been optimized yet beyond the change to treat
    # stacks of card sequences as single move operatios.
    stack:list[MovesWithUndo] = []
    reps:set[str] = set([gs.state_rep()])

    def compose(um:ZeroParamFunction, undo_fd:ZeroParamFunction) -> ZeroParamFunction:
        def fn() -> None:
            undo_fd()
            um()

        return fn

    moves = None

    while True:
        if verbose_fn:
            verbose_fn(repr(gs))
            verbose_fn(f"states: {len(reps)}")
        
        moves = moves or gs.all_moves()

        while moves and len(moves) > 0:
            (dm, um, desc) = moves.pop()
            dm()

            rep = gs.state_rep()

            # use the reps set to avoid looping back to an earlier state
            if not rep in reps:
                reps.add(rep)
                stack.append((moves, compose(um, gs.update_foundations()), rep, desc))
                moves = None
            else:
                um() # undo the move and try the next one

        if gs.is_solved():
            out_fn(repr(gs))
            out_fn(f"success! (visited {len(reps)} states, took {len(stack)} moves)")
            while len(stack) > 0:
                (_, undo, rep, desc) = stack.pop()
                out_fn(desc)
                undo()
                out_fn(repr(gs))

            out_fn("read solution upward from here")

            return True

        if len(stack) == 0:
            out_fn(f"failed! (visited {len(reps)} states)")
            return False

        # we never found a move
        if moves is not None:
            (moves, undo, rep, desc) = stack.pop()
            if verbose_fn:
                verbose_fn(repr(gs))
                verbose_fn(f"backtracking: {len(stack)}")
            # undo the last move and its updates
            undo()

short_to_full_suit = {v: k for k, v in short_suits.items()}

def parse_short_card(sc:str) -> int:
    maybe_suit = sc[-1]

    if maybe_suit in short_to_full_suit:
        return make_card(sc[0:-1], short_to_full_suit[maybe_suit])
    else:
        return make_card(sc, TAROT_NAME)

def parse_cards(scs:list[str]) -> list[Card]:
    return list(map(parse_short_card, scs))

def to_stack(s:str) -> list[str]:
    return s.split(' ')

if __name__ == "__main__":
    # the 3 if False blocks below configure the GameState with a
    # deal transcribed from the actual game (which does appear to
    # only present winnable deals)

    stacks = make_stacks()

    if False:
        stacks = list(map(parse_cards, [
            ['5/', 'Jt', '9', '10', '2v', '2t', '8/'],
            ['Qt', '7v', '9*', '6/', '10*', '5*', '9v'],
            ['3v', 'K/', 'Q*', 'K*', 'J/', '1', '10v'],
            ['4t', '3', '18', '2/', '4', '8v', '6'],
            ['4*', '3*', '4v', '10t', '17', '7', '7*'],
            [],
            ['12', 'Kv', '9t', '8*', '8t', '11', '14'],
            ['Q/', '5v', '19', 'Kt', 'Qv', '9/', '7/'],
            ['6t', '16', '0', '5', '8', '2*', 'J*'],
            ['Jv', '3/', '3t', '7t', '4/', '6v', '13'],
            ['2', '15', '5t', '10/', '6*', '21', '20']
        ]))

    if False:
        stacks = list(map(parse_cards, [
            ['Qv', '15', '2t', '5*', '5t', '6*', '6'],
            ['9t', '3t', '6v', 'Q*', '8*', '3', '7v'],
            ['3*', '8/', '2v', '2', '20', '17', '9/'],
            ['2*', '6/', '18', '6t', '7/', '5v', '13'],
            ['4t', '16', '0', '10', '12', '10v', '10/'],
            [],
            ['J*', '8', '14', '4', '7*', '21', '5'],
            ['3v', '10*', '1', '3/', 'Qt', '7', 'Kt'],
            ['K/', '4/', 'Jv', '9*', '2/', 'K*', '8v'],
            ['Kv', '9', '19', 'J/', '11', '5/', '9v'],
            ['4v', '10t', '8t', '7t', 'Q/', 'Jt', '4*'],
        ]))

    if False:
        stacks = list(map(parse_cards, [
            ['3t', '5*', '11', '5/', '14', '3*', '9'],
            ['Kt', '5t', '1', 'J/', '18', '7', '15'],
            ['16', '2', '2*', 'K/', '3v', '6*', '10'],
            ['Q/', '19', '7v', '8v', '8t', '10v', '5'],
            ['6t', '6', 'Qt', '2t', '21', '10/', 'Q*'],
            [],
            ['2v', '8*', '4', '4/', '8', '12', '9/'],
            ['2/', '6v', '3', '0', 'Qv', '3/', 'J*'],
            ['4v', '7t', '7/', '6/', '10t', '9v', '4*'],
            ['Jv', '9*', 'Jt', '4t', '13', '20', '7*'],
            ['9t', '17', 'Kv', 'K*', '8/', '5v', '10*'],
        ]))

    if False:
        stacks = list(map(parse_cards, [
            to_stack('11 4t 9t 5/ 6* 12 4'),
            to_stack('9* 3v 7* K/ 20 6t 18'),
            to_stack('Kt 10 2v J/ 8 4* 13'),
            to_stack('9/ 8/ 16 2/ 6/ 10t 9v'),
            to_stack('3* 4/ 14 Q* 3/ 21 1'),
            [],
            to_stack('Q/ 8t 2t 15 Jv Jt 19'),
            to_stack('Qv 8* 6 3t 2 10v 6v'),
            to_stack('7t 5v 17 7v 8v 3 7/'),
            to_stack('10* 4v 9 5* Kv 5t J*'),
            to_stack('Qt 0 K* 2* 5 10/ 7'),
        ]))

    gs:GameState = GameState(stacks)
    undo = gs.update_foundations()

    try_solve(gs)
