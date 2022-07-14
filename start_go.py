import argparse
import numpy as np

from games.simple_impl import MctsAgent, SequentialGame, RandomAgent, HumanAgent
from go.go_game import GoState
from go.go_basic_board import GoBasicBoard
from go.go_fast_board import GoFastBoard
from search.mcts import Mcts
from search.evaluators import RandomRolloutEvaluator


class GoHumanAgent(HumanAgent):
    def get_input_action(self, is_last_input_invalid: bool):
        if is_last_input_invalid:
            print("Invalid action")
        while True:
            action_str = input("input x,y or empty ")
            if not action_str:
                return None
            else:
                try:
                    action = tuple(int(x) for x in action_str.split(","))
                    if len(action) != 2:
                        pass
                    return action
                except ValueError:
                    pass
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    def state_factory_method():
        return GoState(GoFastBoard(19))
    rng = np.random.RandomState(0)
    mcts_core = Mcts(RandomRolloutEvaluator(1, rng), puct_const=2.0, max_simulations=1000, random_state=rng)
    agent0 = MctsAgent(0, mcts_core, state_factory_method())
    agent1 = MctsAgent(1, mcts_core, state_factory_method())
    # agent1 = RandomAgent(1, state_factory_method(), rng)
    # agent1 = GoHumanAgent(1, state_factory_method())
    game = SequentialGame(state_factory_method)
    game.run_game([agent0, agent1], True)
