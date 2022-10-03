import argparse
import numpy as np

from games.simple_impl import MctsAgent, SequentialGame, RandomAgent, HumanAgent
from go.manual_agents import SimpleAgentV1
from go.go_game import GoState, IGameState
from go.go_basic_board import GoBasicBoard
from go.go_fast_board import GoFastBoard
from search.mcts import Mcts
from search.evaluators import RandomRolloutEvaluator


class GoHumanAgent(HumanAgent):
    def __init__(self, player_index: int, state: IGameState, num: int, is_coordinate=True):
        super(GoHumanAgent, self).__init__(player_index, state)
        self._num = num
        self._is_coordinate = is_coordinate

    def get_input_action(self, is_last_input_invalid: bool):
        if is_last_input_invalid:
            print("Invalid action")
        while True:
            action_str = input("input x,y or empty ")
            if not action_str:
                if self._is_coordinate:
                    return None
                return GoFastBoard.PASS_INDEX
            else:
                try:
                    action = tuple(int(x) for x in action_str.split(","))
                    if len(action) != 2:
                        pass
                    if self._is_coordinate:
                        return action
                    return action[0] * (self._num + 2) + action[1]
                except ValueError:
                    pass
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    def state_factory_method():
        return GoState(GoBasicBoard(9))
    rng = np.random.RandomState(0)
    mcts_core = Mcts(RandomRolloutEvaluator(1, rng), puct_const=2.0, max_simulations=1000, random_state=rng)
    # agent0 = MctsAgent(0, mcts_core, state_factory_method())
    agent0 = SimpleAgentV1(0, 9)
    # agent1 = MctsAgent(1, mcts_core, state_factory_method())
    # agent1 = RandomAgent(1, state_factory_method(), rng)
    agent1 = GoHumanAgent(1, state_factory_method(), 9, True)
    game = SequentialGame()
    game.run_game(state_factory_method(), [agent0, agent1], True)
