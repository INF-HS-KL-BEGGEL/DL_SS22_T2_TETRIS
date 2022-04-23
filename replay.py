from collections import deque
from random import sample

import numpy as np


class ReplayBuffer:
	def __init__(self):
		self.gameplay_experiences = deque(maxlen=1000000)

	def store_gameplay_experience(self, state, next_state, reward, action, done):
		"""
		Stores a step of gameplay experience in
		the buffer for later training
		"""
		self.gameplay_experiences.append((state, next_state, reward, action, done))

	def sample_gameplay_batch(self):
		"""
		Samples a batch of gameplay experiences
		for training purposes.
		"""
		batch_size = min(128, len(self.gameplay_experiences))
		sampled_gameplay_batch = sample(self.gameplay_experiences, batch_size)
		state_batch, next_state_batch, action_batch, reward_batch, done_batch = [], [], [], [], []
		for gameplay_experience in sampled_gameplay_batch:
			state_batch.append(gameplay_experience[0])
			next_state_batch.append(gameplay_experience[1])
			reward_batch.append(gameplay_experience[2])
			action_batch.append(gameplay_experience[3])
			done_batch.append(gameplay_experience[4])
		return np.array(state_batch), np.array(next_state_batch), action_batch, reward_batch, done_batch

