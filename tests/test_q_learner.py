import unittest

from rl.q_learner import QLearner
from rl.simple_games import SimpleMovingGame


class QLearnerUnitTest(unittest.TestCase):
    @staticmethod
    def test_simple_moving_game(test_num=1):
        simple_game = SimpleMovingGame()
        learner = QLearner()
        simple_game.train(learner)
        winning_count = 0
        for n in range(test_num):
            reward = simple_game.test(learner, is_debug=True)
            if reward > 0:
                winning_count += 1
            print(n, winning_count)
        assert winning_count / test_num >= 0.95


if __name__ == "__main__":
    unittest.main()
