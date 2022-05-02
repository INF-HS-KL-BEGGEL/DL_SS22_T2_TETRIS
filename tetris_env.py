from collections import deque
from copy import copy

import tensorflow as tf

import cv2
import gym
import pygame
from game import Game
from figure import shapes


class TetrisEnv(gym.Env):

	ACTION_SPACE_SIZE = 6
	SNAPSHOT_RATE = 100

	def __init__(self, env_config={}):
		self.game = Game(fps=25)
		self.last_score = 0
		self.fitness = 0
		self.actions = deque(maxlen=10)

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
			print("round fitness: ", self.fitness)
			reward = -5

		return observation, reward, done, info

	def render(self, mode='human'):
		self.game.draw()
		self.game.clock.tick(self.game.fps)
		observation = tf.image.resize(self.game.screenshot(), (32, 40))
		return observation

	def reset(self):
		self.game.games_played += 1
		if self.game.recording:
			self.game.save_video()
		if self.game.games_played % TetrisEnv.SNAPSHOT_RATE == 0:
			self.game.record()
		self.game.tetris.__init__(20, 10)
		self.last_score = 0
		self.fitness = 0
		return self.render()

	def __calc_reward_new(self, figure_before_step, next_figure_before_step, action):
		# 1. Keine löcher
		# 2. Wenige hügel
		# 3. Zeile weg Reward
		# 4. niedrigerer block -> mehr punkte

		repeated_actions = len(list(filter(lambda x: x == action, self.actions))) + 1
		base_reward = 1 / repeated_actions

		block_height = figure_before_step.y_adjusted() + shapes[figure_before_step.type].height()
		# wenn Block platziert
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
			# print("Reward for block: ", reward)
		else:
			reward = block_height * 0.01 if block_height > 10 else 0

		self.actions.append(action)
		return base_reward + reward

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
		# base_score = ((self.game.tetris.score - self.last_score) * 100000) + 1
		# figure_score = self.game.tetris.figure.y**2
		# figure_score = 0
		#
		# extra_reward = 0
		# #  new figure
		# if self.game.tetris.next_figure != next_figure_before_step:
		# 	line_dropped = figure_before_step.y
		# 	extra_reward += self.__check_lines_for_placement(line_dropped)
		#
		# return base_score + figure_score + extra_reward
		if next_figure_before_step == self.game.tetris.next_figure:
			base_figure_reward = (1 if self.game.tetris.figure.y > 6 else 0)
		else:
			base_figure_reward = (1 if figure_before_step.y > 6 else 0)
		return ((2**(self.game.tetris.score - self.last_score) - 1) * 250) + base_figure_reward

	def __check_lines_for_placement(self, line_y):
		base_fill_score = 0
		for y in range(line_y, min(line_y + 4, 19)):
			line_count = len(list(filter(lambda x: x > 0, self.game.tetris.field[y])))
			line_percentage = line_count / 10
			base_fill_score += line_percentage * y**2

		return base_fill_score
