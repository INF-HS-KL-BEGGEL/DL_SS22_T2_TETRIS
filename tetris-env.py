import gym
import pygame
from game import Game

class TetrisEnv(gym.Env):

    def __init__(self, env_config={}):
        self.game = Game()

    def step(self, action):
        self.game.step(action)
    
    def render(self, mode="human"):
        self.game.draw()
        self.game.clock.tick(self.game.fps)

    def reset(self):
        pass
