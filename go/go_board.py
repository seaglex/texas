from __future__ import annotations
import numpy as np
import enum
from typing import Tuple, List, Set, Iterable


Coordinate = Tuple[int, int]


class GoStone(enum.IntEnum):
    Empty = 0
    White = 1
    Black = 2
    Guard = 3

    @staticmethod
    def get_opponent(stone):
        if stone == GoStone.White:
            return GoStone.Black
        if stone == GoStone.Black:
            return GoStone.White
        raise Exception("invalid stone")

    @staticmethod
    def format(stone: GoStone):
        return {
            GoStone.Empty: ".",
            GoStone.White: "o",
            GoStone.Black: "x",
            GoStone.Guard: " ",
        }.get(stone, "?")


class GoBoardUtil(object):
    @staticmethod
    def get_empty_board(num):
        board = np.full((num + 2, num + 2), GoStone.Empty)
        board[0, :] = GoStone.Guard
        board[-1, :] = GoStone.Guard
        board[:, 0] = GoStone.Guard
        board[:, -1] = GoStone.Guard
        return board

    @staticmethod
    def neighbors(x, y):
        return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)


class BasicChain(object):
    """
    Chain: joined stones and their liberties
    """
    def __init__(self, stone: GoStone) -> type(None):
        self._stone: GoStone = stone
        self._stone_coordinates: List[Coordinate] = []
        self._liberties: Set[Coordinate] = set()
        self._oppo_neighbors: Set[BasicChain] = set()

    def append_stone(self, stone: GoStone, coordinate: Coordinate,
                     liberties: Iterable[Coordinate], oppo_neighbors: Iterable[BasicChain]) -> type(None):
        assert stone == self._stone
        self._stone_coordinates.append(coordinate)
        self._liberties.update(liberties)
        self._oppo_neighbors.update(oppo_neighbors)

    def _extend_chain(self, another: BasicChain) -> type(None):
        """
        This method is always called with append_stone() in join()
        """
        assert self._stone == another._stone
        self._stone_coordinates.extend(another._stone_coordinates)
        self._liberties.update(another._liberties)
        self._oppo_neighbors.update(another._oppo_neighbors)

    def join(self, stone: GoStone, coordinate: Coordinate,
             liberties: Iterable[Coordinate], oppo_neighbors: Iterable[BasicChain],
             other_chains: Iterable[BasicChain]
             ):
        self.append_stone(stone, coordinate, liberties, oppo_neighbors)
        for chain in other_chains:
            self._extend_chain(chain)
        self.remove_liberty(coordinate)

    def remove_liberty(self, coordinate: Coordinate) -> type(None):
        assert coordinate in self._liberties
        self._liberties.remove(coordinate)

    # for opponent
    def add_opponent(self, oppo_chain: BasicChain) -> type(None):
        self._oppo_neighbors.add(oppo_chain)

    def is_alive(self) -> bool:
        return bool(self._liberties)

    def recheck_liberties(self, board: np.array) -> type(None):
        """
        A slow implementation, for it's only needed in Atari and Atari is rare
        """
        for coord in self._stone_coordinates:
            for nx, ny in GoBoardUtil.neighbors(*coord):
                if board[nx, ny] == GoStone.Empty:
                    self._liberties.add((nx, ny))
        return

    def destroy_and_update_neighbors(self, board: np.array) -> type(None):
        for neighbor in self._oppo_neighbors:
            neighbor._oppo_neighbors.remove(self)
            neighbor.recheck_liberties(board)

    def get_coordinates(self) -> List[Coordinate]:
        return self._stone_coordinates

    def __repr__(self):
        """
        For more debugging information
        """
        if self._stone_coordinates:
            return '+'.join(["C", self._stone.name, str(self._stone_coordinates[0]), str(len(self._liberties))])
        else:
            return "+".join(["C", self._stone.name])

    @staticmethod
    def having_liberty_plus(chains: Iterable[BasicChain], coordinate: Coordinate) -> bool:
        """
        evaluate liberties of chains with 1 more stone (w/o new liberties of this stone)
        """
        for c in chains:
            if len(c._liberties) >= 2 or coordinate not in c._liberties:
                return True
        return False

    @staticmethod
    def having_liberty_minus(chains: Iterable[BasicChain], coordinate: Coordinate) -> bool:
        """
        evaluate liberties of chains with 1 more opponent stone
        """
        for c in chains:
            if len(c._liberties) >= 2 or coordinate not in c._liberties:
                return True
        return False


class GoBasicBoard(object):
    """
    Basic implementation, w/o acceleration
    Boundary: use guard stones as boundary to avoid if/else
    Chain: joined stones and their liberties
    """
    def __init__(self, num: int):
        # empty board
        self._num = num
        self._board = np.full((num + 2, num + 2), GoStone.Empty)
        self._board[0, :] = GoStone.Guard
        self._board[-1, :] = GoStone.Guard
        self._board[:, 0] = GoStone.Guard
        self._board[:, -1] = GoStone.Guard
        # their chains
        self._chains = np.full((num + 2, num + 2), None, dtype=BasicChain)

    def is_valid_move(self, pos: tuple, stone: GoStone):
        my_coord = pos
        if self._board[my_coord] != GoStone.Empty:
            return False
        opponent_stone = GoStone.get_opponent(stone)

        same_chains = set()
        oppo_chains = set()
        for nx, ny in GoBoardUtil.neighbors(*my_coord):
            neighbor = self._board[nx, ny]
            if neighbor == GoStone.Empty:
                return True
            if neighbor == stone:
                same_chains.add(self._chains[nx, ny])
            elif neighbor == opponent_stone:
                oppo_chains.add(self._chains[nx, ny])
        if same_chains:
            if BasicChain.having_liberty_plus(same_chains, my_coord):
                return True
        if not BasicChain.having_liberty_minus(oppo_chains, my_coord):
            return True
        return False

    def put_stone(self, pos: Coordinate, stone: GoStone) -> None:
        my_coord = pos
        assert self._board[my_coord] == GoStone.Empty
        opponent_stone = GoStone.get_opponent(stone)

        same_chains = set()
        oppo_chains = set()
        liberties = []
        for nx, ny in GoBoardUtil.neighbors(*my_coord):
            neighbor = self._board[nx, ny]
            if neighbor == stone:
                same_chains.add(self._chains[nx, ny])
            elif neighbor == opponent_stone:
                oppo_chains.add(self._chains[nx, ny])
            elif neighbor == GoStone.Empty:
                liberties.append((nx, ny))
        # Put the stone
        self._board[my_coord] = stone
        # 连: join the chains
        if same_chains:
            same_chains = list(same_chains)
            my_chain = same_chains[0]
            my_chain.join(stone, my_coord, liberties, oppo_chains,
                          same_chains[1:])
            for chain in same_chains[1:]:
                for coord in chain.get_coordinates():
                    self._chains[coord] = my_chain
                del chain
        else:
            my_chain = BasicChain(stone)
            my_chain.append_stone(stone, my_coord, liberties, oppo_chains)
        self._chains[my_coord] = my_chain
        # check the opponents
        if oppo_chains:
            for chain in set(oppo_chains):
                chain.remove_liberty(my_coord)
                chain.add_opponent(my_chain)
                if not chain.is_alive():
                    # Atari
                    for coord in chain.get_coordinates():
                        self._chains[coord] = None
                        self._board[coord] = GoStone.Empty
                    chain.destroy_and_update_neighbors(self._board)
                    del chain
        return

    def get_board(self):
        return self._board

    def iter_valid_moves(self, stone: GoStone):
        for x in range(1, self._num + 1):
            for y in range(1, self._num + 1):
                if self._board[x, y] == GoStone.Empty and self.is_valid_move((x, y), stone):
                    yield x, y
        return

    def num(self):
        return self._num

    def to_str(self):
        lines = []
        for x in range(self._num + 2):
            lines.append(''.join(GoStone.format(self._board[x, y]) for y in range(self._num + 2)))
        return '\n'.join(lines)
