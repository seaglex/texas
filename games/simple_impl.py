from typing import Any, List

from .common import IGameState, IAgent
from search.mcts import Mcts


class MctsAgent(IAgent):
    def __init__(self, player_index: int, mcts: Mcts, state: IGameState):
        self._mcts = mcts
        self._state = state
        self._player_index = player_index

    def get_name(self) -> str:
        return type(self).__name__ + str(self._player_index)

    def step(self) -> Any:
        action = self._mcts.mcts_search(self._state)
        self._state.apply_action(action)
        return action

    def inform_action(self, other_player: int, action: Any) -> type(None):
        assert other_player != self._player_index
        self._state.apply_action(action)


class RandomAgent(IAgent):
    def __init__(self, player_index: int, state: IGameState, rng):
        self._player_index = player_index
        self._state = state
        self._rng = rng

    def get_name(self) -> str:
        return type(self).__name__ + str(self._player_index)

    def step(self) -> Any:
        actions = self._state.get_valid_actions()
        action = actions[self._rng.randint(0, len(actions))]
        self._state.apply_action(action)
        return action

    def inform_action(self, other_player: int, action: Any) -> type(None):
        assert other_player != self._player_index
        self._state.apply_action(action)


class SequentialGame(object):
    def __init__(self, state_factory_method):
        self._state_factory_method = state_factory_method

    def run_game(self, agents: List[IAgent], verbose=False):
        game_state = self._state_factory_method()
        while not game_state.is_terminal():
            player = game_state.get_current_player()
            action = agents[player].step()
            game_state.apply_action(action)
            for p, agent in enumerate(agents):
                if p == player:
                    continue
                agent.inform_action(player, action)
            if verbose:
                print(agents[player].get_name(), action)
                print(game_state.to_str())
                print()
        scores = game_state.get_rewards()
        if verbose:
            print("Scores")
            for n, agent in enumerate(agents):
                print(n, agent.get_name(), scores[n])
        return scores
