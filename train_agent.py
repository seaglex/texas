import argparse
import itertools
import numpy as np
import pickle
import datetime as dt

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


def start_game():
    judge = TexasJudge()
    simulator = Simulator(judge)
    big_blind = 20

    start_epoch = -1
    learner = q_learner.QLearner(bandit.EpsilonGreedySampler(eps_end=0.2, eps_decay=100000), 0.05)
    quantizer4 = key_state_agent.State4Quantizer()
    quantizer5 = key_state_agent.State5Quantizer()

    # model = load_model("models/InnerKeyStateAgent-272000.pkl")
    # learner = model.q_learner

    agents = [
        naive_agents.BraveAgent(big_blind, 2000, simulator),
        naive_agents.StaticAgent(big_blind, 2000, simulator, 1000),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            simulator, quantizer4,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            simulator, quantizer4,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            simulator, quantizer4,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            simulator, quantizer5,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            simulator, quantizer5,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            simulator, quantizer5,
            learner),
    ]
    test_agent_indexes = [
        4, 7
    ]
    acc_rewards = [0] * len(agents)
    acc_test_rewards = [0] * len(agents)
    trial_num = 0
    test_trial_num = 0
    rewards_list = [[] for _ in range(len(agents))]
    test_rewards_list = [[] for _ in range(len(agents))]

    np.random.seed(0)
    game = NoLimitTexasGame(judge, big_blind)

    for epoch in itertools.count(start=start_epoch+1):
        # 充钱 or 归零
        for n, agent in enumerate(agents):
            if agent.get_amount() < big_blind or agent.get_amount() > 2000 * 10:
                agent.set_amount(2000)
        # is test
        is_test = epoch % 10 in (1, 2)
        for idx in test_agent_indexes:
            agents[idx].is_test = is_test

        # 开玩
        amounts = game.run_a_hand(agents, is_verbose=False)
        for n, agent in enumerate(agents):
            agent.set_reward(amounts[n])

        trial_num += 1
        for n, agent in enumerate(agents):
            acc_rewards[n] += amounts[n]
        for idx in test_agent_indexes:
            rewards_list[idx].append(amounts[idx])
        if is_test:
            test_trial_num += 1
            for idx in test_agent_indexes:
                acc_test_rewards[idx] += amounts[idx]
                test_rewards_list[idx].append(amounts[idx])

        if epoch % 100 == 0:
            print(epoch, end=" ", flush=True)
        if epoch % 500 == 0:
            print()
            for n, agent in enumerate(agents):
                print("\tagent%d" % n,
                      "acc-reward", acc_rewards[n] / trial_num,
                      "acc-test-reward", acc_test_rewards[n] / trial_num, flush=True)
            for idx in test_agent_indexes:
                if test_trial_num <= 0:
                    break
                ana_rewards = np.array(rewards_list[idx][-500:])
                ana_test_rewards = np.array(test_rewards_list[idx][-100:])
                print("epoch", epoch, "index", idx,
                      "avg-reward/std", ana_rewards.sum() / len(ana_rewards), ana_rewards.std(),
                      "avg-test-reward/std", ana_test_rewards.sum() / len(ana_test_rewards), ana_test_rewards.std(),
                      flush=True
                      )
        if epoch % 1000 != 0:
            continue
        for idx in test_agent_indexes:
            with open("InnerKeyStateAgent-index%d-%d.pkl" % (idx, epoch), "wb") as fout:
                pickle.dump(agents[idx], fout)


if __name__ == "__main__":
    start_game()
