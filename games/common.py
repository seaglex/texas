from __future__ import annotations
from typing import Any, List


class IGameState(object):
    def get_current_player(self) -> int:
        """
        It's the state that control the player order
        """
        raise NotImplementedError()

    def get_valid_actions(self) -> List[Any]:
        raise NotImplementedError()

    def is_valid_action(self, action: Any):
        raise NotImplementedError()

    def apply_action(self, action) -> type(None):
        raise NotImplementedError()

    def is_terminal(self) -> bool:
        raise NotImplementedError()

    def get_rewards(self) -> List[float]:
        raise NotImplementedError()

    @staticmethod
    def is_good_enough(score) -> bool:
        raise NotImplementedError

    def clone(self) -> IGameState:
        raise NotImplementedError()

    def to_str(self) -> str:
        raise NotImplementedError()


class IAgent(object):
    def get_name(self) -> str:
        raise NotImplementedError()

    def step(self) -> Any:
        """
        Take and return an action
        """
        raise NotImplementedError()

    def inform_action(self, other_player: int, action: Any) -> type(None):
        """
        Inform that other_player takes the action
        """
        raise NotImplementedError()


class IActionConverter(object):
    def get_outer_action(self, inner_action: Any) -> Any:
        raise NotImplementedError()

    def get_inner_action(self, outer_action: Any) -> Any:
        raise NotImplementedError()


class IdentityActionConverter(IActionConverter):
    def get_outer_action(self, inner_action: Any) -> Any:
        return inner_action

    def get_inner_action(self, outer_action: Any) -> Any:
        return outer_action


class ReverseActionConverter(IActionConverter):
    def __init__(self, converter: IActionConverter):
        self._converter = converter

    def get_outer_action(self, inner_action: Any) -> Any:
        return self._converter.get_inner_action(inner_action)

    def get_inner_action(self, outer_action: Any) -> Any:
        return self._converter.get_outer_action(outer_action)
