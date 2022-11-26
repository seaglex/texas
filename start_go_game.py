import argparse
from typing import Any, Optional
import numpy as np
import sys

from games.simple_impl import MctsAgent, SequentialGame, RandomAgent, HumanAgent
from games.common import IActionConverter, ReverseActionConverter
from go.manual_agents import SimpleAgentV1
from go.go_common import Coordinate
from go.go_game import GoState, IGameState
from go.go_basic_board import GoBasicBoard
from go.go_fast_board import GoFastBoard
from search.mcts import Mcts
from search.evaluators import RandomRolloutEvaluator


class GoToIndexConverter(IActionConverter):
    def __init__(self, num: int, pass_index: int):
        self._pass_index = pass_index
        self._num = num

    def get_inner_action(self, outer_action: int) -> Optional[Coordinate]:
        if outer_action == self._pass_index:
            return None
        return outer_action // (self._num + 2), outer_action % (self._num + 2)

    def get_outer_action(self, inner_action: Optional[Coordinate]) -> int:
        if inner_action is None:
            return self._pass_index
        return inner_action[0] * (self._num + 2) + inner_action[1]


class GoHumanAgent(HumanAgent):
    def __init__(self, player_index: int, state: IGameState, converter: IActionConverter):
        super(GoHumanAgent, self).__init__(player_index, state)
        self._converter = converter

    def get_input_action(self, is_last_input_invalid: bool):
        if is_last_input_invalid:
            print("Invalid action")
        while True:
            action_str = input("input x,y or empty(for pass) ")
            if action_str == "exit":
                sys.exit(0)
            if not action_str:
                return self._converter.get_outer_action(None)
            else:
                try:
                    action = tuple(int(x) for x in action_str.split(","))
                    if len(action) != 2:
                        pass
                    return self._converter.get_outer_action(action)
                except ValueError:
                    pass
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--board_size", type=int, default=9)
    args = parser.parse_args()

    board_size = args.board_size
    rng = np.random.RandomState(0)
    to_index_action = GoToIndexConverter(board_size, GoFastBoard.PASS_INDEX)

    # state决定Action的类型，所有agents都需要和state的Action类型一致
    def state_factory_method():
        return GoState(GoFastBoard(board_size))

    mcts_core = Mcts(RandomRolloutEvaluator(1, rng), puct_const=2.0, max_simulations=1000, random_state=rng)
    # agent0 = MctsAgent(0, mcts_core, state_factory_method())
    agent0 = SimpleAgentV1(0, board_size, to_index_action)
    # agent1 = MctsAgent(1, mcts_core, state_factory_method())
    # agent1 = RandomAgent(1, state_factory_method(), rng)
    agent1 = GoHumanAgent(1, state_factory_method(), to_index_action)
    game = SequentialGame()
    game.run_game(state_factory_method(), [agent0, agent1], True)
