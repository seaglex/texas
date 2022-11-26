"""
Judge
set_: 最好的一组5张牌
cards: 手牌
Card: size=2数组表示(symbol, digit)
"""

from collections import defaultdict
import enum
import numpy as np

from .poker import PokerDigit, PokerSymbol, PokerCard


class TexasLevel(enum.IntEnum):
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
    unknown = 0


class TexasJudge(object):
    BEST_SET_SIZE = 5
    MAX_CARD_SIZE = 7

    def __init__(self, is_debug=False):
        self.is_debug = is_debug

    def argmax(self, card_lists):
        if not card_lists:
            return []
        return self._arg_max([self._get_level_set(cs) for cs in card_lists])

    def rank(self, card_lists):
        if not card_lists:
            return []
        return self._rank([self._get_level_set(cs) for cs in card_lists])

    def _arg_max(self, level_best_sets):
        """
        :param level_best_sets: size >= 1
        :return: best indexes
        """
        if self.is_debug:
            for level, set_ in level_best_sets:
                print(level, end=" ")
                for j in range(len(set_)):
                    print(PokerCard.short_format(*set_[j]), end=" ")
                print("\t", end=" ")

        best_indexes = [0]
        best_level, best_set = level_best_sets[0]
        for i in range(1, len(level_best_sets)):
            level, set_ = level_best_sets[i]
            if level < best_level:
                continue
            if level > best_level:
                best_level, best_set = level, set_
                best_indexes = [i]
                continue
            worse = False
            better = False
            for j in range(len(best_set)):
                if j >= len(set_):
                    print("error")
                if set_[j][1] < best_set[j][1]:
                    worse = True
                    break
                elif set_[j][1] > best_set[j][1]:
                    better = True
                    break
            if worse:
                continue
            if better:
                best_level, best_set = level, set_
                best_indexes = [i]
                continue
            best_indexes.append(i)
        if self.is_debug:
            print(best_indexes)
        return best_indexes

    def _rank(self, level_best_sets):
        # level + five cards, packed together as hex
        packed_results = np.zeros(len(level_best_sets))
        for n, (level, cards) in enumerate(level_best_sets):
            result = level
            for m, c in enumerate(cards):
                result = (result << 4) + c[1]
            packed_results[n] = result
        if self.is_debug:
            for n, packed in enumerate(packed_results):
                print(level_best_sets[n][0], "%X" % packed)
        indexes = np.argsort(packed_results)
        ranks = np.zeros(len(level_best_sets), dtype=int)
        rank_level = 0
        last_repr = None
        for index in indexes[::-1]:
            if last_repr is not None and packed_results[index] != last_repr:
                rank_level += 1
            ranks[index] = rank_level
            last_repr = packed_results[index]
        if self.is_debug:
            print(' '.join(str(l) for l in rank_level))
        return ranks

    @staticmethod
    def _select_set(cards, first_digit, second_digit, left_num):
        set_ = []
        first_cards = []
        second_cards = []
        for card in sorted(cards, key=lambda x: x[1], reverse=True):
            if card[1] == first_digit:
                first_cards.append(card)
                continue
            if card[1] == second_digit:
                second_cards.append(card)
                continue
            if len(set_) < left_num:
                set_.append(card)
        set_ = first_cards + second_cards + set_
        if len(set_) > TexasJudge.BEST_SET_SIZE:  # 3 + 3
            set_ = set_[:TexasJudge.BEST_SET_SIZE]
        return set_

    def _check_flush(self, cards):
        # check straight & flush (except straight it self)
        best_level = TexasLevel.unknown
        best_flush = None
        last_sym = PokerSymbol.unknown
        last_digit = PokerDigit.unknown
        straight_flush_cnt = 0
        flush_cnt = 0
        ace = None
        cards = list(sorted(cards, key=lambda c: (c[0] << 4) + c[1], reverse=True))
        for index, (sym, digit) in enumerate(cards):
            if sym != last_sym:
                flush_cnt = 1
                straight_flush_cnt = 1
                last_digit = digit
                last_sym = sym
                if digit == PokerDigit.A:
                    ace = cards[index]
                else:
                    ace = None
                continue
            flush_cnt += 1
            if digit == last_digit - 1:
                straight_flush_cnt += 1
            else:
                straight_flush_cnt = 1
            if digit == PokerDigit.A:
                ace = cards[index]
            last_digit = digit
            if flush_cnt >= self.BEST_SET_SIZE:
                if straight_flush_cnt == self.BEST_SET_SIZE:
                    # the first and the best
                    best_level = TexasLevel.straight_flush
                    best_flush = cards[index + 1 - self.BEST_SET_SIZE: index + 1]
                    break
                elif straight_flush_cnt == self.BEST_SET_SIZE - 1 and ace is not None and last_digit == 2:
                    # the last and the best
                    best_level = TexasLevel.straight_flush
                    best_flush = [*(cards[index + 2 - self.BEST_SET_SIZE: index + 1]), ace]
                    break
                elif best_level < TexasLevel.flush:
                    # might find straight flush later
                    best_level = TexasLevel.flush
                    best_flush = cards[index + 1 - self.BEST_SET_SIZE: index + 1]
                else:
                    continue
        return best_level, best_flush

    def _check_straight(self, cards):
        straight_cnt = 0
        cards = list(sorted(cards, key=lambda x: x[1], reverse=True))
        last_digit = PokerDigit.unknown
        set_ = []
        ace = None
        for index, c in enumerate(cards):
            digit = c[1]
            if digit == PokerDigit.A:
                ace = c
            if digit == last_digit - 1:
                straight_cnt += 1
                set_.append(c)
            elif digit == last_digit:
                pass
            else:
                straight_cnt = 1
                set_.clear()
                set_.append(c)
            last_digit = digit
            if straight_cnt == self.BEST_SET_SIZE:
                return TexasLevel.straight, set_
        if straight_cnt == self.BEST_SET_SIZE - 1 and last_digit == 2 and ace is not None:
            straight_cnt += 1
            set_.append(ace)
            return TexasLevel.straight, set_
        return TexasLevel.unknown, None

    def _check_nums(self, cards):
        # check others
        digit_counts = defaultdict(int)
        for _, digit in cards:
            digit_counts[digit] += 1
        digit_counts = list(sorted(digit_counts.items(), key=lambda dc: dc[1] * 100 + dc[0], reverse=True))
        if digit_counts[0][1] >= 4:  # four
            return TexasLevel.four, self._select_set(cards, digit_counts[0][0], None, 1)
        if digit_counts[0][1] == 3 and len(digit_counts) >= 2 and digit_counts[1][1] >= 2:  # full house
            return TexasLevel.full_house, self._select_set(cards, digit_counts[0][0], digit_counts[1][0], 0)
        if digit_counts[0][1] == 3:  # three
            return TexasLevel.three, self._select_set(cards, digit_counts[0][0], None, 2)
        if digit_counts[0][1] == 2 and len(digit_counts) >= 2 and digit_counts[1][1] == 2:  # two pairs
            return TexasLevel.two_pairs, self._select_set(cards, digit_counts[0][0], digit_counts[1][0], 1)
        if digit_counts[0][1] == 2:  # pair
            return TexasLevel.pair, self._select_set(cards, digit_counts[0][0], None, 3)
        return TexasLevel.high_card, self._select_set(cards, None, None, 5)

    def _get_level_set(self, cards):
        # get the highest level & best combination set (5 cards out of 7)
        assert len(cards) <= self.MAX_CARD_SIZE
        best_level, best_set = self._check_flush(cards)
        if best_level == TexasLevel.straight_flush:
            return best_level, best_set
        num_level, num_set = self._check_nums(cards)
        if num_level > best_level:
            best_level, best_set = num_level, num_set
        if best_level > TexasLevel.straight:
            return best_level, best_set
        straight_level, straight_set = self._check_straight(cards)
        if straight_level > best_level:
            best_level, best_set = straight_level, straight_set
        return best_level, best_set
