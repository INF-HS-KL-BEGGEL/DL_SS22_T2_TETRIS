import enum
import os
from collections import deque

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
		self.default_epsilon = 0.10
		self.min_epsilon = 0.01
		self.target_score = (os.getenv('TARGET_SCORE') or 50)
		self.last_scores = deque(maxlen=20)

	def step(self, action, action_q=None):
		figure_before_step = self.game.tetris.figure
		next_figure_before_step = self.game.tetris.next_figure

		self.game.step(mode='ai', action=action, action_q=action_q)

		observation = self.render()
		done = self.game.tetris.state == 'gameover'
		reward = self.__calc_reward(figure_before_step, next_figure_before_step, action)

		info = self.game.tetris.score - self.last_score
		self.last_score = self.game.tetris.score

		if done:
			reward = -100
			if self.game.recording:
				self.game.save_video()
			self.last_scores.append(self.game.tetris.score)

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
		if eval:
			self.game.record()
		self.game.tetris.__init__(20, 10)
		self.last_score = 0
		self.last_bumps = 0
		self.last_hole_count = 0
		return self.render()

	def __calc_reward(self, figure_before_step, next_figure_before_step, action):
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

	def get_epsilon(self):
		if len(self.last_scores) == 0:
			return self.default_epsilon
		avg_score = sum(self.last_scores) / len(self.last_scores)
		if avg_score > self.target_score:
			return self.min_epsilon
		else:
			return self.default_epsilon
