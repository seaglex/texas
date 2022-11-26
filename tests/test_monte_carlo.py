import unittest
from texas import monte_carlo
from texas import poker
from texas.judge import TexasJudge


class SimulatorTestCase(unittest.TestCase):
    def test_get_pr(self):
        judge = TexasJudge()
        simulator = monte_carlo.Simulator(judge)
        pr = simulator.get_pr([(poker.PokerSymbol.heart, 2), (poker.PokerSymbol.diamond, 3)], trial_num=10000)
        self.assertTrue(pr <= 0.35)
        pr = simulator.get_pr(
            [(poker.PokerSymbol.heart, poker.PokerDigit.A), (poker.PokerSymbol.diamond, poker.PokerDigit.A)],
        )
        self.assertTrue(pr >= 0.80)
        pr = simulator.get_pr([(poker.PokerSymbol.heart, poker.PokerDigit.A), (poker.PokerSymbol.heart, 13)])
        self.assertTrue(pr >= 0.60)


if __name__ == "__main__":
    unittest.main()
