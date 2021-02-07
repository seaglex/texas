import unittest

from texas import poker
from texas import direct_calc
from texas import monte_carlo
from texas.judge import TexasJudge, TexasLevel


class SimulatorTestCase(unittest.TestCase):
    def test_get_straight_flush_pr(self):
        judge = TexasJudge()
        cards = [(poker.PokerKind.heart, 4), (poker.PokerKind.spade, 5)]
        community_cards = [(poker.PokerKind.diamond, 6), (poker.PokerKind.club, 7),]

        calc = direct_calc.ApproxCalc()

        simulator = monte_carlo.Simulator(judge)
        num = 10000
        straight_flush_prs = calc.get_straight_flush_prs(cards + community_cards)
        straight_flush_pr = sum(p[0] for p in straight_flush_prs)
        straight_prs = calc.get_straight_prs(cards + community_cards)
        straight_pr = sum(p[0] for p in straight_prs)
        flush_prs = calc.get_flush_prs(cards + community_cards)
        flush_pr = sum(p[0] for p in flush_prs)

        level_counts = simulator.get_level_counts(cards, community_cards, trial_num=num)
        print(TexasLevel.straight_flush,
              straight_flush_pr,
              level_counts.get(TexasLevel.straight_flush, 0) / num
              )
        print(TexasLevel.straight,
              straight_pr,
              level_counts.get(TexasLevel.straight, 0) / num
              )
        print(TexasLevel.flush,
              flush_pr,
              level_counts.get(TexasLevel.flush, 0) / num
              )


if __name__ == "__main__":
    unittest.main()
