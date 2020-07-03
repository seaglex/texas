import numpy as np
from texas.poker import PokerConst, PokerKind


class Simulator(object):
    MAX_COMMON_NUM = 5

    def __init__(self, judge):
        digits = np.arange(PokerConst.MIN_DIGIT, PokerConst.MAX_DIGIT + 1, 1)
        kinds = [PokerKind.heart.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.diamond.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.spade.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.club.value] * PokerConst.DIGIT_NUM
        self.total_cards = np.array([kinds, list(digits) * 4]).T
        self.judge = judge

    def get_pr(self, cards, common_cards=None, player_num=2, trial_num=100):
        """
        :return: 胜率
        """
        assert len(cards) == 2
        assert len(cards) <= self.MAX_COMMON_NUM
        if common_cards is None:
            common_cards = []
        left_cards = []
        for x in self.total_cards:
            if x[0] == cards[0][0] and x[1] == cards[0][1]:
                continue
            if x[0] == cards[1][0] and x[1] == cards[1][1]:
                continue
            is_dup = False
            for common_card in common_cards:
                if x[0] == common_card[0] and x[1] == common_card[1]:
                    is_dup = True
                    break
            if is_dup:
                continue
            left_cards.append(x)
        judge = self.judge
        wins = [0.0] * player_num
        random_state = np.random.get_state()
        np.random.seed(0)
        for i in range(trial_num):
            np.random.shuffle(left_cards)
            total_common_cards = common_cards + left_cards[:self.MAX_COMMON_NUM - len(common_cards)]
            player_cards = [cards + total_common_cards]
            index = self.MAX_COMMON_NUM - len(common_cards)
            for j in range(player_num - 1):
                player_cards.append(left_cards[index: index + 2] + total_common_cards)
                index += 2
            bests = judge.argmax(player_cards)
            weight = 1 / len(bests)
            for b in bests:
                wins[b] += weight
        np.random.set_state(random_state)
        return wins[0] / sum(wins)
