from collections import defaultdict
import math

from .poker import PokerDigit, PokerKind, PokerCard

class PrTools(object):
    @staticmethod
    def get_pr(num, k):
        # 1 / choose(n, k)
        return 1.0 / math.comb(num, k)

class ApproxCalc(object):
    MAX_CARD_SIZE = 7
    MIN_CARD_SIZE = 2
    SUIT_SIZE = 5
    TOTAL_SIZE = 13 * 4

    # 皇家同花顺 和 同花顺 可以一起比较
    straight_flush = 9   # 同花顺
    four = 8             # 4条
    full_house = 7       # 葫芦(3 + 2)
    flush = 6            # 同花
    straight = 5         # 顺子
    three = 4            # 3条
    two_pairs = 3        # 两对
    pair = 2             # 对子
    high_card = 1        # 高牌

    def get_level_prs(self, hole_cards, community_cards=None):
        if community_cards is None:
            community_cards = []
        cards = hole_cards + community_cards
        num = len(cards)
        kind_digits = self.count_kind_stats(cards)
        results = self.get_straight_flush_prs(kind_digits, self.MAX_CARD_SIZE - num, self.TOTAL_SIZE - num)
        if results:
            print(sum(x[0] for x in results))
        return results

    def count_kind_stats(self, cards):
        assert self.MIN_CARD_SIZE <= len(cards) < self.MAX_CARD_SIZE
        # statistics
        kind_digits = {}
        last_kind = PokerKind.unknown
        digits = []
        cards = list(sorted(cards, key=lambda c: (c[0] << 4) + c[1], reverse=True))
        for kind, digit in cards:
            if kind != last_kind:
                if digits:
                    kind_digits[last_kind] = digits
                last_kind = kind
            digits.append(digit)
        kind_digits[last_kind] = digits
        return kind_digits

    def get_straight_flush_prs(self, kind_digits, num_to_check, num_left):
        results = []
        for _, digits in kind_digits.items():
            results += self.get_single_straight_flush_prs(digits, num_to_check, num_left)
        return results

    def _get_single_straight_flush_pr_st(
            self, exclusive_upper, exclusive_below, left, right, num_len, num_to_check, num_left
    ):
        # 必须包含left, right，不能包含exclusive_upper或exclusive_below
        gap = left - right + 1
        if gap > self.SUIT_SIZE:  # two large gap
            return False, None

        if gap == self.SUIT_SIZE:
            # 从剩余中选择 num_to_check 个
            pr = PrTools.get_pr(num_left, num_to_check)
            return True, (pr, left)

        if exclusive_upper - exclusive_below - 1 == self.SUIT_SIZE:
            # 恰好空间够
            pr = PrTools.get_pr(num_left, num_to_check)
            return True, (pr, exclusive_upper - 1)
        elif exclusive_upper - exclusive_below - 1 < self.SUIT_SIZE:
            return False, None
        # 空间充足
        left_space = exclusive_upper - left - 1
        right_space = right - exclusive_below - 1
        all_space = self.SUIT_SIZE - gap
        max_d = left + min(all_space, left_space)
        min_d = right - min(all_space, right_space)
        must_num = gap - num_len
        # 内部数字必选，外部数字，N个数，选出连续的5个，一共N - 5 + 1种
        pr = PrTools.get_pr(num_left, must_num) * PrTools.get_pr(
            num_left - must_num, num_to_check - must_num
        ) * (max_d - min_d + 1 - self.SUIT_SIZE + 1)
        return True, (pr, (max_d, min_d + self.SUIT_SIZE - 1))

    def get_single_straight_flush_prs(self, digits, num_to_check, num_left):
        results = []
        if len(digits) + num_to_check < self.SUIT_SIZE:
            return results
        min_num = self.SUIT_SIZE - num_to_check
        assert min_num >= 0
        for beg_n in range(len(digits) - min_num):
            if beg_n == 0:
                exclusive_upper = PokerDigit.A + 1
            else:
                exclusive_upper = digits[beg_n - 1]
            for end_n in range(beg_n + max(min_num, 1), len(digits) + 1):
                # digits[beg_n] and digits[end_n - 1] are both included
                # digits[beg_n - 1] and digits[end_n] are not included
                if end_n == len(digits):
                    exclusive_below = 1 if digits[0] == PokerDigit.A else 0
                else:
                    exclusive_below = digits[end_n]
                flag, result = self._get_single_straight_flush_pr_st(
                    exclusive_upper, exclusive_below, digits[beg_n], digits[end_n - 1], end_n - beg_n,
                    num_to_check, num_left)
                if flag:
                    results.append(result)
            pass
        pass
        if digits[0] != PokerDigit.A:
            return results
        for beg_n in range(1, len(digits)):
            exclusive_upper = digits[beg_n - 1]
            exclusive_below = 0
            flag, result = self._get_single_straight_flush_pr_st(
                exclusive_upper, exclusive_below, digits[beg_n], 1, len(digits) - beg_n + 1,
                num_to_check, num_left
            )
            if flag:
                results.append(result)
        pass
        return results
