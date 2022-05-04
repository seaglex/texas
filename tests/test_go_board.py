import unittest

from go.go_board import GoBasicBoard, GoStone


class GoBoardUnitTest(unittest.TestCase):
    @staticmethod
    def test_atari():
        board = GoBasicBoard(9)
        beg = 1
        for n in range(beg, beg + 3):
            board.put_stone((n, beg + 1), GoStone.White)
        for n in range(beg + 1, beg + 3):
            board.put_stone((n, beg), GoStone.White)
        for n in range(beg, beg + 4):
            board.put_stone((n, beg + 2), GoStone.Black)
        board.put_stone((beg + 3, beg + 0), GoStone.Black)
        board.put_stone((beg + 3, beg + 1), GoStone.Black)
        board.print()
        assert board.is_valid_move((beg + 0, beg + 0), GoStone.Black)
        board.put_stone((beg + 0, beg + 0), GoStone.Black)
        board.print()
        raw_board = board.get_board()
        assert (raw_board == GoStone.White).sum() == 0
        assert (raw_board == GoStone.Black).sum() == 7
