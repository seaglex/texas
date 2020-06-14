import unittest
import random
from texas import monte_carlo
from texas import poker
from texas.judge import TexasJudge


class SimulatorTestCase(unittest.TestCase):
    def test_get_pr(self):
        judge = TexasJudge()
        simulator = monte_carlo.Simulator(judge)
        random.seed(0)
        pr = simulator.get_pr([(poker.PokerKind.heart, 2), (poker.PokerKind.diamond, 3)], trial_num=10000)
        self.assertTrue(pr <= 0.01)
        pr = simulator.get_pr(
            [(poker.PokerKind.heart, poker.PokerDigit.A), (poker.PokerKind.diamond, poker.PokerDigit.A)]
        )
        self.assertTrue(pr >= 0.90)
        pr = simulator.get_pr([(poker.PokerKind.heart, poker.PokerDigit.A), (poker.PokerKind.heart, 13)])
        self.assertTrue(pr >= 0.55)


if __name__ == "__main__":
    unittest.main()
