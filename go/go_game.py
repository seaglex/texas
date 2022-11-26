from __future__ import annotations
from typing import List, Any
import copy

from .go_common import GoStone, IGoBoard, TStone
from .go_judge import GoJudge
from games.common import IGameState


Action = Any


class GoState(IGameState):
    def __init__(self, board: IGoBoard, player_index=0, stone=GoStone.Black):
        self._player_index = player_index
        self._stone = stone
        self._board = board
        self._pass_cnt = 0
        self._move_cnt = 0
        # cache
        self._max_move_count = board.num() ** 2 * 2
        self._pass_action = board.get_pass_move()

    def get_current_player(self) -> int:
        return self._player_index

    def get_current_stone(self) -> TStone:
        return self._stone

    def get_move_count(self) -> int:
        return self._move_cnt

    def get_valid_actions(self) -> List[Action]:
        return self._board.iter_valid_moves(self._stone)

    def is_valid_action(self, action):
        return self._board.is_valid_move(action, self._stone)

    def apply_action(self, action: Action) -> type(None):
        self._move_cnt += 1
        if action == self._pass_action:  # pass
            self._pass_cnt += 1
            self._player_index = 1 - self._player_index
            self._stone = GoStone.get_opponent(self._stone)
            return
        self._pass_cnt = 0
        self._board.put_stone(action, self._stone)

        self._player_index = 1 - self._player_index
        self._stone = GoStone.get_opponent(self._stone)
        return

    def is_terminal(self) -> bool:
        return self._pass_cnt >= 2 or self._move_cnt >= self._max_move_count

    def get_rewards(self) -> List[float]:
        judge = GoJudge()
        win = judge.get_black_win(self._board.get_board())
        return [win,  -win]

    @staticmethod
    def is_good_enough(score) -> bool:
        return score > 0

    def clone(self) -> GoState:
        return copy.deepcopy(self)

    def to_str(self) -> str:
        return self._board.to_str()
