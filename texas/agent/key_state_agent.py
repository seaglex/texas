"""
Solution1:
state: probability + amount
"""
from texas import common
import math


class StateQuantizer(object):
    @staticmethod
    def quantize_pr(pr):
        return int(pr/0.1)

    @staticmethod
    def quantize_amount(big_blind, amount):
        if amount == 0:
            return -1
        return int(math.log2(amount / big_blind))

    @staticmethod
    def quantize_num(num):
        if num == 0:
            return -1
        return int(math.log2(num))


class State4Quantizer(StateQuantizer):
    def quantize(self, pr, hand_bet, context, index):
        latest_bet = context.latest_bets[index]
        total_amount = context.total_pot  # How much to earn (before this round)
        for bet in context.latest_bets:
            total_amount += bet
        delta_bet = hand_bet - latest_bet  # How much to bet
        num_left = 0
        num_all_in= 0
        for n in range(context.num):
            if context.latest_states[n] != common.AgentState.Fold:
                num_left += 1
            elif context.latest_states[n] == common.AgentState.All_in:
                num_all_in += 1
        return (
            StateQuantizer.quantize_pr(pr),
            StateQuantizer.quantize_amount(context.big_blind, total_amount),
            StateQuantizer.quantize_amount(context.big_blind, delta_bet),
            num_all_in > 0,
        )



class KeyStateAgent(common.BaseAgent):
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

    def get_bet(self, hand_bet, context, index):
        num = context.num
        # state
        if self._cache.is_valid(len(self._community_cards)):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num, KeyStateAgent.TRIAL_NUM)
            self._cache.set_value(len(self._community_cards), pr)
        state = self.state_quantizer.quantize(pr, hand_bet, context, index)
        action = self.q_learner.get_action(state, common.AgentState.get_normal_actions(hand_bet),
                                           None if self.is_test else 1)
        if self.last_action is not None:
            self.q_learner.update(self.last_state, self.last_action, state, 0)
        self.last_state = state
        self.last_action = action
        return self._wrap_return(action, self._get_bet(action, hand_bet))

    def _get_bet(self, action, hand_bet):
        return {
            common.AgentState.Fold: self._latest_bet,
            common.AgentState.Check: 0,
            common.AgentState.Bet: self._big_blind,
            common.AgentState.Call: hand_bet,
            common.AgentState.Raise: hand_bet * 2,
            common.AgentState.Raise_more: hand_bet * 4,
            common.AgentState.All_in: self._total_amount - self._cum_amount
        }.get(action)

    def set_reward(self, amount):
        super().set_reward(amount)
        self.q_learner.update(self.last_state, self.last_action, None, amount)
