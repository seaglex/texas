import argparse
import random

from texas import monte_carlo
from texas import judge
from texas.poker import PokerCard
from texas.direct_cmp import ApproxComparer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-p", "--player_num", type=int, default=4)
    parser.add_argument("-a", "--auto_num", type=int, default=0)
    parser.add_argument("-t", "--trial", type=int, default=1000)
    args = parser.parse_args()

    simulator = monte_carlo.Simulator(judge.TexasJudge(args.verbose))
    total_cards = [PokerCard(x[0], x[1]) for x in simulator.total_cards]
    r = random.Random(0)

    is_auto = args.auto_num > 0
    while not is_auto or args.auto_num > 0:
        if not is_auto:
            print("Input your 2+ total_cards (split by space): ", end="")
            line = input()
            if line.strip().lower() == "exit":
                break
            words = line.split()
            if len(words) < 2:
                print("Wrong input")
                continue
            cards = [PokerCard.try_parse(x) for x in words if x]
            if sum(1 for c in cards if not c) > 0 or len(cards) < 2:
                print("Wrong input")
                continue
        else:
            r.shuffle(total_cards)
            cards = total_cards[:2]
            args.auto_num -= 1

        pr1 = simulator.get_pr(
            [c.get_data() for c in cards[:2]],
            [c.get_data() for c in cards[2:]],
            player_num=args.player_num,
            trial_num=args.trial
        )
        comparer = ApproxComparer()
        pr2 = comparer.get_pr(
            [c.get_data() for c in cards[:2]],
            [c.get_data() for c in cards[2:]],
            player_num=args.player_num,
        )
        print(cards, f"Winning pr: {pr1:.1%}(MC) {pr2:.1%}(Appox)")
