import argparse
import itertools
import numpy as np
import pickle
import datetime as dt
from collections import deque

from texas.texas_games import NoLimitTexasGame
from texas.judge import TexasJudge
from texas.monte_carlo import Simulator
from texas.direct_cmp import ApproxComparer
from texas.agent import human_agent, naive_agents
from texas.agent import key_state_agent
from texas.common import BaseAgent
from rl import q_learner, bandit

def load_model(fname):
    with open(fname, "rb") as fin:
        return pickle.load(fin)


def start_game():
    judge = TexasJudge()
    pr_calc = ApproxComparer()
    big_blind = 20

    start_epoch = 1000000
    learner = q_learner.QLearner(bandit.EpsilonGreedySampler(eps_end=0.2, eps_decay=100000), 0.01)
    quantizer2 = key_state_agent.State2Quantizer()

    model = load_model("models/InnerKeyStateAgent-q2-vs_naive-1000000.pkl")
    learner = model.q_learner

    agents = [
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            pr_calc, quantizer2,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            pr_calc, quantizer2,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            pr_calc, quantizer2,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            pr_calc, quantizer2,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            pr_calc, quantizer2,
            learner),
        key_state_agent.InnerKeyStateAgent(
            big_blind, 2000,
            pr_calc, quantizer2,
            learner),
    ]
    test_agent_indexes = [
        5
    ]
    acc_rewards = [0] * len(agents)
    acc_test_rewards = [0] * len(agents)
    trial_num = 0
    test_trial_num = 0
    test_rewards_list = [deque(maxlen=100) for _ in range(len(agents))]

    np.random.seed(0)
    game = NoLimitTexasGame(judge, big_blind)

    for epoch in itertools.count(start=start_epoch+1):
        # 充钱 or 归零
        for n, agent in enumerate(agents):
            if agent.get_amount() < big_blind or agent.get_amount() > 2000 * 10:
                agent.set_amount(2000)
        # is test
        is_test = epoch % 10 in (1, 2)
        for agent in agents:
            agent.is_test = is_test

        # 开玩
        amounts = game.run_a_hand(agents, is_verbose=False)
        for n, agent in enumerate(agents):
            agent.set_reward(amounts[n])

        trial_num += 1
        for n, agent in enumerate(agents):
            acc_rewards[n] = acc_rewards[n] * 0.9999 + amounts[n] * 0.0001
        if is_test:
            test_trial_num += 1
            for idx in range(len(agents)):
                acc_test_rewards[idx] = acc_test_rewards[idx] * 0.9999 + amounts[idx] * 0.0001
                test_rewards_list[idx].append(amounts[idx])

        if epoch % 1000 == 0:
            print(epoch, end=" ", flush=True)
        if epoch % 10000 == 0:
            print()
            for n, agent in enumerate(agents):
                print("\tagent%d" % n,
                      "acc-reward", acc_rewards[n] / trial_num,
                      "acc-test-reward", acc_test_rewards[n] / trial_num, flush=True)
            for idx in test_agent_indexes:
                if test_trial_num <= 0:
                    break
                ana_test_rewards = np.array(test_rewards_list[idx])
                print("epoch", epoch, "index", idx,
                      "avg-test-reward/std", ana_test_rewards.sum() / len(ana_test_rewards), ana_test_rewards.std(),
                      flush=True
                      )
        if epoch % 100000 != 0:
            continue
        for idx in test_agent_indexes:
            with open("models/InnerKeyStateAgent-index%d-%d.pkl" % (idx, epoch), "wb") as fout:
                pickle.dump(agents[idx], fout)


if __name__ == "__main__":
    start_game()
