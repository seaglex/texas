import pickle
import datetime as dt

from texas.direct_calc import ApproxCalc
from texas.direct_cmp import ApproxComparer
from texas.judge import TexasJudge
from texas.monte_carlo import Simulator

if __name__ == "__main__":
    cards = [(1, 2), (1, 3), (1, 4), (1, 5)]
    comparer = ApproxComparer()
    simulator = Simulator(TexasJudge())

    hole_cards = cards[:2]
    community_cards = cards[2:]

    beg = dt.datetime.now()
    for n in range(1000):
        comparer.get_pr(hole_cards, community_cards)
    delta = dt.datetime.now() - beg
    print(delta)

    beg = dt.datetime.now()
    for n in range(1000):
        simulator.get_pr(hole_cards, community_cards, trial_num=1000)
    delta = dt.datetime.now() - beg
    print(delta)
