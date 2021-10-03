import random

from texas import common


class RandomAgent(common.BaseAgent):
    def __init__(self, big_blind, total_amount):
        super().__init__(big_blind, total_amount)
        self._rand = random.Random(0)

    def get_bet(self, open_bet, context, index):
        pr = self._rand.random()
        inner_action = common.InnerAction.Aggressive
        if pr < 0.33:
            inner_action = common.InnerAction.Conservative
        elif pr < 0.67:
            inner_action = common.InnerAction.Normal
        return self._wrap_return(*self._normalize_action_bet(inner_action, open_bet))


class StaticAgent(common.BaseAgent):
    def __init__(self, big_blind, total_amount, pr_calc, doubt_max_call=None):
        super().__init__(big_blind, total_amount)
        self.pr_calc = pr_calc
        self._doubt_max_call = doubt_max_call if doubt_max_call else big_blind * 10
        # cache
        self._cache = common.SingleCache()

    def start_new_game(self):
        super(StaticAgent, self).start_new_game()
        self._cache.reset()

    def get_bet(self, open_bet, context, index):
        num = context.num
        if self._cache.is_valid(context.round):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num)
            self._cache.set_value(context.round, pr)
        assert context.latest_bets[index] == self._latest_bet
        if pr < 0.5:
            if pr < 1.0 / num or open_bet >= self._doubt_max_call:
                inner_action = common.InnerAction.Conservative
            else:
                inner_action = common.InnerAction.Normal
        else:
            if open_bet >= self._doubt_max_call or open_bet == 0:
                inner_action = common.InnerAction.Normal
            else:
                inner_action = common.InnerAction.Aggressive
        return self._wrap_return(*self._normalize_action_bet(inner_action, open_bet))


class BraveAgent(common.BaseAgent):
    def __init__(self, big_blind, total_amount, pr_calc):
        super().__init__(big_blind, total_amount)
        self.pr_calc = pr_calc
        self._cache = common.SingleCache()

    def start_new_game(self):
        super(BraveAgent, self).start_new_game()
        self._cache.reset()

    def get_bet(self, open_bet, context, index):
        num = context.num
        if self._cache.is_valid(context.round):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num)
            self._cache.set_value(context.round, pr)
        assert context.latest_bets[index] == self._latest_bet
        if pr < 1.0 / num:
            inner_action = common.InnerAction.Conservative
        else:
            inner_action = common.InnerAction.Normal
        return self._wrap_return(*self._normalize_action_bet(inner_action, open_bet))
