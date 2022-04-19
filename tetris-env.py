import gym
import pygame
from game import Game

class TetrisEnv(gym.Env):

    def __init__(self,env_config={}):
        self.game = Game()

    def step(self, action):
        self.game.step()
        self.game.clock.tick(self.game.fps)
        rect = pygame.Rect(25, 25, 100, 50)
        sub = pygame.screen.subsurface(rect)
        pygame.image.save(sub, "screenshot.jpg")

    
    def render(self):
        pass

    def reset(self):
        pass