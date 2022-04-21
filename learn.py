
from agent import DQNAgent
from tetris_env import TetrisEnv

if __name__ == '__main__':
    env = TetrisEnv()
    agent = DQNAgent('super cooler agent', env)

    done = False
    while not done:
        agent.train(done)

    # https://towardsdatascience.com/deep-reinforcement-learning-with-python-part-2-creating-training-the-rl-agent-using-deep-q-d8216e59cf31