import numpy as np
from texas.poker import PokerConst, PokerKind, PokerCard


class Simulator(object):
    def __init__(self, judge):
        digits = np.arange(PokerConst.MIN_DIGIT, PokerConst.MAX_DIGIT + 1, 1)
        kinds = [PokerKind.heart.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.diamond.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.spade.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.club.value] * PokerConst.DIGIT_NUM
        self.total_cards = np.array([kinds, list(digits) * 4]).T
        self.judge = judge

    def get_pr(self, cards, trial_num=100):
        """
        最简情况，2个人，2张牌，猜测再发5张牌的赢的概率
        :return: 胜率
        """
        assert len(cards) == 2
        left_cards = [x for x in self.total_cards
                      if (x[0] != cards[0][0] or x[1] != cards[0][1]) and (x[0] != cards[1][0] or x[1] != cards[1][1])]
        judge = self.judge
        wins = [0.0, 0.0]
        random_state = np.random.get_state()
        np.random.seed(0)
        for i in range(trial_num):
            np.random.shuffle(left_cards)
            common_cards = left_cards[:5]
            bests = judge.argmax([cards + common_cards, left_cards[5:7] + common_cards])
            weight = 1 / len(bests)
            for b in bests:
                wins[b] += weight
        np.random.set_state(random_state)
        return wins[0] / sum(wins)
