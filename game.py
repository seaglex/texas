import argparse

from texas.texas_games import NoLimitTexasGame
from texas.judge import TexasJudge
from texas.monte_carlo import Simulator
from texas.agent import human_agent, naive_agents


def start_game(agent_num, is_verbose, is_public):
    judge = TexasJudge()
    simulator = Simulator(judge)
    big_blind = 20
    agents = []
    agents.append(naive_agents.StaticAgent(big_blind, 2000, simulator, None))
    for n in range(agent_num - 2):
        agents.append(naive_agents.StaticAgent(big_blind, 2000, simulator, 1000))
    agents.append(human_agent.HumanAgent(big_blind, 2000, simulator))
    game = NoLimitTexasGame(judge, big_blind)
    amounts = game.run_a_hand(agents, is_verbose=is_verbose, is_public=is_public)
    for n, agent in enumerate(agents):
        print("Agent%d" % n, amounts[n])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--agent_num", type=int, default=8)
    parser.add_argument("-p", "--public", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    start_game(args.agent_num, True, args.public)