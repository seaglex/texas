from typing import Any

from games.common import IAgent
from games.simple_impl import IActionConverter, IdentityActionConverter
from go.go_game import GoState
from go.go_basic_board import GoBasicBoard, GoBasicSuggester


class SimpleAgentV1(IAgent):
    """
    1 初始化中，抢占地盘
    2 缠斗中，攻击或长气
    """
    def __init__(self, player_index: int, num: int, converter: IActionConverter = None):
        self._player_index = player_index
        self._go_board = GoBasicBoard(num)
        self._state = GoState(self._go_board)
        self._converter = converter if converter is not None else IdentityActionConverter()

    def get_name(self) -> str:
        return "simple-agent-v1-" + str(self._player_index)

    def step(self) -> Any:
        stone = self._state.get_current_stone()
        if self._state.get_move_count() <= 4:
            action = GoBasicSuggester.get_static_suggestion(stone, self._go_board)
        else:
            action = GoBasicSuggester.get_liberty_suggestion(stone, self._go_board)
        self._state.apply_action(action)
        return self._converter.get_outer_action(action)

    def inform_action(self, other_player: int, action: Any) -> type(None):
        if self._player_index != other_player:
            self._state.apply_action(self._converter.get_inner_action(action))
