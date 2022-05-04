"""
Tic-Tac-Toe
It's simple enough to test random rollouts
"""
import numpy as np
from typing import Final, List, Tuple
import copy

from search.mcts import IGameState
from .common import IAgent


Action = Tuple[int, int]


class TicTacToeBoard(object):
    NUM: Final[int] = 3

    def __init__(self):
        self.board = np.full((TicTacToeBoard.NUM, TicTacToeBoard.NUM), '.')

    def is_successful(self, action: Action, mark: str) -> bool:
        x, y = action
        if all(self.board[x, :] == mark) or all(self.board[:, y] == mark):
            return True
        if x == y and all(self.board.diagonal() == mark):
            return True
        if x + y == TicTacToeBoard.NUM - 1 and all(np.fliplr(self.board).diagonal() == mark):
            return True
        return False

    def to_str(self):
        return '\n'.join(''.join(x for x in row) for row in self.board)


class TicTacToeState(TicTacToeBoard, IGameState):
    def __init__(self):
        super(TicTacToeState, self).__init__()
        self._player = 0  # player 0: x, player 1: o
        self._is_terminal = False
        self._move_count = 0
        self._player0_score = 0.0

    def get_current_player(self) -> int:
        return self._player

    def get_valid_actions(self) -> List[Action]:
        if self._is_terminal:
            return []
        actions = []
        for x in range(TicTacToeBoard.NUM):
            for y in range(TicTacToeBoard.NUM):
                if self.board[x, y] == '.':
                    actions.append((x, y))
        return actions

    def apply_action(self, action: Action) -> type(None):
        assert self.board[action] == '.'
        mark = 'x' if self._player == 0 else 'o'
        self.board[action] = mark
        if self.is_successful(action, mark):
            self._is_terminal = True
            self._player0_score = 1.0 if self._player == 0 else -1.0
        self._player = 1 - self._player
        self._move_count += 1
        if self._move_count >= TicTacToeBoard.NUM ** 2:
            self._is_terminal = True

    def is_terminal(self) -> bool:
        return self._is_terminal

    def get_rewards(self) -> List[float]:
        return [self._player0_score, -self._player0_score]

    @staticmethod
    def is_good_enough(score) -> bool:
        return score > 0.0

    def clone(self) -> IGameState:
        return copy.deepcopy(self)

    def to_str(self) -> str:
        return super(TicTacToeState, self).to_str()


class HumanAgent(IAgent):
    def __init__(self, player_index: int, state: IGameState):
        self._player_index = player_index
        self._state = state

    def get_name(self) -> str:
        return "Human-" + str(self._player_index)

    def set_index(self, index: int) -> type(None):
        self._player_index = index

    def step(self) -> Action:
        coords = list(int(x) for x in input("input x,y ").split(","))
        action = coords[0], coords[1]
        self._state.apply_action(action)
        return action

    def inform_action(self, other_player: int, action: Action) -> type(None):
        assert self._player_index != other_player
        self._state.apply_action(action)
