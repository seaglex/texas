import argparse
import numpy as np

from games.simple_impl import MctsAgent, SequentialGame, RandomAgent, HumanAgent
from games.tic_tac_toe import TicTacToeState
from search.mcts import Mcts
from search.evaluators import RandomRolloutEvaluator


class TicTacToeHumanAgent(HumanAgent):
    def get_input_action(self, is_last_input_invalid: bool):
        while True:
            try:
                if is_last_input_invalid:
                    print("Invalid action")
                action = tuple(int(x) for x in input("input x,y ").split(","))
                if len(action) == 2:
                    return action
            except ValueError:
                pass
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    def state_factory_method():
        return TicTacToeState()
    rng = np.random.RandomState(0)
    mcts_core = Mcts(RandomRolloutEvaluator(1, rng), puct_const=2.0, max_simulations=1000, random_state=rng)
    agent0 = MctsAgent(0, mcts_core, state_factory_method())
    # agent1 = MctsAgent(1, mcts_core, state_factory_method())
    # agent1 = RandomAgent(1, state_factory_method(), rng)
    agent1 = TicTacToeHumanAgent(1, state_factory_method())
    game = SequentialGame()
    game.run_game(state_factory_method(), [agent0, agent1], True)
