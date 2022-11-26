import unittest

from texas import poker
from texas import direct_calc
from texas import monte_carlo
from texas.judge import TexasJudge, TexasLevel


class SimulatorTestCase(unittest.TestCase):
    def test_manual_cases(self):
        cases = [
            [
                [(poker.PokerSymbol.heart, 4), (poker.PokerSymbol.spade, 4)],
                [(poker.PokerSymbol.diamond, 4), ],
            ],
            [
                [(poker.PokerSymbol.heart, 2), (poker.PokerSymbol.heart, 3)],
                [(poker.PokerSymbol.heart, 4), ],
            ],
            [
                [(poker.PokerSymbol.heart, 2), (poker.PokerSymbol.heart, 3)],
                [(poker.PokerSymbol.heart, 4), (poker.PokerSymbol.heart, 5), ],
            ],
        ]
        with open("test_approx.log", "w") as fout:
            for case in cases:
                level_prs = self._get_level_prs(case[0], case[1])
                for card in case[0] + case[1]:
                    print(poker.PokerCard.short_format(*card), file=fout, end=" ")
                print(file=fout, end="\n")
                for level, pr, simulated_pr in level_prs:
                    print(level, pr, simulated_pr, file=fout, sep="\t")
                print(flush=True)

    def _get_level_prs(self, cards, community_cards):
        judge = TexasJudge()
        simulator = monte_carlo.Simulator(judge)
        calc = direct_calc.ApproxCalc()

        num = 10000
        level_counts = simulator.get_level_counts(cards, community_cards, trial_num=num)
        level_prs = calc.get_level_prs(cards + community_cards)

        prs = []
        for level in list(TexasLevel):
            prs.append(
                (level.name, level_counts.get(level, 0) / num, level_prs.get(level, 0.0))
            )
        return prs

    def test_straight_flush_pr(self):
        calc = direct_calc.ApproxCalc()
        pr = calc.get_straight_flush_pr(
            [(1, 2), (1, 5), (1, 6), (1, 10)],
        )
        assert pr > 0

        pr = calc.get_straight_flush_pr(
            [(1, poker.PokerDigit.A), (1, 2)],
        )
        assert pr > 0


if __name__ == "__main__":
    unittest.main()
