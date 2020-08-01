"""
Simple Q-learning
"""

import random
from collections import defaultdict
from rl import bandit


class QLearner(object):
    GAMMA = 0.99

    def __init__(self):
        self._q_values = {}
        self._q_counts = {}
        self._alpha = 0.2
        self._default_value = 0.0
        self._rand = random.Random(0)
        self._sampler = bandit.ThompsonSampler()

    def _get_default_action_values(self):
        return defaultdict(lambda: self._default_value)

    def get_action(self, state, available_actions, iter_cnt=None):
        action_scores = self._q_values.get(state, {})
        action_counts = self._q_counts.get(state, {})
        if iter_cnt is None:
            return bandit.GreedySampler.get_action(available_actions, action_scores, action_counts)
        return self._sampler.get_action(available_actions, action_scores, action_counts)

    def update(self, state, action, next_state, reward):
        action_values = self._q_values.get(state)
        if action_values is None:
            action_values = self._get_default_action_values()
            action_counts = defaultdict(int)
            self._q_values[state] = action_values
            self._q_counts[state] = action_counts
        else:
            action_counts = self._q_counts[state]
        action_values[action] = (1.0 - self._alpha) * action_values[action] + self._alpha * (
            reward + self._get_value(next_state) * self.GAMMA
        )
        action_counts[action] += 1

    def _get_q_value(self, state, action):
        action_values = self._q_values.get(state)
        if action_values is None:
            return self._default_value
        return action_values[action]

    def _get_value(self, state):
        action_values = self._q_values.get(state)
        if action_values is None:
            return self._default_value
        return max(action_values.values())
