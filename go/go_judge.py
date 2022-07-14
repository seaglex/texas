import numpy as np
from collections import deque
from typing import List, Tuple, Final

from .go_basic_board import GoStone, GoBasicBoardUtil


NUM_COMPENSATIONS: Final[List[Tuple[int, float]]] = [
    (9, 2.75),
    (13, 2.75),
    (19, 3.75),
]


class GoJudge(object):
    """
    假设已经下到最后，不需要推理能力，死棋已被提掉
    - 空地同时是黑白的气，各占1/2
    - 简单连通域算法（图广度搜索）
    """
    def count_black(self, board):
        num = len(board) - 2
        markers = np.zeros((num + 2, num + 2))
        black_cnt = 0
        for row in range(1, num + 1):
            for col in range(1, num + 1):
                if markers[row][col] != 0:
                    continue
                markers[row][col] = 1
                if board[row][col] == GoStone.White:
                    continue
                if board[row][col] == GoStone.Black:
                    black_cnt += 1
                    continue
                # empty
                black_cnt += GoJudge._count_empty_black(board, row, col, markers)
        return black_cnt

    @staticmethod
    def _count_empty_black(board, row: int, col: int, markers):
        assert board[row][col] == GoStone.Empty
        unhandled = deque([])
        is_black = False
        is_white = False
        unhandled.append((row, col))
        cnt = 1
        while len(unhandled) > 0:
            coord = unhandled.popleft()
            for nx, ny in GoBasicBoardUtil.neighbors(*coord):
                if board[nx][ny] == GoStone.Black:
                    is_black = True
                elif board[nx][ny] == GoStone.White:
                    is_white = True
                elif board[nx][ny] == GoStone.Empty and markers[nx][ny] == 0:
                    unhandled.append((nx, ny))
                    cnt += 1
                    markers[nx][ny] = 1
        if is_black and is_white:
            return cnt * 0.5
        if is_black:
            return cnt
        return 0

    def get_black_win(self, board):
        num = len(board)
        compensation = NUM_COMPENSATIONS[-1][1]
        for n, comp in NUM_COMPENSATIONS:
            if num <= n:
                compensation = comp
                break
        cnt = self.count_black(board)

        if cnt - compensation > num * num / 2:
            return 1
        elif cnt - compensation < num * num / 2:
            return -1
        return 0
