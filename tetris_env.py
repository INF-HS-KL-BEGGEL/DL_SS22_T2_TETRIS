import enum

import numpy as np
import gym
from game import Game
from figure import *

class TetrisEnv(gym.Env):

	SNAPSHOT_RATE = 100

	def __init__(self, env_config={}):
		self.game = Game(fps=25)
		self.last_score = 0
		self.last_hole_count = 0
		self.last_bumps = 0
		self.epsilon = 0.05
		self.fitness = 0

	def step(self, action, action_q=None):
		figure_before_step = self.game.tetris.figure
		next_figure_before_step = self.game.tetris.next_figure

		self.game.step(mode='ai', action=action, action_q=action_q)

		observation = self.render()
		done = self.game.tetris.state == 'gameover'
		reward = self.__calc_reward_new(figure_before_step, next_figure_before_step, action)

		info = self.game.tetris.score - self.last_score
		self.last_score = self.game.tetris.score

		if done:
			reward = -100
			if self.game.recording:
				self.game.save_video()

		return observation, reward, done, info

	def render(self, mode='ai'):
		self.game.draw()
		if mode == 'human':
			self.game.clock.tick(self.game.fps)

		observation = np.where(self.game.tetris.field > 0, 1, 0)
		onlyFigureField = np.zeros(observation.shape, dtype=int)
		if self.game.tetris.figure is not None:
			for i in range(4):
				for j in range(4):
					p = i * 4 + j
					if p in self.game.tetris.figure.image():
						onlyFigureField[i + self.game.tetris.figure.y][j + self.game.tetris.figure.x] = 1

		observation = np.concatenate((observation, onlyFigureField))
		return observation

	def reset(self, eval=False):
		self.game.games_played += 1
		if self.game.games_played % 5000 == 0 and self.epsilon > 0.01:
			self.epsilon -= 0.001
		if eval:
			self.game.record()
		self.game.tetris.__init__(20, 10)
		self.last_score = 0
		self.last_bumps = 0
		self.last_hole_count = 0
		return self.render()

	def __calc_reward_new(self, figure_before_step, next_figure_before_step, action):
		if figure_before_step != self.game.tetris.figure:
			# 1
			hole_count = self.__calculate_hole_count()
			#2
			bump_count = self.__calculate_bumps()
			#3
			current_score = self.game.tetris.score

			summed_height = self.__calc_height()
			# print(summed_height)

			new_fitness = (-0.51 * summed_height) + (0.76 * current_score) + (-0.36 * hole_count) + (-0.18 * bump_count)
			reward = new_fitness - self.fitness
			self.fitness = new_fitness
			return reward

		return 0

	def __calc_height(self):
		height = 0
		for x in range(self.game.tetris.width):
			for y, _ in enumerate(self.game.tetris.field):
				if self.game.tetris.field[y][x] > 0:
					height += self.game.tetris.height - y
					break
		return height

	def __calculate_hole_count(self):
		holes = [-1] * len(self.game.tetris.field[0])
		hole_count = 0
		for fieldRow in self.game.tetris.field:
			for fieldX in range(len(fieldRow)):
				if holes[fieldX] == -1 and fieldRow[fieldX] > 0:
					holes[fieldX] = 0
				elif holes[fieldX] >= 0 and fieldRow[fieldX] == 0:
					holes[fieldX] += 1
					hole_count += 1
		return hole_count

	def __calculate_bumps(self):
		bumps = 0
		highest_block_pos = [20] * len(self.game.tetris.field[0])
		for x in range(len(self.game.tetris.field[0])):
			for y in range(len(self.game.tetris.field)):
				if self.game.tetris.field[y][x] > 0:
					highest_block_pos[x] = y
					break
		
		for i in range(1, len(highest_block_pos)):
			bumps += abs(highest_block_pos[i] - highest_block_pos[i-1])
		
		return bumps



	def __calc_reward(self, figure_before_step, next_figure_before_step, action):

		if figure_before_step != self.game.tetris.figure:
			shape = shapes[figure_before_step.type]
			rotated_shape_height = shape.height() if figure_before_step.rotation % 2 == 0 else shape.width()
			shape_true_y = figure_before_step.y
			if figure_before_step.type == 1 or figure_before_step.type == 2 or figure_before_step.type == 5 and figure_before_step.rotation == 2 or figure_before_step.type == 0 and figure_before_step.rotation % 2 == 1:
				shape_true_y += 1

			if shape_true_y < 0:
				shape_true_y = 0

			total = 0
			for i in range(rotated_shape_height):
				if shape_true_y + i > 19:
					break
				row = self.game.tetris.field[shape_true_y + i]
				tmpTotal = 0
				for e in row:
					if e > 0:
						tmpTotal += 1
				total += tmpTotal
			total /= rotated_shape_height
			return total * total - (19 - shape_true_y)
		else:
			return 0


	def __check_lines_for_placement(self, line_y):
		base_fill_score = 0
		for y in range(line_y, min(line_y + 4, 19)):
			line_count = len(list(filter(lambda x: x > 0, self.game.tetris.field[y])))
			line_percentage = line_count / 10
			base_fill_score += line_percentage * y**2

		return base_fill_score
