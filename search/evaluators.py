import numpy as np
from typing import List, Tuple, Any

from .mcts import IEvaluator, IGameState


class RandomRolloutEvaluator(IEvaluator):
    """
    Random Rollout evaluator
    Go game is too complex to use random rollouts
    """
    def __init__(self, num, random_state):
        self._num = num
        self._random_state = random_state

    def evaluate_action_priors(self, state: IGameState) -> List[Tuple[Any, float]]:
        actions = state.get_valid_actions()
        if not actions:
            return []
        return list(zip(actions, [1 / len(actions)] * len(actions)))

    def evaluate_state(self, state: IGameState) -> List[float]:
        total_rewards = None
        for n in range(self._num):
            working_state = state.clone()
            while not working_state.is_terminal():
                actions = working_state.get_valid_actions()
                action = actions[self._random_state.randint(0, len(actions))]
                working_state.apply_action(action)
            if total_rewards is None:
                total_rewards = np.array(working_state.get_rewards())
            else:
                total_rewards += working_state.get_rewards()
        return total_rewards / self._num
