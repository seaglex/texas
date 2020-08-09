import enum


class TexasRound(enum.IntEnum):
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3


class AgentState(enum.IntEnum):
    Blind = 0
    Fold = 1
    Check = 2
    Bet = 3
    Call = 4
    Raise = 5
    Raise_more = 6
    All_in = 7

    def is_hand_over(self):
        return self == AgentState.Fold or self == AgentState.All_in

    def is_ready_for_round_end(self):
        return self in {AgentState.Check, AgentState.Call, AgentState.Fold, AgentState.All_in}

    @staticmethod
    def try_parse(s):
        s = s.lower()
        return {
            "blind": AgentState.Blind,
            "fold": AgentState.Fold,
            "check": AgentState.check,
            "bet": AgentState.bet,
            "call": AgentState.Call,
            "raise": AgentState.Raise,
            "raise_more": AgentState.Raise_more,
            "all_in": AgentState.All_in,
        }.get(s, None)


class BaseAgent(object):
    def __init__(self, big_blind, total_amount=None):
        """
        :param total_amount: None for inf
        """
        self._hole_cards = None
        self._community_cards = None
        self._big_blind = big_blind
        self._total_amount = total_amount
        self._cum_amount = 0
        self._latest_bet = 0

    def _wrap_return(self, state, bet):
        if self._total_amount is not None and self._cum_amount + bet >= self._total_amount:
            self._latest_bet = self._total_amount - self._cum_amount
            return AgentState.All_in, self._latest_bet
        self._latest_bet = bet
        return state, bet

    # the following are for game-agent interaction
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

    def add_amount(self, amount):
        self._total_amount += amount