"""
Fast board
1. 使用int而非(x, y)表示位置
2. 使用pseudo liberty（重复计算），而非实际liberty
3. 使用环来表示chain，而非set
4. empty单独成环
"""
from __future__ import annotations
import numpy as np
from typing import List, Iterable

from .go_common import GoStone, IGoBoard, Coordinate, T_Stone


BoardIndex = int


GO_STONE_EMPTY = GoStone.Empty


class FastChainStat(object):
    """
    Chain统计信息
    pseudo liberties: 各stone的liberty单独计算
    empty: 和谁都不想连，包括empty
    """
    def __init__(self, id_=0):
        self.id_ = id_
        self.num_stones = 1
        self.num_pseudo_liberties = 0
        self._pos_sum = 0
        self._pos_square_sum = 0

    def in_atari(self):
        return self._pos_sum ** 2 == self._pos_square_sum * self.num_pseudo_liberties

    def add_liberty(self, index):
        self.num_pseudo_liberties += 1
        self._pos_sum += index
        self._pos_square_sum += index ** 2

    def remove_liberty(self, index):
        self.num_pseudo_liberties -= 1
        self._pos_sum -= index
        self._pos_square_sum -= index ** 2

    def join(self, another: FastChainStat):
        self.num_stones += another.num_stones
        self.num_pseudo_liberties += another.num_pseudo_liberties
        self._pos_sum += another._pos_sum
        self._pos_square_sum += another._pos_square_sum

    def __repr__(self):
        return f"{self.id_}-{self.num_stones}/{self.num_pseudo_liberties}/{self.in_atari()}"


class GoFastBoard(IGoBoard):
    """
    chain_next: 形成一个环
    chain_head: 统计信息，FastChainStat
    ko is ignored（全局同型没有禁止）
    """
    PASS_INDEX = 0

    def __init__(self, num: int):
        self._num = num + 2  # 包含guard
        board_size = self._num ** 2
        self._board = [GO_STONE_EMPTY] * board_size
        self._chain_next = [0] * board_size
        # 一条chain的chain-head指向同一处
        self._chain_head: List[FastChainStat] = [None] * board_size
        self._init_guard()
        self._init_chain()
        self._board_indexes: List[BoardIndex] = []
        for index in self._iter_indexes():
            self._board_indexes.append(index)

    def _init_guard(self):
        self._board[:self._num] = [GoStone.Guard] * self._num
        self._board[-self._num:] = [GoStone.Guard] * self._num
        self._board[0:self._num**2:self._num] = [GoStone.Guard] * self._num
        self._board[self._num-1:self._num**2:self._num] = [GoStone.Guard] * self._num

    def _init_chain(self):
        for index in self._iter_indexes():
            self._chain_head[index] = self._get_emtpy_chain_stat(index)
            self._chain_next[index] = index
        # side chain
        # 选择none，就要判断guard
        # 选择chain，省去判断guard
        side_chain_head = FastChainStat(0)
        side_chain_head.num_stones = (self._num - 1) * 4
        side_chain_head.num_pseudo_liberties = side_chain_head.num_stones
        self._chain_head[:self._num] = [side_chain_head] * self._num
        self._chain_head[-self._num:] = [side_chain_head] * self._num
        self._chain_head[0:self._num**2:self._num] = [side_chain_head] * self._num
        self._chain_head[self._num-1:self._num**2:self._num] = [side_chain_head] * self._num
        return

    def _get_emtpy_chain_stat(self, index: BoardIndex) -> FastChainStat:
        chain_head = FastChainStat(index)
        for n in self._neighbors(index):
            if self._board[n] == GO_STONE_EMPTY:
                chain_head.add_liberty(n)
        return chain_head

    def _neighbors(self, index) -> Iterable[BoardIndex]:
        yield index - self._num
        yield index - 1
        yield index + 1
        yield index + self._num

    def _iter_indexes(self) -> Iterable[BoardIndex]:
        index = self._num + 1
        for row in range(self._num - 2):
            for col in range(self._num - 2):
                yield index
                index += 1
            index += 2
        return

    def _get_index(self, pos: Coordinate) -> BoardIndex:
        return pos[0] * self._num + pos[1]

    def iter_valid_moves(self, stone: T_Stone) -> List[BoardIndex]:
        # Warning: NOT a good design, just to reduce time
        # cache _iter_indexes()
        # use const GO_STONE_EMPTY instead of GoStone.Empty
        actions = []
        for index in self._board_indexes:
            if self._board[index] == GO_STONE_EMPTY and self.is_valid_move(index, stone):
                actions.append(index)
        actions.append(GoFastBoard.PASS_INDEX)
        return actions

    def get_pass_move(self) -> BoardIndex:
        return GoFastBoard.PASS_INDEX

    def is_valid_move(self, index: BoardIndex, stone: T_Stone) -> bool:
        """
        Pass is not included
        :param index:
        :param stone:
        :return:
        """
        if index == GoFastBoard.PASS_INDEX:
            return True
        if self._board[index] != GO_STONE_EMPTY:
            return False
        if self._chain_head[index].num_pseudo_liberties > 0:
            return True
        oppo_stone = GoStone.get_opponent(stone)
        for n in self._neighbors(index):
            if self._board[n] == stone and not self._chain_head[n].in_atari():
                return True
            if self._board[n] == oppo_stone and self._chain_head[n].in_atari():
                return True
        return False

    def put_stone(self, index: BoardIndex, stone: T_Stone) -> None:
        if index == GoFastBoard.PASS_INDEX:
            return
        assert self._board[index] == GO_STONE_EMPTY
        self._join_chains(index, stone)
        self._remove_neighbor_liberties(index)
        self._capture_dead_chains(index, stone)
        return

    def _join_chains(self, index: BoardIndex, stone: T_Stone) -> None:
        largest_chain_size = 0
        largest_chain_head = None
        largest_chain_index = 0
        for n in self._neighbors(index):
            if self._board[n] != stone:
                continue
            if self._chain_head[n].num_stones > largest_chain_size:
                largest_chain_head = self._chain_head[n]
                largest_chain_size = largest_chain_head.num_stones
                largest_chain_index = n
        if largest_chain_size == 0:
            # use the empty chain-head
            self._board[index] = stone
            return
        for n in self._neighbors(index):
            if self._board[n] != stone:
                continue
            if self._chain_head[n] == largest_chain_head:
                continue
            largest_chain_head.join(self._chain_head[n])
            # update chain head
            self._chain_head[n] = largest_chain_head
            cur = self._chain_next[n]
            while cur != n:
                self._chain_head[cur] = largest_chain_head
                cur = self._chain_next[cur]
            # link chains
            (self._chain_next[largest_chain_index], self._chain_next[n]) = (
                self._chain_next[n], self._chain_next[largest_chain_index]
            )
        # join the stone
        self._chain_next[index] = self._chain_next[largest_chain_index]
        self._chain_next[largest_chain_index] = index
        largest_chain_head.join(self._chain_head[index])
        self._chain_head[index] = largest_chain_head
        self._board[index] = stone

    def _remove_neighbor_liberties(self, index: BoardIndex):
        # remove liberties from all neighbors, including empty
        for n in self._neighbors(index):
            self._chain_head[n].remove_liberty(index)
        return

    def _capture_dead_chains(self, index: BoardIndex, stone: T_Stone):
        oppo_stone = GoStone.get_opponent(stone)
        for n in self._neighbors(index):
            if self._board[n] != oppo_stone or self._chain_head[n].num_pseudo_liberties > 0:
                continue
            self._remove_chain(n)
        return

    def _remove_chain(self, index: BoardIndex):
        chain_head = self._chain_head[index]
        cur = index
        while True:
            self._board[cur] = GO_STONE_EMPTY
            for n in self._neighbors(cur):
                if self._chain_head[n] == chain_head:
                    continue
                self._chain_head[n].add_liberty(cur)
            self._chain_head[cur] = self._get_emtpy_chain_stat(cur)
            tmp = self._chain_next[cur]
            self._chain_next[cur] = cur
            cur = tmp
            if cur == index:
                break
        return

    def get_board(self) -> np.array:
        return np.array(self._board).reshape((self._num, self._num))

    def num(self) -> int:
        return self._num - 2

    def to_str(self) -> str:
        lines = []
        base = 0
        for x in range(self._num):
            lines.append(' '.join(GoStone.format(s) for s in self._board[base: base + self._num]))
            base += self._num
        return '\n'.join(lines)

    def check_consistence(self) -> (bool, str):
        return self._check_chain()

    def _check_chain(self) -> (bool, str):
        """
        For debugging/testing
        check whether the chain-stats is correct
        :return:
        """
        checked_indexes = set()
        for index in self._iter_indexes():
            if index in checked_indexes:
                continue
            chain_head = self._chain_head[index]
            if chain_head.num_pseudo_liberties == 0 and self._board[index] != GO_STONE_EMPTY:
                return False, "Chain({0}) w/o liberties".format(index)
            cur = index
            chain_len = 0
            chain_pseudo_liberties = 0
            liberties = set()
            while True:
                if self._chain_head[cur] != chain_head:
                    return False, "Chain heads diverge {0}/{1}".format(index, cur)
                chain_len += 1
                for n in self._neighbors(cur):
                    if self._board[n] == GO_STONE_EMPTY:
                        chain_pseudo_liberties += 1
                        liberties.add(n)
                checked_indexes.add(cur)
                cur = self._chain_next[cur]
                if cur == index:
                    break
            if self._board[index] != GO_STONE_EMPTY and ((len(liberties) == 1) ^ (chain_head.in_atari())):
                return False, "Chain({0}) wrong atari state".format(index)
            if chain_len != chain_head.num_stones:
                return False, "Chain({0}) stones {1}, expecting {2}".format(index, chain_len, chain_head.num_stones)
            if chain_pseudo_liberties != chain_head.num_pseudo_liberties:
                return False, "Chain({0}) pseudo liberties {1}, expecting {2}".format(
                    index, chain_pseudo_liberties, chain_head.num_pseudo_liberties
                )
        return True, ""

    def put_stone_by_coordinate(self, coordinate: Coordinate, stone: T_Stone) -> None:
        self.put_stone(self._get_index(coordinate), stone)

    def is_valid_move_by_coordinate(self, coordinate: Coordinate, stone: T_Stone) -> bool:
        return self.is_valid_move(self._get_index(coordinate), stone)
