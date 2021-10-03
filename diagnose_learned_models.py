import argparse
import pickle
import random

from texas.texas_games import NoLimitTexasGame
from texas.judge import TexasJudge
from texas.monte_carlo import Simulator
from texas.agent import human_agent, naive_agents
from texas.agent import key_state_agent
from texas.common import InnerAction
from rl import q_learner, bandit


def load_model(fname):
    with open(fname, "rb") as fin:
        return pickle.load(fin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    args = parser.parse_args()
    model = load_model(args.model)
    key_best_actions = []
    for key, action_scores in model.q_learner._q_values.items():
        largest = None
        best = None
        for action in [
            InnerAction.Conservative, InnerAction.Normal, InnerAction.Aggressive, InnerAction.Very_Aggressive]:
            score = action_scores.get(action, 0.0)
            if largest is None or score > largest:
                largest = score
                best = action
        key_best_actions.append((key, (best, largest)))
    for key, action in sorted(key_best_actions):
        print(key, action)
