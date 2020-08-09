import random


class GreedySampler(object):
    @staticmethod
    def get_action(available_actions, action_scores, _):
        largest = None
        best = None
        if not action_scores:
            return available_actions[0]
        for action, score in action_scores.items():
            if largest is None or score > largest:
                largest = score
                best = action
        return best


class EpsilonGreedySampler(object):
    def __init__(self, epsilon=0.1):
        self._epsilon = epsilon
        self._rand = random.Random(0)

    def get_action(self, available_actions, action_scores, _):
        if action_scores is None or (self._rand.random() < self._epsilon):
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
