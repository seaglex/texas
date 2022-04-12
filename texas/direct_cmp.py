"""
Estimate wining rate based on community cards and hole cards
"""
from .judge import TexasLevel
from .direct_calc import ApproxCalc


class ApproxComparer(object):
    def get_pr(self, hole_cards, common_cards=None, player_num=2):
        common_cards = [] if common_cards is None else common_cards
        calc = ApproxCalc()
        my_level_prs = calc.get_level_prs(hole_cards + common_cards)
        other_level_prs = calc.get_level_prs(common_cards)
        prs = []
        for level in list(TexasLevel):
            prs.append((
                my_level_prs.get(level, 0.0),
                1 - (1.0 - other_level_prs.get(level, 0.0)) ** player_num,
                0.5, # the digit is ignored
            ))
        return self._get_winning_pr(prs)

    def _get_winning_pr(self, prs):
        winning_pr = 1.0
        pr_others_are_higher = 0.0
        for my_pr, other_pr, pr_win_in_same_level in prs:
            pr_others_are_same_or_higher = 1 - (1 - pr_others_are_higher) * (1 - other_pr)
            # others are lower level or I win in this level
            winning_in_this_level = my_pr * (
                    1 - pr_others_are_same_or_higher
                    + (pr_others_are_same_or_higher - pr_others_are_higher) * pr_win_in_same_level
            )
            pr_others_are_higher = pr_others_are_same_or_higher
            winning_pr *= (1 - winning_in_this_level)
        return 1 - winning_pr
