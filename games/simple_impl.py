from typing import Any, List
import datetime as dt

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


class HumanAgent(IAgent):
    def __init__(self, player_index: int, state: IGameState):
        self._player_index = player_index
        self._state = state

    def get_name(self) -> str:
        return "Human-" + str(self._player_index)

    def get_input_action(self, is_last_input_invalid: bool):
        raise NotImplementedError()

    def step(self) -> Any:
        is_last_input_invalid = False
        while True:
            action = self.get_input_action(is_last_input_invalid)
            if self._state.is_valid_action(action):
                break
            is_last_input_invalid = True
        self._state.apply_action(action)
        return action

    def inform_action(self, other_player: int, action: Any) -> type(None):
        assert self._player_index != other_player
        self._state.apply_action(action)


class SequentialGame(object):
    def __init__(self, state_factory_method):
        self._state_factory_method = state_factory_method

    def run_game(self, agents: List[IAgent], verbose=False):
        beg = dt.datetime.now()
        total_counts = [0] * len(agents)
        total_seconds = [0.0] * len(agents)
        game_state = self._state_factory_method()
        if verbose:
            print("initialize {0:.2f}s".format((dt.datetime.now() - beg).total_seconds()))
        cnt = 0
        while not game_state.is_terminal():
            cnt += 1
            player = game_state.get_current_player()
            beg = dt.datetime.now()
            action = agents[player].step()
            seconds = (dt.datetime.now() - beg).total_seconds()
            total_seconds[player] += seconds
            total_counts[player] += 1
            game_state.apply_action(action)
            for p, agent in enumerate(agents):
                if p == player:
                    continue
                agent.inform_action(player, action)
            if verbose:
                print("step", cnt, agents[player].get_name(), action,
                      "time {0:.2f}s (avg {1:.2f}s)".format(seconds, total_seconds[player]/total_counts[player]))
                print(game_state.to_str())
                print()
        scores = game_state.get_rewards()
        if verbose:
            print("Scores")
            for n, agent in enumerate(agents):
                print(n, agent.get_name(), scores[n])
        return scores
