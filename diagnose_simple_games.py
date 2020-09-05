import argparse
from rl.q_learner import QLearner
from rl.simple_games import SimpleMovingGame
from rl.simple_games import RedBlackCardGame
from rl import bandit


def test_simple_moving_game(train_num=10000, test_num=1, is_debug=True):
    simple_game = SimpleMovingGame()
    learner = QLearner(bandit.ThompsonSampler(), 0.2)
    simple_game.train(learner, itr_num=train_num)

    for x in range(0, 4):
        for y in range(0, 4):
            print((x, y), learner._get_value((x, y)))
    print()

    winning_count = 0
    for n in range(test_num):
        reward = simple_game.test(learner, is_debug=is_debug)
        if reward > 0:
            winning_count += 1
    print(winning_count / test_num)


def test_red_black_game(train_num=10000, test_num=1, is_debug=True):
    game = RedBlackCardGame()
    a_learner = QLearner(bandit.EpsilonGreedySampler(), 0.001)
    b_learner = QLearner(bandit.EpsilonGreedySampler(), 0.001)
    game.train(a_learner, b_learner, train_num)

    print("player-A")
    for is_red in [False, True]:
        print("Red" if is_red else "Black", end="\t")
        for x in range(11):
            print("{0:.3}".format(a_learner._get_q_value(is_red, x)), end=" ")
        print()
    print("player-B")
    print("None", end="\t")
    for x in range(11):
        print("{0:.3}".format(b_learner._get_q_value(None, x)), end=" ")
    print("\n")

    avg_score = 0
    for n in range(test_num):
        reward = game.test(a_learner, b_learner, is_debug=is_debug)
        avg_score += reward
    print(avg_score / test_num)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("training_num", type=int, default=10000, nargs="?")
    args = parser.parse_args()

    test_simple_moving_game(args.training_num, 1000, False)
    test_red_black_game(args.training_num)