import unittest

from texas.judge import TexasJudge, TexasLevel


class TexasJudgeTestCase(unittest.TestCase):
    def setUp(self):
        self.cards_levels = [
            ([(1, 14), (1, 12), (1, 11), (1, 10), (1, 9), (1, 8)], TexasLevel.straight_flush),
            ([(1, 14), (1, 13), (1, 12), (1, 11), (1, 10), (1, 9)], TexasLevel.straight_flush),
            ([(1, 9), (2, 9), (3, 9), (4, 9), (1, 14), (2, 10)], TexasLevel.four),
            ([(1, 9), (2, 9), (3, 9), (1, 6), (1, 5), (1, 4), (1, 2), (4, 2)], TexasLevel.full_house),
            ([(1, 9), (1, 6), (1, 5), (1, 3), (1, 2), (2, 9), (3, 7)], TexasLevel.flush),
            ([(1, 14), (2, 13), (3, 12), (1, 11), (1, 10), (1, 7)], TexasLevel.straight),
            ([(1, 9), (2, 9), (3, 9), (1, 7), (1, 8), (1, 10), (2, 2)], TexasLevel.three),
            ([(1, 9), (2, 9), (3, 8), (4, 8), (1, 7), (1, 10), (2, 2)], TexasLevel.two_pairs),
            ([(1, 9), (2, 9), (3, 8), (4, 12), (1, 7), (1, 4), (2, 2)], TexasLevel.pair),
            ([(1, 14), (2, 9), (3, 12), (4, 5), (1, 7), (1, 10), (2, 2)], TexasLevel.high_card),
        ]

    def test_level_judgement(self):
        judge = TexasJudge()
        for cards, level in self.cards_levels:
            # random.shuffle(cards)
            best_level, best_suit = judge._get_level_suit(cards)
            self.assertEqual(level, best_level, cards)

    def test_arg_max(self):
        judge = TexasJudge()
        indexes = judge.argmax([x[0] for x in self.cards_levels])
        self.assertEqual(indexes, [1])

if __name__ == "__main__":
    unittest.main()
