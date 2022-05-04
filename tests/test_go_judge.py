import unittest

from go.go_judge import GoJudge
from go.go_board import GoStone, GoBoardUtil


class GoJudgeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.empty_board = GoBoardUtil.get_empty_board(9)
        simple_board = GoBoardUtil.get_empty_board(9)
        beg = 1
        for n in range(beg, beg + 9):
            simple_board[beg + 3][n] = GoStone.Black
            simple_board[beg + 6][n] = GoStone.Black
            simple_board[beg + 7][n] = GoStone.White
        simple_board[beg + 8][beg + 1] = GoStone.White
        self.simple_board = simple_board

    def test_emtpy(self):
        judge = GoJudge()
        self.assertEqual(judge.count_black(self.empty_board), 0, "emtpy-board")

    def test_manual1(self):
        judge = GoJudge()
        self.assertEqual(judge.count_black(self.simple_board), 7 * 9, "7-rows")
