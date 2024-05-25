import unittest
import solver
from typing import Callable, Optional

CardDesc = tuple[str, str]

def stack_of(cards:list[CardDesc]) -> list[solver.Card]:
    return list(map(lambda c: solver.make_card(*c), cards))

class TestCardCreation(unittest.TestCase):
    def test_make_card(self) -> None:
        for rank in solver.ranks:
            for suit in solver.suits:
                n = solver.make_card(rank, suit)
                (r, s) = solver.card(n)
                self.assertEqual(r, rank)
                self.assertEqual(s, suit)

        for t in range(0, solver.TAROT_COUNT):
            n = solver.make_card(str(t), solver.TAROT_NAME)
            (r, s) = solver.card(n)
            self.assertEqual(str(t), r)
            self.assertEqual(s, solver.TAROT_NAME)

    def test_make_deck(self) -> None:
        deck = solver.make_deck()
        self.assertEqual(70, len(deck))

    def test_is_tarot(self) -> None:
        def is_tarot(r:str, s:str) -> bool:
            return solver.is_tarot(solver.make_card(r, s))
        self.assertFalse(is_tarot("10", "Goblets"))
        self.assertFalse(is_tarot("A", "Swords"))
        self.assertFalse(is_tarot("8", "Coins"))
        self.assertTrue(is_tarot("0", solver.TAROT_NAME))
        self.assertTrue(is_tarot("20", solver.TAROT_NAME))

    def test_short_card(self) -> None:
        deck = solver.make_deck()
        shorts = map(solver.short_card, deck)
        cards = map(solver.parse_short_card, shorts)
        self.assertListEqual(deck, list(cards))

    def test_playable_on(self) -> None:
        cases = [
            (("5", "Coins"), ("6", "Coins"), True),
            (("5", "Coins"), ("4", "Coins"), True),
            (("5", "Coins"), ("7", "Coins"), False),
            (("5", "Coins"), ("6", "Goblets"), False),
            (("7", "Goblets"), ("6", "Goblets"), True),
            (("5", "Coins"), ("6", "Goblets"), False),
            (("0", solver.TAROT_NAME), ("1", solver.TAROT_NAME), True),
            (("21", solver.TAROT_NAME), ("20", solver.TAROT_NAME), True),
            (("21", solver.TAROT_NAME), ("0", solver.TAROT_NAME), False),
        ]

        for (c1, c2, res) in cases:
            self.assertEqual(solver.playable_on(solver.make_card(*c1), solver.make_card(*c2)), res)

    def test_take_full_sequence(self) -> None:
        cards = ["5/", "6/", "7/"]
        arr = solver.parse_cards(cards)
        arr_before = arr.copy()
        arr_before.reverse()
        self.assertListEqual(solver.take_sequence(arr), arr_before)
        self.assertListEqual(arr, [])

    def test_take_singleton_sequence(self) -> None:
        cards = ["5*", "6*", "7/"]
        arr = solver.parse_cards(cards)

        self.assertListEqual(solver.take_sequence(arr), [solver.parse_short_card("7/")])
        self.assertListEqual(arr, solver.parse_cards(["5*", "6*"]))

    def test_take_partial_sequence(self) -> None:
        cards = ["5v", "6v", "7", "8", "9"]
        arr = solver.parse_cards(cards)

        self.assertListEqual(solver.take_sequence(arr), solver.parse_cards(["9", "8", "7"]))
        self.assertListEqual(arr, solver.parse_cards(["5v", "6v"]))


    def test_first_empty(self) -> None:
        arr = [[1], [2, 3], [], [4]]
        no_emp = [[1], [2, 2], [3]]
        self.assertEqual(solver.first_empty(arr), 2)
        self.assertEqual(solver.first_empty(no_emp), None)

    def test_make_stacks(self) -> None:
        stacks = solver.make_stacks()
        self.assertEqual(len(stacks), 11)
        for i, s in enumerate(stacks):
            if i == 5:
                self.assertEqual(len(s), 0)
            else:
                self.assertEqual(len(s), 7)

    def test_empty_GameState(self) -> None:
        gs = solver.GameState([])
        self.assertEqual(len(gs.all_moves()), 0)

    def do_moves_and_checks(self, gs:solver.GameState, expected_count: Optional[int] = None) -> None:
        before = repr(gs)
        moves = gs.all_moves()
        if expected_count is not None:
            self.assertEqual(expected_count, len(moves))
        for (do_move, undo_move, _) in moves:
            rep_before = gs.state_rep()
            repr_before = repr(gs)
            do_move()
            # the move should result in a state change of some sort but rep may not change
            # because some moves/states are considered equivalent
            self.assertNotEqual(repr_before, repr(gs))
            self.assertIsNotNone(solver.first_empty(gs.stacks))
            undo_move()
            self.assertEqual(rep_before, gs.state_rep())
            self.assertEqual(repr_before, repr(gs))

        self.assertEqual(before, repr(gs))

    def confirm_trivial_solve(self, gs:solver.GameState) -> None:
        before = repr(gs)
        undo = gs.update_foundations()
        self.assertNotEqual(before, repr(gs))
        # only card is on foundations, no more moves
        self.do_moves_and_checks(gs, 0)
        self.assertTrue(gs.is_solved())
        undo()
        after = repr(gs)

        self.assertEqual(before, after)

    def test_trivial_GameState(self) -> None:
        stacks = [
            stack_of([("2", "Coins")]),
            []
        ]

        gs = solver.GameState(stacks)
        self.do_moves_and_checks(gs, 2)
        self.confirm_trivial_solve(gs)

    def test_top_stacking(self) -> None:
        stacks = [
            stack_of([("8", "Goblets")]),
            stack_of([("4", "Coins")]),
            stack_of([("5", "Coins")]),
            stack_of([("9", "Goblets")]),
        ]

        gs = solver.GameState(stacks)
        self.assertIsNone(solver.first_empty(gs.stacks))
        # each stack top can go to stash or to one other card
        self.do_moves_and_checks(gs, 8)

    def test_moves_from_stash(self) -> None:
        stacks = [
            stack_of([("2", "Coins")]),
            stack_of([("3", "Coins")]),
            [],
        ]

        gs = solver.GameState(stacks)
        gs.move_to_stash(0)

        # move from stash to first empty stack or onto 3 or move 3 to empty stack
        self.do_moves_and_checks(gs, 3)
        self.confirm_trivial_solve(gs)

    def test_complex_but_trivial_solve(self) -> None:
        stacks = [
            stack_of([(str(n), "Coins") for n in range(10, 1, -1)]),
            stack_of([(str(n), "Goblets") for n in range(10, 1, -1)]),
            stack_of([(str(n), "Thorns") for n in range(10, 1, -1)]),
            stack_of([(str(n), solver.TAROT_NAME) for n in range(15, solver.TAROT_COUNT)]),
            stack_of([(str(n), solver.TAROT_NAME) for n in range(14, -1, -1)]),
            [],
        ]

        gs = solver.GameState(stacks)
        self.confirm_trivial_solve(gs)

        gs.update_foundations()
        self.assertTrue(solver.try_solve(gs, solver.noop_output))

    def test_fast_but_nontrivial_solve(self) -> None:
        stacks = [
            stack_of([("2", "Thorns"), ("3", "Goblets"), ("3", "Coins"), ("4", "Coins")]),
            stack_of([("2", "Coins"), ("2", "Goblets"), ("3", "Thorns"), ("5", "Coins")]),
            stack_of([("4", "Thorns"), ("4", "Goblets"), ("6", "Coins")]),
            []
        ]

        gs = solver.GameState(stacks)
        gs.update_foundations()
        self.assertTrue(solver.try_solve(gs, solver.noop_output))

    def test_fast_impossible_case(self) -> None:
        stacks = [
            stack_of([("2", "Thorns"), ("3", "Thorns")]),
        ]

        gs = solver.GameState(stacks)
        gs.update_foundations()

        # without a free stack, these cannot be cleared
        self.assertFalse(solver.try_solve(gs, solver.noop_output))

    def test_blocked_stash(self) -> None:
        stacks = [
            stack_of([("2", "Thorns"), ("11", solver.TAROT_NAME)]),
        ]

        gs = solver.GameState(stacks)
        gs.move_to_stash(0)
        repr_before = repr(gs)
        gs.update_foundations()
        self.assertEqual(repr_before, repr(gs))

    def test_tarot_stash_edge_case(self) -> None:
        stacks = [
            stack_of([("0", solver.TAROT_NAME), ("1", solver.TAROT_NAME)]),
        ]

        gs = solver.GameState(stacks)
        gs.update_foundations()

        # tarot cards aren't blocked by the stash, so this _is_ solvable
        self.assertTrue(solver.try_solve(gs, solver.noop_output))

    def assertThrows(self, fn:Callable[[], None]) -> None:
        threw = False
        try:
            fn()
        except:
            threw = True
            pass

        self.assertTrue(threw)

    def test_move_to_stash_bounds_check(self) -> None:
        stacks = [
            stack_of([("2", "Thorns")]),
        ]

        gs = solver.GameState(stacks)

        self.assertThrows(lambda: gs.move_to_stash(1))

    def test_stash_occupied_check(self) -> None:
        stacks = [
            stack_of([("2", "Thorns")]),
        ]

        gs = solver.GameState(stacks)

        rep = gs.state_rep()

        gs.move_to_stash(0)

        # cannot move to occupied stash
        self.assertThrows(lambda: gs.move_to_stash(0))

        gs.pop_stash(0)

        # cannot pop unoccupied stash
        self.assertThrows(lambda: gs.pop_stash(0))

        self.assertEqual(rep, gs.state_rep())

if __name__ == "__main__":
    unittest.main()

