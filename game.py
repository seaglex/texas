import argparse
import pickle

from texas.texas_games import NoLimitTexasGame
from texas.judge import TexasJudge
from texas.monte_carlo import Simulator
from texas.agent import human_agent, naive_agents
from texas.agent import key_state_agent
from texas.common import BaseAgent
from rl import q_learner, bandit


def load_model(fname):
    with open(fname, "rb") as fin:
        return pickle.load(fin)

def start_game(agent_num, is_public, models):
    judge = TexasJudge()
    simulator = Simulator(judge)
    big_blind = 20

    agents = []
    for n in range(agent_num - len(models) - 1):
        agents.append(naive_agents.StaticAgent(big_blind, 2000, simulator, 1000))
    for n in range(len(models)):
        agents.append(load_model(models[n]))
        agents[-1].set_amount(2000)
        agents[-1].is_test = True
    agents.append(human_agent.HumanAgent(big_blind, 2000, simulator))

    game = NoLimitTexasGame(judge, big_blind)

    is_bankrupt = False
    while not is_bankrupt:
        amounts = game.run_a_hand(agents, is_verbose=True, is_public=is_public)
        for n, amount in enumerate(amounts):
            print("Agent%d" % n, amount)
        for n, agent in enumerate(agents):
            agent.set_reward(amounts[n])
            if agent.get_amount() < big_blind:
                is_bankrupt = True
                break

    # end of game
    print("Left amount")
    for n, agent in enumerate(agents):
        print("Agent%d" % n, agent.get_amount())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--agent_num", type=int, default=8)
    parser.add_argument("-m", "--model", nargs="*")
    parser.add_argument("-p", "--public", action="store_true")
    args = parser.parse_args()

    start_game(args.agent_num, args.public, args.model)
