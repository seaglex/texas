"""
直接估计最后各level概率
方法：
1. 遍历所有满足的牌型，比如A2345 23456 34567 ... 10JQKA
2. 每一种牌型，基于当前hole cards，计算概率
3. 假设牌型之间独立, 1 - ∏ (1 -pr(牌型 | hole cards))
   这不是在任何地方都完美的假设，比如straight，但是暂时选择独立假设，因为加性假设容易出大于1的概率
   - 各种牌型之间并非独立(∏)，A2345和23456必然相关
   - 也不是exclusive(+)，A23456就同时满足A2345和23456
"""
from collections import defaultdict
import math

from .poker import PokerDigit, PokerSymbol, PokerConst
from .judge import TexasLevel
from .common import TexasConst


class StraightFlushTool(object):
    def pr_choose_target(self, num, m, t):
        # choose m cards out of num, t specified cards are in them
        # choose(n-t, m-t) / choose(n, m)
        # = ( (n-t)! / ((m-t)! (n-m)!) ) / ( n! / (m! (n-m)!) )
        # = (n-t)! m! / ( n! (m-t)!) )
        # eg. 50张选5张，恰好有H3H4概率，5/50 * 4/49
        if t > m:
            return 0.0
        pr = 1.0
        for x in range(t):
            pr *= (m - x) / (num - x)
        return pr


class StraightApproxTool(object):
    # approximation
    def pr_choose_target(self, num, m, t):
        # choose m cards out of num, t specified digits are in them
        # 考虑t=1
        # 1 - choose(n-4, m) / choose(n, m)
        # = 1 - (n-4)! m! (n-m)! / ( m! (n-4-m)! n!)
        # = 1 - (n-4)! (n-m)! / ((n-m-4)! n!)
        # ≈ 1 - ((n-m)/n) ** 4
        # 两个近似
        # 1. 如上简化计算，缩小了结果
        # 2. 考虑第t个数字时，假设已经消耗了t张（实际可能消耗超过t张），放大了结果
        if t > m:
            return 0.0
        pr = 1.0
        for x in range(t):
            pr *= 1 - ((num - m - t) / (num - t)) ** 4
        return pr


class FlushNumTool(object):
    """
    For number/number combination, it's approximate
    eg. 3+3 包含2个full house
    """
    def pr_choose_target_in_subset(self, num, m, num1, t1):
        # choose m cards out of num, and at least t1 are out of num1 (subset of num)
        # choose(num1, t1) * choose(num - num1, m - t1) / choose(num, m)
        # = num1 ! (num-num1)! m! (num-m)! / ( t1! (num1-t1)! (m-t1)! (num-num1-m + t1)! num! )
        # = choose(m, t1) choose(num-m, num-t1) / choose(num, num1)
        if m < t1:
            return 0.0
        pr = 0.0
        for x in range(t1, min(m, num1) + 1):
            pr += math.comb(num1, x) * math.comb(num - num1, m - x) / math.comb(num, m)
        return pr

    def pr_choose_2targets_in_subsets(self, num, m, num1, t1, num2, t2):
        # choose m cards out of num, and at least t1 are out of num1, and at least t2 are out of num2
        if t1 + t2 > m:
            return 0.0
        pr = 0.0
        for x1 in range(t1, min(m - t2, num1) + 1):
            for x2 in range(t2, min(m - t1, num2) + 1):
                if x1 + x2 > m:
                    continue
                pr += math.comb(num1, x1) * math.comb(num2, x2) * math.comb(
                    num - num1 - num2, m - x1 - x2) / math.comb(num, m)
        return pr


class ApproxCalc(object):
    @staticmethod
    def count_sym_digits(cards):
        """
        :return: {symbol: sorted-digits}
        """
        # statistics
        sym_digits = {}
        last_sym = PokerSymbol.unknown
        digits = []
        cards = list(sorted(cards, key=lambda c: (c[0] << 4) + c[1]))
        for sym, digit in cards:
            if sym != last_sym:
                if digits:
                    sym_digits[last_sym] = digits
                    digits = []
                last_sym = sym
            digits.append(digit)
        sym_digits[last_sym] = digits
        return sym_digits

    @staticmethod
    def count_unique_digits(cards):
        """
        :return: sorted-unique-digits
        """
        # statistics
        digits = []
        all_digits = sorted([c[1] for c in cards])
        last_digit = PokerDigit.unknown
        for digit in all_digits:
            if digit != last_digit:
                digits.append(digit)
                last_digit = digit
        return digits

    @staticmethod
    def count_symbols(cards):
        """
        :return: {symbol: count}, {symbol, max-digit}
        """
        sym_counts = defaultdict(int)
        sym_max_digits = {}
        for c in cards:
            sym_counts[c[0]] += 1
            if c[0] not in sym_max_digits:
                sym_max_digits[c[0]] = c[1]
            else:
                sym_max_digits[c[0]] = max(c[1], sym_max_digits[c[0]])
        return sym_counts, sym_max_digits

    @staticmethod
    def count_digits(cards):
        """
        :return: [(digit: count)], sorted by digit
        """
        digit_counts = defaultdict(int)
        for _, digit in cards:
            digit_counts[digit] += 1
        digit_counts = list(sorted(digit_counts.items(), key=lambda c: c[1]))
        return digit_counts

    def get_level_prs(self, cards):
        digit_counts = ApproxCalc.count_digits(cards)
        return {
            TexasLevel.straight_flush: self.get_straight_flush_pr(cards),
            TexasLevel.four:           self.get_num_pr(digit_counts, 4),
            TexasLevel.full_house:     self.get_num_combination_pr(digit_counts, 3, 2),
            TexasLevel.straight:       self.get_straight_pr(cards),
            TexasLevel.flush:          self.get_flush_pr(cards),
            TexasLevel.three:          self.get_num_pr(digit_counts, 3),
            TexasLevel.two_pairs:      self.get_num_combination_pr(digit_counts, 2, 2),
            TexasLevel.pair:           self.get_num_pr(digit_counts, 2),
        }

    def get_straight_flush_pr(self, cards):
        num_left = TexasConst.TOTAL_NUM - len(cards)
        num_to_check = TexasConst.MAX_HAND_SIZE - len(cards)
        # A and 1 never in the same straight
        cards = cards + [(c[0], PokerDigit.A_MINUS) for c in cards if c[1] == PokerDigit.A]
        sym_digits = ApproxCalc.count_sym_digits(cards)
        tool = StraightFlushTool()

        # pr(winning) = 1 - pr(fail all the possibility)
        # 独立假设没问题
        pr = 1.0
        for _, digits in sym_digits.items():
            pr *= 1 - self._ana_single_straight_pr(digits, num_to_check, num_left, tool)
        pr *= (1 - self._ana_single_straight_pr([], num_to_check, num_left, tool)) ** (4 - len(sym_digits))
        return 1 - pr

    def get_straight_pr(self, cards):
        num_left = TexasConst.TOTAL_NUM - len(cards)
        num_to_check = TexasConst.MAX_HAND_SIZE - len(cards)
        # A and 1 never in the same straight
        cards = cards + [(c[0], PokerDigit.A_MINUS) for c in cards if c[1] == PokerDigit.A]
        digits = self.count_unique_digits(cards)
        return self._ana_single_straight_pr(digits, num_to_check, num_left, StraightApproxTool())

    def get_flush_pr(self, cards):
        num_left = TexasConst.TOTAL_NUM - len(cards)
        num_to_check = TexasConst.MAX_HAND_SIZE - len(cards)
        sym_counts, sym_max_digits = ApproxCalc.count_symbols(cards)
        tool = FlushNumTool()
        # pr(winning) = 1 - pr(fail all the possibility)
        # 独立性假设没问题
        pr = 1.0
        for sym, cnt in sym_counts.items():
            if cnt >= TexasConst.BEST_HAND_SIZE:
                return 1.0
            target_cnt = TexasConst.BEST_HAND_SIZE - cnt
            pr *= 1 - tool.pr_choose_target_in_subset(num_left, num_to_check, PokerConst.DIGIT_NUM - cnt, target_cnt)
        pr *= (1 - tool.pr_choose_target_in_subset(
            num_left, num_to_check, PokerConst.DIGIT_NUM, TexasConst.BEST_HAND_SIZE
        )) ** (4 - len(sym_counts))
        return 1 - pr

    def get_num_pr(self, digit_counts, num):
        # Four, three, pair
        # use digit_counts for efficiency
        card_num = sum(dc[1] for dc in digit_counts)
        num_left = TexasConst.TOTAL_NUM - card_num
        num_to_check = TexasConst.MAX_HAND_SIZE - card_num
        tool = FlushNumTool()

        # pr(winning) = 1 - pr(fail all the possibility)
        # 独立性假设没问题
        pr = 1.0
        for digit, cnt in digit_counts:
            if cnt >= num:
                return 1.0
            pr *= 1 - tool.pr_choose_target_in_subset(num_left, num_to_check, 4 - cnt, num - cnt)
        if num_to_check >= num:
            pr *= (1 - tool.pr_choose_target_in_subset(num_left, 4, num_to_check, num)) ** (
                    PokerConst.DIGIT_NUM - len(digit_counts))
        return 1 - pr

    def get_num_combination_pr(self, digit_counts, num1, num2):
        # full house, two pair
        # use digit_counts for efficiency
        card_num = sum(dc[1] for dc in digit_counts)
        num_left = TexasConst.TOTAL_NUM - card_num
        num_to_check = TexasConst.MAX_HAND_SIZE - card_num
        tool = FlushNumTool()

        # pr(winning) = 1 - pr(fail all the possibility)
        # 独立性假设没问题
        pr = 1.0
        # 2 - combination
        for i, (d1, cnt1) in enumerate(digit_counts):
            for d2, cnt2 in digit_counts[i+1:]:
                if cnt1 >= num1 and cnt2 >= num2:
                    return 1.0
                elif cnt1 >= num1:
                    pr *= 1 - tool.pr_choose_target_in_subset(num_left, num_to_check, 4 - cnt2, num2 - cnt2)
                elif cnt2 >= num2:
                    pr *= 1 - tool.pr_choose_target_in_subset(num_left, num_to_check, 4 - cnt1, num1 - cnt1)
                else:
                    pr *= 1 - tool.pr_choose_2targets_in_subsets(
                        num_left, num_to_check, 4 - cnt1, num1 - cnt1, 4 - cnt2, num2 - cnt2
                    )
        # 1 - combination
        for d1, cnt1 in digit_counts:
            if cnt1 >= num1:
                if num2 <= num_to_check:
                    pr *= (1 - tool.pr_choose_target_in_subset(num_left, num_to_check, 4, num2)) ** (
                        PokerConst.DIGIT_NUM - len(digit_counts))
            elif num1 - cnt1 + num2 <= num_to_check:
                pr *= (1 - tool.pr_choose_2targets_in_subsets(num_left, num_to_check, 4 - cnt1, num1 - cnt1, 4, num2)
                       ) ** (PokerConst.DIGIT_NUM - len(digit_counts))
        if num1 + num2 <= num_to_check:
            pr *= (1 - tool.pr_choose_2targets_in_subsets(num_left, num_to_check, 4, num1, 4, num2)) ** (
                PokerConst.DIGIT_NUM * (PokerConst.DIGIT_NUM - 1) / 2
                - len(digit_counts) * (len(digit_counts) - 1) / 2
                - len(digit_counts) * (PokerConst.DIGIT_NUM - len(digit_counts))
            )
        return 1 - pr

    def _ana_single_straight_pr(self, digits, num_to_check, num_left, tool):
        if len(digits) + num_to_check < TexasConst.BEST_HAND_SIZE:
            return 0.0
        total_count = (PokerDigit.A - PokerDigit.A_MINUS + 1) - (TexasConst.BEST_HAND_SIZE - 1)
        if not digits:
            return tool.pr_choose_target(num_left, num_to_check, TexasConst.BEST_HAND_SIZE) * total_count
        beg_idx = 0
        end_idx = 1
        valid_num_counts = defaultdict(int)
        min_beg = max(TexasConst.MIN_DIGIT, digits[0] - TexasConst.BEST_HAND_SIZE + 1)
        max_beg = digits[-1]
        for beg in range(min_beg, max_beg + 1):
            end = beg + TexasConst.BEST_HAND_SIZE
            # find the inclusive beg position, where the digit in [beg, end)
            while beg_idx < len(digits) and digits[beg_idx] < beg:
                beg_idx += 1
            if beg_idx >= len(digits):
                break
            # find the exclusive end position, where the digit >= end
            while end_idx < len(digits) and digits[end_idx] < end:
                end_idx += 1
            # a valid range beg-end
            valid_num_counts[end_idx - beg_idx] += 1
        # pr(winning) = 1 - pr(fail all the possibility)
        # 独立性假设，稍稍低估（采用）
        # 互斥性假设，稍稍高估
        pr = 1.0
        for valid_num, cnt in valid_num_counts.items():
            if valid_num >= TexasConst.BEST_HAND_SIZE:
                return 1.0
            pr *= (1 - tool.pr_choose_target(num_left, num_to_check, TexasConst.BEST_HAND_SIZE - valid_num)) ** cnt
            total_count -= cnt
        pr *= (1 - tool.pr_choose_target(num_left, num_to_check, TexasConst.BEST_HAND_SIZE)) ** total_count
        return 1 - pr
