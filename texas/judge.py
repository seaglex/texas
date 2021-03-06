"""
Judge
suit: 最好的一组5张牌
cards: 手牌
Card: size=2数组表示(kind, digit)
"""

from collections import defaultdict
import enum
import numpy as np

from .poker import PokerDigit, PokerKind, PokerCard


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
    SUIT_SIZE = 5
    MAX_CARD_SIZE = 7

    def __init__(self, is_debug=False):
        self.is_debug = is_debug

    def argmax(self, card_lists):
        if not card_lists:
            return []
        return self._arg_max([self._get_level_suit(cs) for cs in card_lists])

    def rank(self, card_lists):
        if not card_lists:
            return []
        return self._rank([self._get_level_suit(cs) for cs in card_lists])

    def _arg_max(self, level_best_suits):
        """
        :param level_best_suits: size >= 1
        :return: best indexes
        """
        if self.is_debug:
            for l, suit in level_best_suits:
                print(l, end=" ")
                for j in range(len(suit)):
                    print(PokerCard.short_format(*suit[j]), end=" ")
                print("\t", end=" ")

        best_indexes = [0]
        best_level, best_suit = level_best_suits[0]
        for i in range(1, len(level_best_suits)):
            level, suit = level_best_suits[i]
            if level < best_level:
                continue
            if level > best_level:
                best_level, best_suit = level, suit
                best_indexes = [i]
                continue
            worse = False
            better = False
            for j in range(len(best_suit)):
                if j >= len(suit):
                    print("error")
                if suit[j][1] < best_suit[j][1]:
                    worse = True
                    break
                elif suit[j][1] > best_suit[j][1]:
                    better = True
                    break
            if worse:
                continue
            if better:
                best_level, best_suit = level, suit
                best_indexes = [i]
                continue
            best_indexes.append(i)
        if self.is_debug:
            print(best_indexes)
        return best_indexes

    def _rank(self, level_best_suits):
        # level + five cards, packed together as hex
        packed_results = np.zeros(len(level_best_suits))
        for n, (level, cards) in enumerate(level_best_suits):
            result = level
            for m, c in enumerate(cards):
                result = (result << 4) + c[1]
            packed_results[n] = result
        if self.is_debug:
            for n, packed in enumerate(packed_results):
                print(level_best_suits[n][0], "%X" % packed)
        indexes = np.argsort(packed_results)
        ranks = np.zeros(len(level_best_suits), dtype=int)
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
    def _select_suit(cards, first_digit, second_digit, left_num):
        suit = []
        first_cards = []
        second_cards = []
        for card in sorted(cards, key=lambda x: x[1], reverse=True):
            if card[1] == first_digit:
                first_cards.append(card)
                continue
            if card[1] == second_digit:
                second_cards.append(card)
                continue
            if len(suit) < left_num:
                suit.append(card)
        suit = first_cards + second_cards + suit
        if len(suit) > TexasJudge.SUIT_SIZE:  # 3 + 3
            suit = suit[:TexasJudge.SUIT_SIZE]
        return suit

    def _check_flush(self, cards):
        # check straight & flush (except straight it self)
        best_level = TexasLevel.unknown
        best_flush = None
        last_kind = PokerKind.unknown
        last_digit = PokerDigit.unknown
        straight_flush_cnt = 0
        flush_cnt = 0
        ace = None
        cards = list(sorted(cards, key=lambda c: (c[0] << 4) + c[1], reverse=True))
        for index, (kind, digit) in enumerate(cards):
            if kind != last_kind:
                flush_cnt = 1
                straight_flush_cnt = 1
                last_digit = digit
                last_kind = kind
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
            if flush_cnt >= self.SUIT_SIZE:
                if straight_flush_cnt == self.SUIT_SIZE:
                    # the first and the best
                    best_level = TexasLevel.straight_flush
                    best_flush = cards[index + 1 - self.SUIT_SIZE: index + 1]
                    break
                elif straight_flush_cnt == self.SUIT_SIZE - 1 and ace is not None and last_digit == 2:
                    # the last and the best
                    best_level = TexasLevel.straight_flush
                    best_flush = [*(cards[index + 2 - self.SUIT_SIZE: index + 1]), ace]
                    break
                elif best_level < TexasLevel.flush:
                    # might find straight flush later
                    best_level = TexasLevel.flush
                    best_flush = cards[index + 1 - self.SUIT_SIZE: index + 1]
                else:
                    continue
        return best_level, best_flush

    def _check_straight(self, cards):
        straight_cnt = 0
        cards = list(sorted(cards, key=lambda x: x[1], reverse=True))
        last_digit = PokerDigit.unknown
        suit = []
        ace = None
        for index, c in enumerate(cards):
            digit = c[1]
            if digit == PokerDigit.A:
                ace = c
            if digit == last_digit - 1:
                straight_cnt += 1
                suit.append(c)
            elif digit == last_digit:
                pass
            else:
                straight_cnt = 1
                suit.clear()
                suit.append(c)
            last_digit = digit
            if straight_cnt == self.SUIT_SIZE:
                return TexasLevel.straight, suit
        if straight_cnt == self.SUIT_SIZE - 1 and last_digit == 2 and ace is not None:
            straight_cnt += 1
            suit.append(ace)
            return TexasLevel.straight, suit
        return TexasLevel.unknown, None

    def _check_nums(self, cards):
        # check others
        digit_counts = defaultdict(int)
        for _, digit in cards:
            digit_counts[digit] += 1
        digit_counts = list(sorted(digit_counts.items(), key=lambda dc: dc[1] * 100 + dc[0], reverse=True))
        if digit_counts[0][1] >= 4:  # four
            return TexasLevel.four, self._select_suit(cards, digit_counts[0][0], None, 1)
        if digit_counts[0][1] == 3 and len(digit_counts) >= 2 and digit_counts[1][1] >= 2:  # full house
            return TexasLevel.full_house, self._select_suit(cards, digit_counts[0][0], digit_counts[1][0], 0)
        if digit_counts[0][1] == 3:  # three
            return TexasLevel.three, self._select_suit(cards, digit_counts[0][0], None, 2)
        if digit_counts[0][1] == 2 and len(digit_counts) >= 2 and digit_counts[1][1] == 2:  # two pairs
            return TexasLevel.two_pairs, self._select_suit(cards, digit_counts[0][0], digit_counts[1][0], 1)
        if digit_counts[0][1] == 2:  # pair
            return TexasLevel.pair, self._select_suit(cards, digit_counts[0][0], None, 3)
        return TexasLevel.high_card, self._select_suit(cards, None, None, 5)

    def _get_level_suit(self, cards):
        assert len(cards) <= self.MAX_CARD_SIZE
        best_level, best_suit = self._check_flush(cards)
        if best_level == TexasLevel.straight_flush:
            return best_level, best_suit
        num_level, num_suit = self._check_nums(cards)
        if num_level > best_level:
            best_level, best_suit = num_level, num_suit
        if best_level > TexasLevel.straight:
            return best_level, best_suit
        straight_level, straight_suit = self._check_straight(cards)
        if straight_level > best_level:
            best_level, best_suit = straight_level, straight_suit
        return best_level, best_suit
