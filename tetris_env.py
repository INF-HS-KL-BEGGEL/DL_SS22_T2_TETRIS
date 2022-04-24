from copy import copy

import gym
import pygame
from game import Game

class TetrisEnv(gym.Env):

	ACTION_SPACE_SIZE = 6

	def __init__(self, env_config={}):
		self.game = Game(fps=2000)
		self.last_score = 0

	def step(self, action):

		figure_before_step = self.game.tetris.figure
		next_figure_before_step = self.game.tetris.next_figure
		field_before_step = copy(self.game.tetris.field)

		self.game.step(mode='ai', action=action)

		observation = self.render()
		done = self.game.tetris.state == 'gameover'
		info = None

		reward = self.__calc_reward(figure_before_step, next_figure_before_step)
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
		self.last_score = 0
		return self.render()

	def __calc_reward(self, figure_before_step, next_figure_before_step):
		base_score = ((self.game.tetris.score - self.last_score) * 100000) + 1
		figure_score = self.game.tetris.figure.y**2

		extra_reward = 0
		#  new figure
		if self.game.tetris.next_figure != next_figure_before_step:
			line_dropped = figure_before_step.y
			extra_reward += self.__check_lines_for_placement(line_dropped)

		return base_score + figure_score + extra_reward

	def __check_lines_for_placement(self, line_y):
		base_fill_score = 0
		for y in range(line_y, min(line_y + 4, 19)):
			line_count = len(list(filter(lambda x: x > 0, self.game.tetris.field[y])))
			line_percentage = line_count / 10
			base_fill_score += line_percentage * y**2

		return base_fill_score
