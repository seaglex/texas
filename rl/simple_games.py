"""
This is only for test RL algorithms
"""
import random
import numpy as np


class SimpleMovingGame(object):
    """
    Simple game
    - start from (0, 0) to target (3, 3) with a trap (2, 2)
    - rewards for target and trap are 1 and -1, respectively
    - Move 1 to one of the four directions each time, 80% move forward, 10% left and 10% right
    - However, it never escape the rectangle between (0, 0) and (5, 5)
    """
    MOVING_CONFIDENCE = 0.8

    def __init__(self):
        self._start = (0, 0)
        self._target = (3, 3)
        self._trap = (2, 2)
        self._available_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self._available_actions = [0, 1, 2, 3]
        self._trap_reward = -1
        self._target_reward = 1
        self._rand = random.Random(0)

    def _get_direction(self, action):
        pr = self._rand.random()
        if pr < SimpleMovingGame.MOVING_CONFIDENCE:
            index = action
        elif self._rand.random() < 0.8:
            index = (action + 1) % 4
        else:
            index = (action - 1) % 4
        return self._available_directions[index]

    def _move(self, pos, action):
        direction = self._get_direction(action)
        pos = (min(max(pos[0] + direction[0], 0), 5), min(max(pos[1] + direction[1], 0), 5))
        return pos

    def train(self, q_learner, itr_num=10000, max_step=20):
        for itr in range(itr_num):
            if itr >= 5000:
                last_pos = (1, 1)
            else:
                last_pos = self._start
            for step in range(max_step):
                action = q_learner.get_action(last_pos, self._available_actions, itr)
                pos = self._move(last_pos, action)
                if pos == self._target:
                    q_learner.update(last_pos, action, pos, self._target_reward)
                    break
                elif pos == self._trap:
                    q_learner.update(last_pos, action, pos, self._trap_reward)
                    break
                else:
                    q_learner.update(last_pos, action, pos, 0.0)
                    last_pos = pos
            pass
        return

    def test(self, agent, max_step=20, start=None, is_debug=False):
        last_pos = self._start if start is None else start
        for step in range(max_step):
            action = agent.get_action(last_pos, self._available_actions)
            pos = self._move(last_pos, action)
            if is_debug:
                print(last_pos, action, pos)
            if pos == self._target:
                return self._target_reward
            elif pos == self._trap:
                return self._trap_reward
            else:
                last_pos = pos
        return 0.0


class RedBlackCardGame(object):
    """
    * red-black card
    * A：50%概率得到red/black card
    * A resign -20
    * A hold
        * B resign 10
        * B see
            * red/black 30/-40
    """
    class APlayer(object):
        def __init__(self, action=5):
            self._action = action

        def get_action(self, is_red, *args):
            if is_red:
                return 0
            return self._action

        def update(self, *args):
            return

    class BPlayer(object):
        def __init__(self, action=5):
            self._action = action

        def get_action(self, *args):
            return self._action

        def update(self, *args):
            return

    def __init__(self):
        self._rand = random.Random(0)
        self._pr_red = 0.5
        self._resigning_prs = np.arange(0, 1.01, 0.1)
        self._actions = np.arange(0, 11, 1)
        self._normalizer = 1 / 40

    def train(self, a_learner, b_learner, itr_num=10000):
        for itr in range(itr_num):
            if itr >= 9000:
                itr = itr
            is_red = self._rand.random() < self._pr_red
            a_action = a_learner.get_action(is_red, self._actions, itr)
            a_resigning_pr = self._resigning_prs[a_action]
            has_a_resigned = self._rand.random() < a_resigning_pr
            if has_a_resigned:
                a_learner.update(is_red, a_action, "a_resigned", -20 * self._normalizer)
            else:
                b_action = b_learner.get_action(None, self._actions, itr)
                has_b_resigned = self._rand.random() < self._resigning_prs[b_action]
                if has_b_resigned:
                    a_learner.update(is_red, a_action, "b_resigned", 10 * self._normalizer)
                    b_learner.update(None, b_action, "b_resigned", -10 * self._normalizer)
                else:
                    score = (30 if is_red else -40) * self._normalizer
                    a_learner.update(is_red, a_action, "saw", score)
                    b_learner.update(None, b_action, "saw", -score)
            pass

    def test(self, a_agent, b_agent, is_debug=False):
        is_red = self._rand.random() < self._pr_red
        a_action = a_agent.get_action(is_red, self._actions)
        a_resigning_pr = self._resigning_prs[a_action]
        has_a_resigned = self._rand.random() < a_resigning_pr
        if has_a_resigned:
            result, score = "a_resigned", -20 * self._normalizer
        else:
            b_action = b_agent.get_action(None, self._actions)
            has_b_resigned = self._rand.random() < self._resigning_prs[b_action]
            if has_b_resigned:
                result, score = "b_resigned", 10 * self._normalizer
            else:
                result, score = "saw", (30 if is_red else -40) * self._normalizer
        if is_debug:
            print("Red" if is_red else "Black", result, score)
        return score
