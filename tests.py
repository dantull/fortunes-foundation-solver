import unittest
import solver

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

        self.assertEquals(short_card("5", "Thorns"), "5/")
        self.assertEquals(short_card("K", "Swords"), "Kt")
        self.assertEquals(short_card("10", "Goblets"), "10v")
        self.assertEquals(short_card("A", "Swords"), "At")
        self.assertEquals(short_card("8", "Coins"), "8*")
        self.assertEquals(short_card("0", solver.TAROT_NAME), "0")
        self.assertEquals(short_card("20", solver.TAROT_NAME), "20")

if __name__ == "__main__":
    unittest.main()
