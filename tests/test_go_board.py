import unittest
import numpy as np

from go.go_common import GoStone, IGoBoard
from go.go_basic_board import GoBasicBoard
from go.go_fast_board import GoFastBoard


class GoBoardUnitTest(unittest.TestCase):
    def _test_atari(self, board: IGoBoard):
        beg = 1
        for n in range(beg, beg + 3):
            board.put_stone_by_coordinate((n, beg + 1), GoStone.White)
        for n in range(beg + 1, beg + 3):
            board.put_stone_by_coordinate((n, beg), GoStone.White)
        for n in range(beg, beg + 4):
            board.put_stone_by_coordinate((n, beg + 2), GoStone.Black)
        board.put_stone_by_coordinate((beg + 3, beg + 0), GoStone.Black)
        board.put_stone_by_coordinate((beg + 3, beg + 1), GoStone.Black)
        print(board.to_str())
        self.assertTrue(board.is_valid_move_by_coordinate((beg + 0, beg + 0), GoStone.Black))
        board.put_stone_by_coordinate((beg + 0, beg + 0), GoStone.Black)
        print(board.to_str())
        raw_board = board.get_board()
        self.assertEqual((raw_board == GoStone.White).sum(), 0)
        self.assertEqual((raw_board == GoStone.Black).sum(), 7)

    def test_atari(self):
        self._test_atari(GoFastBoard(9))
        self._test_atari(GoBasicBoard(9))

    def test_2_boards(self):
        src_board = GoBasicBoard(9)
        dst_board = GoFastBoard(9)
        stone = GoStone.Black
        rng = np.random.RandomState()
        for itr in range(9 * 9 * 2):
            src_valid_actions = list(src_board.iter_valid_moves(stone))
            dst_valid_actions = list(dst_board.iter_valid_moves(stone))
            self.assertEqual(len(src_valid_actions), len(dst_valid_actions), "test-%d" % itr)
            if not src_valid_actions and not dst_valid_actions:
                break
            n = rng.randint(0, len(src_valid_actions))
            src_board.put_stone(src_valid_actions[n], stone)
            dst_board.put_stone(dst_valid_actions[n], stone)
            stone = GoStone.get_opponent(stone)
