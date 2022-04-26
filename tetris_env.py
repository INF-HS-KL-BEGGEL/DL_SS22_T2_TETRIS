from copy import copy
import enum

import numpy as np
import gym
import pygame
from game import Game
from figure import *

class TetrisEnv(gym.Env):

	ACTION_SPACE_SIZE = 6

	def __init__(self, env_config={}):
		self.game = Game(fps=25)
		self.last_score = 0
		self.last_hole_count = 0
		self.last_bumps = 0

	def step(self, action):

		figure_before_step = self.game.tetris.figure
		next_figure_before_step = self.game.tetris.next_figure
		field_before_step = copy(self.game.tetris.field)

		self.game.step(mode='ai', action=action)

		observation = self.render()
		done = self.game.tetris.state == 'gameover'
		reward = self.__calc_reward_new(figure_before_step, next_figure_before_step, action)

		info = self.game.tetris.score - self.last_score
		self.last_score = self.game.tetris.score

		if done:
			reward = -100

		return observation, reward, done, info

	def render(self, mode='human'):
		self.game.draw()
		self.game.clock.tick(self.game.fps)
		#observation = self.game.screenshot().astype('float32')
		return np.array(self.game.tetris.field)

	def reset(self):
		self.game.tetris.__init__(20, 10)
		self.last_score = 0
		self.last_bumps = 0
		self.last_hole_count = 0
		return self.render()

	def __calc_reward_new(self, figure_before_step, next_figure_before_step, action):
		# 1. Keine löcher
		# 2. Wenige hügel
		# 3. Zeile weg Reward
		# 4. niedrigerer block -> mehr punkte
		
		block_height = figure_before_step.y_adjusted() + shapes[figure_before_step.type].height()
		reward_bonus = (block_height - 10) ** 2
		if block_height < 10:
			reward_bonus = 0

		# wenn Block platziert
		if figure_before_step != self.game.tetris.figure:
			# 1
			hole_count = self.__calculate_hole_count()
			hole_delta = hole_count - self.last_hole_count
			self.last_hole_count = hole_count
			#2
			bump_count = self.__calculate_bumps()
			bump_delta = bump_count - self.last_bumps
			self.last_bumps = bump_count
			if bump_count < 6 and bump_delta > 0:
				bump_delta = 0
			#3
			current_score = self.game.tetris.score
			score_delta = current_score - self.last_score

			reward = (-10 * hole_delta) + (-2.5 * bump_delta) + (1000 * score_delta) + (0.2 * reward_bonus)
			print("Reward for block: ", reward)
			return reward

		return (0.2 * reward_bonus)

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
			print("Reward for block: ", total * total - (19 - shape_true_y))
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
