from copy import copy

import gym
import pygame
from game import Game
from figure import *

class TetrisEnv(gym.Env):

	SNAPSHOT_RATE = 100

	def __init__(self, env_config={}):
		self.game = Game(fps=25)
		self.last_score = 0

	def step(self, action, action_q=None):
		figure_before_step = self.game.tetris.figure
		next_figure_before_step = self.game.tetris.next_figure
		field_before_step = copy(self.game.tetris.field)

		self.game.step(mode='ai', action=action, action_q=action_q)

		observation = self.render()
		done = self.game.tetris.state == 'gameover'
		reward = self.__calc_reward(figure_before_step, next_figure_before_step, action)

		info = self.game.tetris.score - self.last_score
		self.last_score = self.game.tetris.score

		if done:
			reward = -100

		return observation, reward, done, info

	def render(self, mode='human'):
		self.game.draw()
		self.game.clock.tick(self.game.fps)
		observation = self.game.screenshot().astype('float32')
		return observation

	def reset(self):
		self.game.games_played += 1
		if self.game.recording:
			self.game.save_video()
		if self.game.games_played % TetrisEnv.SNAPSHOT_RATE == 0:
			self.game.record()
		self.game.tetris.__init__(20, 10)
		self.last_score = 0
		return self.render()

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
#				print("Counting blocks at Y: ", 19 - shape_true_y - i)
				tmpTotal = 0
				for e in row:
					if e > 0:
						tmpTotal += 1
				total += tmpTotal
#				print("[", 19 - shape_true_y - i, "]Found ", tmpTotal, " blocks!")
#			print("Total blocks in range: ", total)
#			print("Rotation: ", figure_before_step.rotation)
			total /= rotated_shape_height
			print("Reward for block: ", total * total - (19 - shape_true_y))
			return total * total - (19 - shape_true_y)
		else:
			return 0
#		if next_figure_before_step == self.game.tetris.next_figure:
#			base_figure_reward = (1 if self.game.tetris.figure.y > 6 else 0)
#		else:
#			base_figure_reward = (1 if figure_before_step.y > 6 else 0)
#		return ((2**(self.game.tetris.score - self.last_score) - 1) * 250) + base_figure_reward

	def __check_lines_for_placement(self, line_y):
		base_fill_score = 0
		for y in range(line_y, min(line_y + 4, 19)):
			line_count = len(list(filter(lambda x: x > 0, self.game.tetris.field[y])))
			line_percentage = line_count / 10
			base_fill_score += line_percentage * y**2

		return base_fill_score
