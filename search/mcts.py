"""
Monte Carlo Tree Search
参考open_spiel设计，简化，尽量提升可读性
"""
from __future__ import annotations
from typing import List, Tuple, Any
import numpy as np
import math

from games.common import IGameState


class IEvaluator(object):
    def evaluate_action_priors(self, state: IGameState) -> List[Tuple[Any, float]]:
        raise NotImplementedError()

    def evaluate_state(self, state: IGameState) -> List[float]:
        raise NotImplementedError()


class SearchNode(object):
    INF = float("inf")

    def __init__(self, player_index: int, action: Any, prior=1.0):
        """
        :param player_index: which player benefits from the action;
        :param action: from which it reach this state
        :param prior:
        """
        self.player_index = player_index
        self.action = action
        self.prior = prior
        self.explore_count: int = 0
        self.total_reward: float = 0.0
        self.outcomes = []  # determined outcomes
        self.children: List[SearchNode] = []

    def __repr__(self):
        return "player{0}-{1}-{2:.3f}-{3}".format(
            self.player_index, self.action,
            self.total_reward / max(self.explore_count, 1),
            self.explore_count
        )

    # upper confidence of tree
    def puct_value(self, parent_explore_count: int, puct_const: float):
        if self.outcomes:
            return self.outcomes[self.player_index]
        return (self.explore_count and self.total_reward / self.explore_count
                ) + puct_const * self.prior * math.sqrt(parent_explore_count) / (self.explore_count + 1)

    def uct_value(self, parent_explore_count: int, uct_const: float):
        if self.outcomes:
            return self.outcomes[self.player_index]
        if self.explore_count == 0:
            return SearchNode.INF
        return self.total_reward / self.explore_count + uct_const * math.sqrt(
            math.log(parent_explore_count) / self.explore_count)

    def final_sorting_key(self):
        return (0 if not self.outcomes else self.outcomes[self.player_index],
                self.explore_count, self.total_reward)


class Mcts(object):
    def __init__(self, evaluator: IEvaluator, puct_const: float, max_simulations: int,
                 random_state: np.random.RandomState):
        self._evaluator = evaluator
        self._puct_const = puct_const
        self._max_simulations = max_simulations
        self._random = random_state
        self._uct = SearchNode.uct_value

    def mcts_search(self, state: IGameState) -> Any:
        assert state is not None
        # If there were many choices, the other player will be benefited
        # However, it has reached this state, current player will be benefited
        # In fact, the root.player_index doesn't matter
        root = SearchNode(state.get_current_player(), None)
        # A min-max selection, based on both the evaluator (rewards) and determined results (outcomes)
        for itr in range(self._max_simulations):
            # expand & select
            path, working_state = self._apply_tree_policy(root, state)
            solved = False
            if working_state.is_terminal():
                rewards = working_state.get_rewards()
                solved = True
                path[-1].outcomes = rewards
            else:
                rewards = self._evaluator.evaluate_state(working_state)
            # update rewards & explore counts
            for node in reversed(path):
                node.explore_count += 1
                node.total_reward += rewards[node.player_index]
                if solved and node.children:
                    solved, best_outcomes = self._select_best_outcomes(state, node.children)
                    if solved:
                        node.outcomes = best_outcomes
            # If the result is determined
            if root.outcomes:
                break

        best_child = max(root.children, key=SearchNode.final_sorting_key)
        return best_child.action

    @staticmethod
    def _select_best_outcomes(state: IGameState, children: List[SearchNode]) -> (bool, List[float]):
        """
        A min-max approach for the determined case,
        all children are solved or one child has "good enough" result.
        :param children
        :return: solved? the-best-outcomes
        """
        best_outcomes = None
        all_solved = True
        player = children[0].player_index
        for child in children:
            if not child.outcomes:
                all_solved = False
            elif best_outcomes is None or child.outcomes[player] > best_outcomes[player]:
                best_outcomes = child.outcomes
        if all_solved or state.is_good_enough(best_outcomes[player]):
            return True, best_outcomes
        return False, []

    def _apply_tree_policy(self, root: SearchNode, state: IGameState) -> (List[SearchNode], IGameState):
        path = [root]
        working_state = state.clone()

        node = root
        while not working_state.is_terminal() and node.explore_count > 0:
            # go deeper
            if not node.children:
                node.children = self._expand(working_state)
            node = self._select(node)
            working_state.apply_action(node.action)
            path.append(node)
        return path, working_state

    def _select(self, node: SearchNode) -> SearchNode:
        return max(node.children, key=lambda c: self._uct(c, node.explore_count, self._puct_const))

    def _expand(self, state: IGameState) -> List[SearchNode]:
        action_priors = self._evaluator.evaluate_action_priors(state)
        player = state.get_current_player()
        children = [SearchNode(player, action, prior) for action, prior in action_priors]
        # shuffle to avoid bias
        self._random.shuffle(children)
        return children
