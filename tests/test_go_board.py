import unittest

from go.go_board import GoBasicBoard, GoStone


class GoBoardUnitTest(unittest.TestCase):
    @staticmethod
    def test_atari():
        board = GoBasicBoard(9)
        for n in range(0, 3):
            board.put_stone((n, 1), GoStone.White)
        for n in range(1, 3):
            board.put_stone((n, 0), GoStone.White)
        for n in range(0, 4):
            board.put_stone((n, 2), GoStone.Black)
        board.put_stone((3, 0), GoStone.Black)
        board.put_stone((3, 1), GoStone.Black)
        board.print()
        assert board.is_valid_move((0, 0), GoStone.Black)
        board.put_stone((0, 0), GoStone.Black)
        board.print()
        raw_board = board.get_raw_board()
        assert (raw_board == GoStone.White).sum() == 0
        assert (raw_board == GoStone.Black).sum() == 7
