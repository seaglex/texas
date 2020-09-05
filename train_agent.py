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
    rewards = []
    test_rewards = []

    start_epoch = -1
    learner = q_learner.QLearner(bandit.EpsilonGreedySampler(), 0.05)
    quantizer = key_state_agent.State4Quantizer()
    agents = [
        naive_agents.BraveAgent(big_blind, 2000, simulator),
        naive_agents.StaticAgent(big_blind, 2000, simulator, 1000),
        key_state_agent.KeyStateAgent(
            big_blind, 2000,
            simulator, quantizer,
            learner),
        key_state_agent.KeyStateAgent(
            big_blind, 2000,
            simulator, quantizer,
            learner),
        key_state_agent.KeyStateAgent(
            big_blind, 2000,
            simulator, quantizer,
            learner),
        key_state_agent.KeyStateAgent(
            big_blind, 2000,
            simulator, quantizer,
            learner),
        key_state_agent.KeyStateAgent(
            big_blind, 2000,
            simulator, quantizer,
            learner),
        key_state_agent.KeyStateAgent(
            big_blind, 2000,
            simulator, quantizer,
            learner),
    ]
    acc_rewards = [0] * len(agents)

    np.random.seed(0)
    game = NoLimitTexasGame(judge, big_blind)

    for epoch in itertools.count(start=start_epoch+1):
        # 充钱
        for n, agent in enumerate(agents):
            if agent.get_amount() < big_blind:
                agent.set_amount(2000)
        # 开玩
        if epoch % 10 in (1, 2):
            agents[-1].is_test = True
        else:
            agents[-1].is_test = False
        before_amount = agents[-1].get_amount()
        amounts = game.run_a_hand(agents, is_verbose=False)
        for n, agent in enumerate(agents):
            agent.set_reward(amounts[n])
            acc_rewards[n] += amounts[n]
        if before_amount + amounts[-1] < 0 or epoch > 500:
            print(epoch, before_amount, amounts[-1])
        rewards.append(amounts[-1])

        if epoch % 10 in (1, 2):
            test_rewards.append(amounts[-1])
        if epoch % 100 == 0:
            print(epoch, end=" ", flush=True)
        if epoch % 500 == 0:
            print()
            ana_rewards = np.array(rewards[-500:])
            ana_test_rewards = np.array(test_rewards[-100:])
            for n, agent in enumerate(agents):
                print("\tagent%d" % n, "amount", agent.get_amount(), "acc-reward", acc_rewards[n], flush=True)
            if len(ana_test_rewards) >= 10:
                print("epoch", epoch,
                      "avg-reward/std", ana_rewards.sum() / len(ana_rewards), ana_rewards.std(),
                      "avg-test-reward/std", ana_test_rewards.sum() / len(ana_test_rewards), ana_test_rewards.std(),
                      flush=True
                      )
        if epoch % 1000 == 0:
            with open("KeyStateAgent-%d.pkl" % epoch, "wb") as fout:
                pickle.dump(agents[-1], fout)


if __name__ == "__main__":
    start_game()
