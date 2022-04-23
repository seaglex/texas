
class GoState(object):
    def __init__(self, board):
        self._player_index = 0
        self._board = board

    def apply_action(self, pos, piece):
        return

    def get_actions(self):
        return []

    def is_terminal(self):
        return False

    def get_rewards(self):
        return []

class GoGame(object):
    def __init__(self, judge, num):
        self._judge = judge
        self._num = num

    def run_a_round(self, agents):
        return None
