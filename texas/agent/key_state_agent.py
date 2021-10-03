"""
Solution1:
action: probability + amount
"""
from texas import common
from texas.common import InnerAction
import math


class StateQuantizer(object):
    @staticmethod
    def quantize_pr(pr):
        return int(pr/0.1)

    @staticmethod
    def quantize_amount(big_blind, amount):
        if amount == 0:
            return -1
        return min(int(math.log2(amount / big_blind)), 8)

    @staticmethod
    def quantize_num(num):
        if num <= 3:
            return num
        return 4


class State2Quantizer(StateQuantizer):
    def quantize(self, pr, open_bet, remain_amt, context, index):
        return (
            StateQuantizer.quantize_pr(pr),
            context.round,
        )


class State3Quantizer(StateQuantizer):
    def quantize(self, pr, open_bet, remain_amt, context, index):
        _, latest_bet = context.get_action_bet(index)
        delta_bet = min(open_bet - latest_bet, remain_amt) # How much to bet
        total_amount = context.get_max_earning(delta_bet + latest_bet)

        return (
            StateQuantizer.quantize_pr(pr),
            StateQuantizer.quantize_amount(context.big_blind, total_amount),
            StateQuantizer.quantize_amount(context.big_blind, delta_bet),
        )


class State5Quantizer(StateQuantizer):
    def quantize(self, pr, open_bet, remain_amt, context, index):
        _, latest_bet = context.get_action_bet(index)
        delta_bet = min(open_bet - latest_bet, remain_amt) # How much to bet
        total_amount = context.get_max_earning(delta_bet + latest_bet)

        num_left = context.num_left
        return (
            context.round,
            StateQuantizer.quantize_pr(pr),
            StateQuantizer.quantize_amount(context.big_blind, total_amount),
            StateQuantizer.quantize_amount(context.big_blind, delta_bet),
            StateQuantizer.quantize_num(num_left),
        )


class InnerKeyStateAgent(common.BaseAgent):
    def __init__(self, big_blind, total_amount, pr_calc, state_quantizer, q_learner):
        super().__init__(big_blind, total_amount)
        self.pr_calc = pr_calc
        self.state_quantizer = state_quantizer
        self.q_learner = q_learner
        self.last_state = None
        self.last_action = None
        # flag
        self.is_test = False
        # cache
        self._cache = common.SingleCache()

    def _get_inner_actions(self):
        return [InnerAction.Conservative, InnerAction.Normal, InnerAction.Aggressive, InnerAction.Very_Aggressive]

    def start_new_game(self):
        super(InnerKeyStateAgent, self).start_new_game()
        self._cache.reset()

    def get_bet(self, open_bet, context, index):
        num = context.num
        # action
        if self._cache.is_valid(context.round):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num)
            self._cache.set_value(context.round, pr)
        assert context.latest_bets[index] == self._latest_bet
        state = self.state_quantizer.quantize(pr, open_bet, self._total_amount - self._cum_amount, context, index)
        remain_amount = (self._total_amount - self._cum_amount) + self._latest_bet
        inner_action = self.q_learner.get_action(state, self._get_inner_actions(),
                                                 None if self.is_test else 1)
        if self.last_action is not None:
            self.q_learner.update(self.last_state, self.last_action, state, 0)
        self.last_state = state
        self.last_action = inner_action
        return self._wrap_return(*self._normalize_action_bet(inner_action, open_bet))

    def set_reward(self, amount):
        super().set_reward(amount)
        self.q_learner.update(self.last_state, self.last_action, None, amount)
