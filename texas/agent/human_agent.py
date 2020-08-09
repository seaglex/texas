from texas.poker import PokerCard
from texas import common


class HumanAgent(common.BaseAgent):
    def __init__(self, big_blind, total_amount, pr_calc=None):
        super().__init__(big_blind, total_amount)
        self._pr_calc = pr_calc

    @staticmethod
    def _read_amount(hand_bet, check):
        while True:
            amount_str = input("amount(bet={0} now):".format(hand_bet))
            try:
                amount = int(amount_str)
                if check(amount):
                    return amount
                else:
                    print("Wrong number")
            except ValueError:
                print("Wrong number")

    def get_bet(self, hand_bet, context, index):
        while True:
            state_str = input("F(old)/C(heck)/C(all)/B(et)/R(aise)/A(ll-in)): ")
            state_str = state_str.lower()
            if state_str in ("f", "fold"):
                return self._wrap_return(common.AgentState.Fold, self._latest_bet)
            if state_str in ("c", "check", "call"):
                if hand_bet == 0:
                    return self._wrap_return(common.AgentState.Check, 0)
                return self._wrap_return(common.AgentState.Call, hand_bet)
            if hand_bet == 0 and state_str in ("b", "bet"):
                amount = self._read_amount(hand_bet, lambda x: x >= self._big_blind)
                return self._wrap_return(common.AgentState.Bet, amount)
            if hand_bet > 0 and state_str in ("r", "raise"):
                amount = self._read_amount(hand_bet, lambda x: x >= hand_bet * 2)
                return self._wrap_return(common.AgentState.Raise, amount)
            if state_str in ("a", "all-in", "allin", "all_in"):
                return self._wrap_return(common.AgentState.All_in, self._total_amount - self._cum_amount)
            print("Wrong input")

    def get_hole_cards(self, hold_cards):
        print("You get", ' '.join(str(PokerCard(*c)) for c in hold_cards))
        super().get_hole_cards(hold_cards)
