"""
Solution1:
action: probability + amount
"""
from texas import common
import math
import enum


"""
实际：保守fold/check，基础call/bet，激进/raise，非常激进/raise_more，后三种都有可能遇到all_in
方案：内部一个状态，外部一个状态
"""
class InnerAction(enum.IntEnum):
    Conservative = 0
    Normal = 1
    Aggressive = 2
    Very_Aggressive = 3


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


class State4Quantizer(StateQuantizer):
    def quantize(self, pr, open_bet, remain_amt, context, index):
        _, latest_bet = context.get_action_bet(index)
        delta_bet = min(open_bet - latest_bet, remain_amt) # How much to bet
        total_amount = context.get_max_earning(delta_bet + latest_bet)

        return (
            StateQuantizer.quantize_pr(pr),
            StateQuantizer.quantize_amount(context.big_blind, total_amount),
            StateQuantizer.quantize_amount(context.big_blind, delta_bet),
            False,  # it's due to a bug, the trained model in 202010 is fact a state3quantizer
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
    TRIAL_NUM = 200

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

    def _get_inner_actions(self, open_bet, max_amount):
        avail_actions = [InnerAction.Conservative, InnerAction.Normal]
        base = self._big_blind if open_bet == 0 else open_bet
        if max_amount > base:
            avail_actions.append(InnerAction.Aggressive)
        if max_amount > base * 2:
            avail_actions.append(InnerAction.Very_Aggressive)
        return avail_actions

    def start_new_game(self):
        super(InnerKeyStateAgent, self).start_new_game()
        self._cache.reset()

    def get_bet(self, open_bet, context, index):
        num = context.num
        # action
        if self._cache.is_valid(context.round):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num, InnerKeyStateAgent.TRIAL_NUM)
            self._cache.set_value(context.round, pr)
        assert context.latest_bets[index] == self._latest_bet
        state = self.state_quantizer.quantize(pr, open_bet, self._total_amount - self._cum_amount, context, index)
        remain_amount = (self._total_amount - self._cum_amount) + self._latest_bet
        inner_action = self.q_learner.get_action(state, self._get_inner_actions(open_bet, remain_amount),
                                                 None if self.is_test else 1)
        if self.last_action is not None:
            self.q_learner.update(self.last_state, self.last_action, state, 0)
        self.last_state = state
        self.last_action = inner_action
        return self._wrap_return(*self._get_action_and_bet(inner_action, open_bet))

    def _get_action_and_bet(self, action, open_bet):
        if open_bet == 0:
            if action == InnerAction.Conservative:
                return common.AgentAction.Check, 0
            if action == InnerAction.Normal:
                return common.AgentAction.Bet, self._big_blind
            if action == InnerAction.Aggressive:
                return common.AgentAction.Bet, self._big_blind * 2
            if action == InnerAction.Very_Aggressive:
                return common.AgentAction.Bet, self._big_blind * 4
        else:
            if action == InnerAction.Conservative:
                if self._latest_bet == open_bet:  # only big-blind can reach here
                    return common.AgentAction.Call, self._latest_bet
                return common.AgentAction.Fold, self._latest_bet,
            if action == InnerAction.Normal:
                return common.AgentAction.Call, open_bet,
            if action == InnerAction.Aggressive:
                return common.AgentAction.Raise, open_bet * 2
            if action == InnerAction.Very_Aggressive:
                return common.AgentAction.Raise_more, open_bet * 4

    def set_reward(self, amount):
        super().set_reward(amount)
        self.q_learner.update(self.last_state, self.last_action, None, amount)
