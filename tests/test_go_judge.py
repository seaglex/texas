import unittest
import numpy as np

from go.go_judge import GoJudge, GoPiece


class GoJudgeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        empty_board = np.ones((9, 9))
        empty_board *= GoPiece.Empty
        self.empty_board = empty_board

        row_board = np.ones((9, 9)) * GoPiece.Empty
        for n in range(9):
            row_board[3][n] = GoPiece.Black
            row_board[6][n] = GoPiece.Black
            row_board[7][n] = GoPiece.White
        row_board[8][1] = GoPiece.White
        self.row_board = row_board

    def test_emtpy(self):
        judge = GoJudge()
        self.assertEqual(judge.count_black(self.empty_board), 0, "emtpy-board")

    def test_manual1(self):
        judge = GoJudge()
        self.assertEqual(judge.count_black(self.row_board), 7 * 9, "7-rows")
