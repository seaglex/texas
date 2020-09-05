import random
import math


class GreedySampler(object):
    @staticmethod
    def get_action(available_actions, action_scores, _):
        largest = None
        best = None
        if not action_scores:
            return available_actions[0]
        for action in available_actions:
            score = action_scores.get(action, 0.0)
            if largest is None or score > largest:
                largest = score
                best = action
        return best


class EpsilonGreedySampler(object):
    def __init__(self, eps_start=0.9, eps_end=0.05, eps_decay=1000):
        self._eps_start = eps_start
        self._eps_end = eps_end
        self._eps_decay = eps_decay
        self._rand = random.Random(0)
        self._count = 0

    def get_action(self, available_actions, action_scores, _):
        self._count += 1
        eps_threshold = self._eps_end + (self._eps_start - self._eps_end) * math.exp(
            -1. * self._count / self._eps_decay)
        if action_scores is None or (self._rand.random() < eps_threshold):
            return available_actions[self._rand.randint(0, len(available_actions) - 1)]
        largest = None
        best = None
        pool_size = 0
        for action in available_actions:
            score = action_scores.get(action, 0.0)
            if largest is None or score > largest:
                largest = score
                best = action
                pool_size = 1
            elif score == largest:
                # 蓄水池抽样
                pool_size += 1
                if self._rand.random() < 1.0 / pool_size:
                    best = action
        return best


class ThompsonSampler(object):
    def __init__(self, a=1, b=1):
        self._a = a
        self._b = b
        self._rand = random.Random(0)

    def get_action(self, available_actions, action_scores, action_counts):
        largest = None
        best = None
        action_scores = {} if action_scores is None else action_scores
        action_counts = {} if action_counts is None else action_counts
        for action in available_actions:
            score = action_scores.get(action, 0.0)
            count = action_counts.get(action, 0)
            a = count * (score + 1.0) * 0.5
            b = count - a
            r = self._rand.betavariate(self._a + a, self._b + b)
            if largest is None or r > largest:
                largest = r
                best = action
        return best
