import unittest
from texas import texas_games
from texas.judge import TexasJudge


class TexasGameTestCase(unittest.TestCase):
    def test_dividing_money(self):
        judge = TexasJudge()
        game = texas_games.NoLimitTexasGame(judge)
        amounts = game._divide_the_money(500, [300, None, None, None], [0, 0, 1, 2])
        self.assertEqual(list(amounts), [150, 350, 0, 0])
        amounts = game._divide_the_money(500, [300, 400, 200, None], [0, 0, 1, 1])
        self.assertEqual(list(amounts), [150, 250, 0, 100])
