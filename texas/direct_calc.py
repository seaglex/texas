from collections import defaultdict
import math

from .poker import PokerDigit, PokerKind, PokerCard


class StraightFlushTool(object):
    def pr_choose_k(self, num, m, k):
        # 从num中选m张，恰好有k个数字的概率，k个数字每个都是确定花色
        # choose(n-k, m-k) / choose(n, m)
        # = ( (n-k)! / ((m-k)! (n-m)!) ) / ( n! / (m! (n-m)!) )
        # = (n-k)! m! / ( n! (m-k)!) )
        # eg. 50张选5张，恰好有H3H4概率，5/50 * 4/49
        pr = 1.0
        for x in range(k):
            pr *= (m - x) / (num - x)
        return pr

    def pr_choose_k_excl_r(self, num, m, k, r):
        # 从num中选m张，恰好有k个数字，并且不含r个数字的概率，k个数字每个都是确定花色
        # choose(n-k-consecutive, m-k) / choose(n, m)
        # = ( (n-k-consecutive)! / ((m-k)! (n-m-consecutive)!) ) / ( n! / (m! (n-m)!) )
        # = (n-m)! m! (n-k-consecutive)! / ( n! (m-k)! (n-m-consecutive)!) )
        pr = 1.0
        for x in range(k):
            pr *= (m - x) / (num - x)
        for x in range(r):
            pr *= (num - m - x) / (num - k - x)
        return pr

    def pr_choose_consecutive_k(self, num, m, consecutive, k):
        # 从num个数中随机选m个数，其中至少k个数是r个连续数中的连续一段的概率
        # r个数中可能选k, ..., min(consecutive, m)
        pr = 0.0
        for cnt in range(k, min(consecutive, m) + 1):
            # 从num个数中随机选m个数，其中恰好cnt个数是r个连续数中的连续一段的概率
            pr += self.pr_choose_k_excl_r(num, m, cnt, consecutive - cnt) * (consecutive - cnt + 1)
        return pr


class StraightApproxTool(object):
    # 粗略估计
    def pr_choose_k(self, num, m, k):
        # 从num中选m张，恰好有k个数字的概率，每个数字可以从4个花色中选
        # 考虑k=1
        # 1 - choose(n-4, m) / choose(n, m)
        # = 1 - (n-4)! m! (n-m)! / ( m! (n-4-m)! n!)
        # = 1 - (n-4)! (n-m)! / ((n-m-4)! n!)
        # ≈ 1 - ((n-m)/n) ** 4
        # 两个近似
        # 1. 如上简化计算，缩小了结果
        # 2. 考虑第k个数字时，假设已经消耗了k张（实际可能消耗超过k张），放大了结果
        pr = 1.0
        for x in range(k):
            pr *= 1 - ((num - m - k) / (num - k)) ** 4
        return pr

    def pr_choose_k_excl_r(self, num, m, k, r):
        pr = self.pr_choose_k(num - r * 4, m, k)
        return pr * (((num - r * 4) / num) ** m)

    def pr_choose_consecutive_k(self, num, m, consecutive, k):
        # 从num个数中随机选m个数，其中至少k个数是r个连续数中的连续一段的概率
        # r个数中可能选k, .., min(consecutive, m)
        pr = 0.0
        for cnt in range(k, min(consecutive, m) + 1):
            # 从num个数中随机选m个数，其中恰好cnt个数是r个连续数中的连续一段的概率
            # choose(n-cnt, m-cnt) / choose(n, m) * (consecutive - cnt + 1)
            pr += self.pr_choose_k_excl_r(num, m, cnt, consecutive - cnt) * (consecutive - cnt + 1)
        return pr


class FlushTool(object):
    def pr_choose_k(self, num, avail_num, k):
        # num个数选k个，恰好来自avail_num
        # choose(avail_num, k) / choose(num, k)
        # = avail_num! k! (num-k)! / (k! (avail_num - k)! num!)
        # = avail_num! (num-k)! / ((avail_num - k)! num!)
        pr = 1.0
        for x in range(k):
            pr *= (avail_num - x) / (num - x)
        return pr

    def pr_choose_k_to_s(self, num, avail_num, k, s):
        # num个数选k-s个，恰好来自avail_num
        # 小球不放回 + 两种颜色
        # 3红3蓝，不放回拿3次，恰好2红1蓝，3 * 3 / 6 * 5 * 4
        # choose(avail_num, k) * choose(num-avail_num, s-k) / choose(num, s)
        # = avail_num ! (num-avail_num)! s! (num-s)! / ( k! (avail_num-k)! (s-k)! (num-avail_num-s + k)! num! )
        # = choose(s, k) choose(num-s, avail_num-k) / choose(num, avail_num)
        pr = 0.0
        for x in range(k, s+1):
            pr += math.comb(avail_num, x) * math.comb(num - avail_num, s - x) / math.comb(num, s)
        return pr

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
        kind_digits = self.count_kind_digits(cards)
        results = self.get_straight_flush_prs(kind_digits, self.MAX_CARD_SIZE - num, self.TOTAL_SIZE - num)
        if results:
            print(sum(x[0] for x in results))
        return results

    def count_kind_digits(self, cards):
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
                    digits = []
                last_kind = kind
            digits.append(digit)
        kind_digits[last_kind] = digits
        return kind_digits

    def count_digits(self, cards):
        assert self.MIN_CARD_SIZE <= len(cards) < self.MAX_CARD_SIZE
        # statistics
        digits = []
        cards = list(sorted(cards, key=lambda c: c[1], reverse=True))
        last_digit = PokerDigit.unknown
        for _, digit in cards:
            if digit != last_digit:
                digits.append(digit)
        return digits

    def count_kinds(self, cards):
        assert self.MIN_CARD_SIZE <= len(cards) < self.MAX_CARD_SIZE
        kind_counts = defaultdict(int)
        kind_max_digits = {}
        for c in cards:
            kind_counts[c[0]] += 1
            if c[0] not in kind_max_digits:
                kind_max_digits[c[0]] = c[1]
            else:
                kind_max_digits[c[0]] = max(c[1], kind_max_digits[c[0]])
        return kind_counts, kind_max_digits

    def get_straight_flush_prs(self, cards):
        num_to_check = self.MAX_CARD_SIZE - len(cards)
        num_left = self.TOTAL_SIZE - len(cards)
        kind_digits = self.count_kind_digits(cards)
        results = []
        for _, digits in kind_digits.items():
            results += self.ana_single_straight_prs(digits, num_to_check, num_left, StraightFlushTool())
        return results

    def get_straight_prs(self, cards):
        num_to_check = self.MAX_CARD_SIZE - len(cards)
        num_left = self.TOTAL_SIZE - len(cards)
        digits = self.count_digits(cards)
        return self.ana_single_straight_prs(digits, num_to_check, num_left, StraightApproxTool())

    def get_flush_prs(self, cards):
        num_to_check = self.MAX_CARD_SIZE - len(cards)
        num_left = self.TOTAL_SIZE - len(cards)
        kind_counts, kind_max_digits = self.count_kinds(cards)
        results = []
        tool = FlushTool()
        for kind, cnt in kind_counts.items():
            pr = self.ana_single_flush_pr(cnt, num_to_check, num_left, tool)
            results.append((pr, kind_max_digits[kind]))
        return results


    def _ana_single_straight_pr_st(
            self, exclusive_upper, exclusive_below, left, right, num_len,
            num_to_check, num_left,
            tool
    ):
        # 必须包含left, right，不能包含exclusive_upper或exclusive_below
        gap = left - right + 1
        # two large gap, not possible
        if gap > self.SUIT_SIZE:
            return False, None

        # left-right，恰好够
        if gap == self.SUIT_SIZE:
            # 从剩余中选择num_left选择num_to_check个，必须有gap - num_len固定
            pr = tool.pr_choose_k(num_left, num_to_check, self.SUIT_SIZE - num_len)
            return True, (pr, left)
        # left-right，小，可以外扩
        if exclusive_upper - exclusive_below - 1 == self.SUIT_SIZE:
            # 恰好外扩空间够
            pr = tool.pr_choose_k(num_left, num_to_check, self.SUIT_SIZE - num_len)
            return True, (pr, exclusive_upper - 1)
        elif exclusive_upper - exclusive_below - 1 < self.SUIT_SIZE:
            # 外扩空间不够
            return False, None
        # 外扩空间充足
        left_space = exclusive_upper - left - 1
        right_space = right - exclusive_below - 1
        all_space = self.SUIT_SIZE - gap
        max_d = left + min(all_space, left_space)
        min_d = right - min(all_space, right_space)
        must_num = gap - num_len
        # 外部数字，N-num_len个数，选出"连续"的suit_size-num_len个
        pr = tool.pr_choose_consecutive_k(
            num_left, num_to_check, max_d - min_d + 1 - num_len, self.SUIT_SIZE - num_len
        )
        return True, (pr, (max_d, min_d + self.SUIT_SIZE - 1))

    def ana_single_straight_prs(self, digits, num_to_check, num_left, tool):
        # TODO
        # 当前选取的各种straight段，概率有多算（因为可能出现6/7张顺子）
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
                flag, result = self._ana_single_straight_pr_st(
                    exclusive_upper, exclusive_below, digits[beg_n], digits[end_n - 1], end_n - beg_n,
                    num_to_check, num_left,
                    tool
                )
                if flag:
                    results.append(result)
            pass
        pass
        if digits[0] != PokerDigit.A:
            return results
        for beg_n in range(1, len(digits)):
            exclusive_upper = digits[beg_n - 1]
            exclusive_below = 0
            flag, result = self._ana_single_straight_pr_st(
                exclusive_upper, exclusive_below, digits[beg_n], 1, len(digits) - beg_n + 1,
                num_to_check, num_left,
                tool
            )
            if flag:
                results.append(result)
        pass
        return results

    def ana_single_flush_pr(self, num, num_to_check, num_left, tool):
        if num_to_check + num < self.SUIT_SIZE:
            return 0.0
        if num_to_check + num == self.SUIT_SIZE:
            # choose(13 - num, num_to_check) / choose(num_left, num_to_check)
            return tool.pr_choose_k(num_left, 13 - num, num_to_check)
        # num_to_check + num > self.SUIT_SIZE:
        # choose(13 - num, suit_size - num .. num_to_check) / choose(num_left, num_to_check)
        return tool.pr_choose_k_to_s(num_left, 13 - num, self.SUIT_SIZE - num, num_to_check)
