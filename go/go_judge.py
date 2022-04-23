import numpy as np
from collections import deque

from .go_board import GoStone


NUM_COMPENSATIONS = {
    9: 2.75,
    13: 2.75,
    19: 3.74,
}


class GoJudge(object):
    """
    假设已经下到最后，不需要推理能力，死棋已被提掉
    - 空地同时是黑白的气，各占1/2
    - 简单连通域算法（图广度搜索）
    """
    def count_black(self, board):
        N = len(board)
        markers = np.zeros((N, N))
        black_cnt = 0
        for row in range(N):
            for col in range(N):
                if markers[row][col] != 0:
                    continue
                markers[row][col] = 1
                if board[row][col] == GoStone.White:
                    continue
                if board[row][col] == GoStone.Black:
                    black_cnt += 1
                    continue
                # empty
                black_cnt += self._count_empty_black(board, row, col, markers)
        return black_cnt

    def _count_empty_black(self, board, row, col, markers):
        assert board[row][col] == GoStone.Empty
        N = len(board)
        unhandled = deque([])
        is_black = False
        is_white = False
        unhandled.append((row, col))
        cnt = 1
        while len(unhandled) > 0:
            y, x = unhandled.popleft()
            if y > 0:
                if board[y - 1][x] == GoStone.Black:
                    is_black = True
                elif board[y - 1][x] == GoStone.White:
                    is_white = True
                elif markers[y - 1][x] == 0:
                    unhandled.append((y - 1, x))
                    cnt += 1
                    markers[y - 1][x] = 1
            if y < N - 1:
                if board[y + 1][x] == GoStone.Black:
                    is_black = True
                elif board[y + 1][x] == GoStone.White:
                    is_white = True
                elif markers[y + 1][x] == 0:
                    unhandled.append((y + 1, x))
                    cnt += 1
                    markers[y + 1][x] = 1
            if x > 0:
                if board[y][x - 1] == GoStone.Black:
                    is_black = True
                elif board[y][x - 1] == GoStone.White:
                    is_white = True
                elif markers[y][x - 1] == 0:
                    unhandled.append((y, x - 1))
                    cnt += 1
                    markers[y][x - 1] = 1
            if x < N - 1:
                if board[y][x + 1] == GoStone.Black:
                    is_black = True
                elif board[y][x + 1] == GoStone.White:
                    is_white = True
                elif markers[y][x + 1] == 0:
                    unhandled.append((y, x + 1))
                    cnt += 1
                    markers[y][x + 1] = 1
        if is_black and is_white:
            return cnt * 0.5
        if is_black:
            return cnt
        return 0
