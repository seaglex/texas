import argparse
import numpy as np

from games.simple_impl import MctsAgent, SequentialGame, RandomAgent
from games.tic_tac_toe import TicTacToeState, HumanAgent
from search.mcts import Mcts
from search.evaluators import RandomRolloutEvaluator


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    def state_factory_method():
        return TicTacToeState()
    rng = np.random.RandomState(0)
    mcts_core = Mcts(RandomRolloutEvaluator(1, rng), puct_const=2.0, max_simulations=1000, random_state=rng)
    agent0 = MctsAgent(0, mcts_core, state_factory_method())
    # agent1 = MctsAgent(1, mcts_core, state_factory_method())
    agent1 = RandomAgent(1, state_factory_method(), rng)
    # agent1 = HumanAgent(1, state_factory_method())
    game = SequentialGame(state_factory_method)
    game.run_game([agent0, agent1], True)
