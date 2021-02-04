from texas import common


class StaticAgent(common.BaseAgent):
    TRIAL_NUM = 200

    def __init__(self, big_blind, total_amount, pr_calc, doubt_max_call=None):
        super().__init__(big_blind, total_amount)
        self.pr_calc = pr_calc
        self._doubt_max_call = doubt_max_call if doubt_max_call else big_blind * 10
        # cache
        self._cache = common.SingleCache()

    def get_bet(self, open_bet, context, index):
        num = context.num
        if self._cache.is_valid(len(self._community_cards)):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num, StaticAgent.TRIAL_NUM)
            self._cache.set_value(len(self._community_cards), pr)
        if pr < 1.0 / num:
            if open_bet == 0:
                return self._wrap_return(common.AgentState.Check, 0)
            else:
                return self._wrap_return(common.AgentState.Fold, self._latest_bet)
        if pr < 0.5:
            if open_bet == 0:
                return self._wrap_return(common.AgentState.Check, 0)
            if open_bet > 0:
                if open_bet < self._doubt_max_call:
                    return self._wrap_return(common.AgentState.Call, open_bet)
                else:
                    return self._wrap_return(common.AgentState.Fold, self._latest_bet)
        # high rate to win
        if open_bet == 0:
            return self._wrap_return(common.AgentState.Bet, self._big_blind)
        return self._wrap_return(common.AgentState.Raise, open_bet * 2)


class BraveAgent(common.BaseAgent):
    TRIAL_NUM = 200

    def __init__(self, big_blind, total_amount, pr_calc):
        super().__init__(big_blind, total_amount)
        self.pr_calc = pr_calc
        self._cache = common.SingleCache()

    def get_bet(self, open_bet, context, index):
        num = context.num
        if self._cache.is_valid(len(self._community_cards)):
            pr = self._cache.get_value()
        else:
            pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num, BraveAgent.TRIAL_NUM)
            self._cache.set_value(len(self._community_cards), pr)
        if pr < 1.5 / num:
            if open_bet == 0:
                return self._wrap_return(common.AgentState.Check, 0)
            else:
                return self._wrap_return(common.AgentState.Fold, self._latest_bet)
        if open_bet == 0:
            return self._wrap_return(common.AgentState.Check, 0)
        return self._wrap_return(common.AgentState.Call, open_bet)
