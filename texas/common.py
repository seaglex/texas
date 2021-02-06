import enum


class TexasRound(enum.IntEnum):
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3


class AgentAction(enum.IntEnum):
    Blind = 0
    Fold = 1
    Check = 2
    Bet = 3
    Call = 4
    Raise = 5
    Raise_more = 6
    All_in = 7
    Padding = -1

    def is_hand_over(self):
        return self == AgentAction.Fold or self == AgentAction.All_in

    @staticmethod
    def try_parse(s):
        s = s.lower()
        return {
            "blind": AgentAction.Blind,
            "fold": AgentAction.Fold,
            "check": AgentAction.check,
            "bet": AgentAction.bet,
            "call": AgentAction.Call,
            "raise": AgentAction.Raise,
            "raise_more": AgentAction.Raise_more,
            "all_in": AgentAction.All_in,
            "padding": AgentAction.Padding,
        }.get(s, None)

    @staticmethod
    def get_normal_actions(open_bet):
        if open_bet == 0:
            return AgentAction.Fold, AgentAction.Check, AgentAction.All_in, AgentAction.Bet
        else:
            return AgentAction.Fold, AgentAction.Call, AgentAction.Raise, AgentAction.Raise_more, AgentAction.All_in


class SingleCache(object):
    def __init__(self):
        self._key = None
        self._value = None
        self._initialized = False

    def is_valid(self, key):
        return self._initialized and key == self._key

    def reset(self):
        self._initialized = False
        self._key = None

    def get_value(self):
        return self._value

    def set_value(self, key, value):
        self._key = key
        self._value = value
        self._initialized = True


class BaseAgent(object):
    glb_count = 0

    def __init__(self, big_blind, total_amount=None, *, name=None):
        """
        :param total_amount: None for inf
        """
        self._big_blind = big_blind
        self._total_amount = total_amount  # Total money
        self._name = name
        self._agent_index = BaseAgent.glb_count
        BaseAgent.glb_count += 1

        self._hole_cards = []
        self._community_cards = []
        self._cum_amount = 0               # agent's money in pool
        self._latest_bet = 0               # latest bet in this round

    def get_name(self):
        if not self._name:
            return type(self).__name__ + str(self._agent_index)
        return self._name

    def _wrap_return(self, action, bet):
        """
        Handle the case that there is not enough money & save latest_bet
        """
        if self._total_amount is not None and self._cum_amount + bet >= self._total_amount:
            self._latest_bet = self._total_amount - self._cum_amount
            return AgentAction.All_in, self._latest_bet
        self._latest_bet = bet
        return action, bet

    # the following are for game-agent interaction
    def start_new_game(self):
        self._hole_cards = []
        self._community_cards = []
        assert self._cum_amount == 0
        assert self._latest_bet == 0

    def get_hole_cards(self, hold_cards):
        self._hole_cards = hold_cards

    def get_community_cards(self, community_cards):
        self._community_cards = community_cards

    def set_bet(self, bet):
        """
        For blind
        """
        self._latest_bet = bet

    def round_over(self):
        self._cum_amount += self._latest_bet
        self._latest_bet = 0

    def get_amount(self):
        return self._total_amount

    def set_amount(self, amount):
        self._total_amount = amount

    def set_reward(self, amount):
        if self._total_amount is not None:
            self._total_amount += amount
        self._cum_amount = 0
