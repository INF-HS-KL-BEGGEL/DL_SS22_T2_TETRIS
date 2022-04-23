import gym
import pygame
from game import Game

class TetrisEnv(gym.Env):

	ACTION_SPACE_SIZE = 6

	def __init__(self, env_config={}):
		self.game = Game(fps=2000)
		self.last_score = 0

	def step(self, action):
		self.game.step(mode='ai', action=action)

		observation = self.render()
		done = self.game.tetris.state == 'gameover'
		info = None

		reward = self.__calc_reward()
		self.last_score = self.game.tetris.score

		if done:
			reward = 0

		return observation, reward, done, info

	def render(self, mode='human'):
		self.game.draw()
		self.game.clock.tick(self.game.fps)
		observation = self.game.screenshot().astype('float32')
		return observation

	def reset(self):
		self.game.tetris.__init__(20, 10)
		return self.render()

	def __calc_reward(self):
		base_score = ((self.game.tetris.score - self.last_score) * 100000) + 1
		figure_score = self.game.tetris.figure.y**2
		return base_score + figure_score
