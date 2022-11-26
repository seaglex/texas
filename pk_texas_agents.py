import argparse
import numpy as np
import pickle
import copy
import cProfile

from texas.texas_games import NoLimitTexasGame
from texas.judge import TexasJudge
from texas.monte_carlo import Simulator
from texas.agent import naive_agents


def start_game(agents, big_blind, max_epoch, seed):
    judge = TexasJudge()

    np.random.seed(seed)
    game = NoLimitTexasGame(judge, big_blind)

    max_bankrupt_num = 10
    min_agent_num = 4
    init_pool_amount = big_blind * 100

    for a in agents:
        a.set_amount(init_pool_amount)
    agent_rewards = {a: -init_pool_amount for a in agents}
    ordered_agents = agents[:]

    epoch = 0
    while epoch < max_epoch:
        epoch += 1
        amounts = game.run_a_hand(agents, is_verbose=False)
        for n, agent in enumerate(agents):
            agent.set_reward(amounts[n])
        if epoch % 100 == 0:
            print("Hand", epoch)
            for a in agents:
                print(a.get_name(), agent_rewards[a], a.get_amount())
        # rotate
        agents = agents[-1:] + agents[:-1]

        quitting_list = []
        for index, a in enumerate(agents):
            if a.get_amount() >= big_blind:
                continue
            if agent_rewards[a] <= -max_bankrupt_num * init_pool_amount:
                # to quit
                agent_rewards[a] += a.get_amount()
                a.set_amount(0)
                quitting_list.append(index)
            else:
                # more money
                agent_rewards[a] -= init_pool_amount
                a.set_amount(a.get_amount() + init_pool_amount)
        for cnt, index in enumerate(quitting_list):
            agents.pop(index - cnt)

        if len(agents) < min_agent_num:
            break
    print("Final results -", epoch)
    for a in ordered_agents:
        print(a.get_name(), a.get_amount() + agent_rewards[a])


def get_model(fname, big_blind):
    judge = TexasJudge()
    calc = Simulator(judge)

    model = {
        "static": naive_agents.StaticAgent(big_blind, 0, calc, 1000),
        "brave": naive_agents.BraveAgent(big_blind, 0, calc),
        "random": naive_agents.RandomAgent(big_blind, 0),
    }.get(fname)
    if model:
        return model
    with open(fname, "rb") as fin:
        return pickle.load(fin)


def start_pk(left_name, right_name, seed):
    big_blind = 20
    left_model = get_model(left_name, big_blind)
    right_model = get_model(right_name, big_blind)
    agents = [
        left_model, right_model,
        *([copy.deepcopy(left_model) for _ in range(2)]),
        *([copy.deepcopy(right_model) for _ in range(2)]),
    ]
    for index, a in enumerate(agents):
        a._agent_index = index
    if seed is None:
        seed = np.random.randint(0, 32768, (1), np.int)[0]
    start_game(agents, big_blind, 1000, seed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--left", required=True)
    parser.add_argument("-r", "--right", required=True)
    parser.add_argument("-s", "--seed", type=int, default=-1)
    args = parser.parse_args()
    start_pk(args.left, args.right, args.seed if args.seed >= 0 else None)