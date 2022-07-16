from __future__ import annotations
import numpy as np
from typing import Any, Tuple, List


Coordinate = Tuple[int, int]


T_Stone = int


class GoStone(object):
    """
    Enum is slow(copy, storing), use int directly in the board
    """
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
    def format(stone):
        return {
            GoStone.Empty: ".",
            GoStone.White: "o",
            GoStone.Black: "x",
            GoStone.Guard: " ",
        }.get(stone, "?")

    @staticmethod
    def get_name(stone):
        return {
            GoStone.Empty: "Empty",
            GoStone.White: "White",
            GoStone.Black: "Black",
            GoStone.Guard: "Guard",
        }.get(stone, "Unknown")


class IGoBoard(object):
    def is_valid_move(self, pos: Any, stone: T_Stone) -> bool:
        raise NotImplementedError()

    def put_stone(self, pos: Any, stone: T_Stone) -> None:
        raise NotImplementedError()

    def iter_valid_moves(self, stone: T_Stone) -> List[Any]:
        raise NotImplementedError()

    def get_pass_move(self) -> Any:
        raise NotImplementedError()

    def get_board(self) -> np.array:
        raise NotImplementedError()

    def num(self) -> int:
        raise NotImplementedError()

    def to_str(self) -> str:
        raise NotImplementedError()

    # testing methods
    def check_consistence(self) -> (bool, str):
        raise NotImplementedError()

    def put_stone_by_coordinate(self, coordinate: Coordinate, stone: T_Stone):
        raise NotImplementedError()

    def is_valid_move_by_coordinate(self, coordinate: Coordinate, stone: T_Stone) -> bool:
        raise NotImplementedError()
