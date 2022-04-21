import gym
import pygame
from game import Game

class TetrisEnv(gym.Env):

    ACTION_SPACE_SIZE = 6

    def __init__(self, env_config={}):
        self.game = Game()

    def step(self, action):
        self.game.step(mode='ai', action=action)
        self.game.draw()

        observation = self.game.screenshot()
        reward = None
        done = False

        return observation, reward, done
    
    def render(self, mode="human"):
        self.game.clock.tick(self.game.fps)

    def reset(self):
        self.game.tetris.__init__(20, 10)

    def getShape(self):
        return self.game.screenshot_size()
