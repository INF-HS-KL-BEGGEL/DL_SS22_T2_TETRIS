import gym
import pygame
from game import Game

class TetrisEnv(gym.Env):

	ACTION_SPACE_SIZE = 6

	def __init__(self, env_config={}):
		self.game = Game()
		self.last_score = 0

	def step(self, action):
		self.game.step(mode='ai', action=action)

		observation = self.render()
		reward = self.game.tetris.score - self.last_score
		self.last_score = self.game.tetris.score
		done = self.game.tetris.state == 'gameover'
		info = None

		return observation, reward, done, info

	def render(self, mode="human"):
		self.game.draw()
		self.game.clock.tick(self.game.fps)
		observation = self.game.screenshot().astype('float32')
		return observation

	def reset(self):
		self.game.tetris.__init__(20, 10)
		return self.render()
