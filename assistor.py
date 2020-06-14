import argparse
import random

from texas import monte_carlo
from texas import judge
from texas.poker import PokerCard


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-a", "--auto_num", type=int, default=0)
    parser.add_argument("-t", "--trial", type=int, default=1000)
    args = parser.parse_args()

    simulator = monte_carlo.Simulator(judge.TexasJudge(args.verbose))
    cards = [PokerCard(x[0], x[1]) for x in simulator.total_cards]
    r = random.Random(0)

    while True:
        if args.auto_num == 0:
            print("Input your 2 cards (split by space): ", end="")
            line = input()
            if line.strip().lower() == "exit":
                break
            words = line.split()
            if len(words) != 2:
                print("Wrong input")
                continue
            card1 = PokerCard.try_parse(words[0])
            card2 = PokerCard.try_parse(words[1])
            if card1 is None or card2 is None:
                print("Wrong input")
                continue
        else:
            r.shuffle(cards)
            card1, card2 = cards[0], cards[1]
            args.auto_num -= 1

        pr = simulator.get_pr([card1.get_data(), card2.get_data()], trial_num=args.trial)
        print(card1, card2, "Winning pr:", pr)
