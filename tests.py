import unittest
import solver

def stack_of(cards):
    return list(map(lambda c: solver.make_card(*c), cards))

class TestCardCreation(unittest.TestCase):
    def test_make_card(self):
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

    def test_make_deck(self):
        deck = solver.make_deck()
        self.assertEqual(70, len(deck))

    def test_short_card(self):
        def short_card(r, s):
            return solver.short_card(solver.make_card(r, s))

        self.assertEqual(short_card("5", "Thorns"), "5/")
        self.assertEqual(short_card("K", "Swords"), "Kt")
        self.assertEqual(short_card("10", "Goblets"), "10v")
        self.assertEqual(short_card("A", "Swords"), "At")
        self.assertEqual(short_card("8", "Coins"), "8*")
        self.assertEqual(short_card("0", solver.TAROT_NAME), "0")
        self.assertEqual(short_card("20", solver.TAROT_NAME), "20")

    def test_playable_on(self):
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

    def test_first_empty(self):
        arr = [[1], [2, 3], [], [4]]
        no_emp = [[1], [2, 2], [3]]
        self.assertEqual(solver.first_empty(arr), 2)
        self.assertEqual(solver.first_empty(no_emp), None)

    def test_make_stacks(self):
        stacks = solver.make_stacks()
        self.assertEqual(len(stacks), 11)
        for i, s in enumerate(stacks):
            if i == 5:
                self.assertEqual(len(s), 0)
            else:
                self.assertEqual(len(s), 7)

    def test_empty_GameState(self):
        gs = solver.GameState([])
        self.assertEqual(len(gs.all_moves()), 0)

    def test_trivial_GameState(self):
        stacks = [
            stack_of([("2", "Coins")]),
            []
        ]

        gs = solver.GameState(stacks)
        moves = gs.all_moves()
        self.assertEqual(len(moves), 2)

if __name__ == "__main__":
    unittest.main()
