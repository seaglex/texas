from texas import common


class StaticAgent(common.BaseAgent):
    TRIAL_NUM = 1000

    def __init__(self, big_blind, total_amount, pr_calc, doubt_max_call=None):
        super().__init__(big_blind, total_amount)
        self.pr_calc = pr_calc
        self._doubt_max_call = doubt_max_call if doubt_max_call else big_blind * 5

    def get_bet(self, hand_bet, context, index):
        num = context.num
        pr = self.pr_calc.get_pr(self._hole_cards, self._community_cards, num, StaticAgent.TRIAL_NUM)
        if pr < 1.0 / num:
            if hand_bet == 0:
                return self._wrap_return(common.AgentState.Check, 0)
            else:
                return self._wrap_return(common.AgentState.Fold, self._latest_bet)
        if pr < 0.5:
            if hand_bet == 0:
                return self._wrap_return(common.AgentState.Check, 0)
            if hand_bet > 0:
                if hand_bet < self._doubt_max_call:
                    return self._wrap_return(common.AgentState.Call, hand_bet)
                else:
                    return self._wrap_return(common.AgentState.Fold, self._latest_bet)
        # high rate to win
        if hand_bet == 0:
            return self._wrap_return(common.AgentState.Bet, self._big_blind)
        return self._wrap_return(common.AgentState.Raise, hand_bet * 2)