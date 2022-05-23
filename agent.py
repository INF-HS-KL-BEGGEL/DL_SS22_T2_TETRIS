import numpy as np
import random
import tensorflow as tf
from keras import Sequential
from keras.layers import Flatten, Dense

import action


class DqnAgent:
	"""
	DQN Agent: the agent that explores the game and
	should eventually learn how to play the game.
	"""

	def __init__(self, model_location='models'):
		self.model_location = model_location

		self.q_net = self._build_dqn_model()
		self.target_q_net = self._build_dqn_model()
		
		self.q_alt_net = self._build_dqn_model()
		self.target_q_alt_net = self._build_dqn_model()

		self.checkpoint = tf.train.Checkpoint(step=tf.Variable(0), net=self.q_net, target_net=self.target_q_net,alt_net=self.q_alt_net, target_alt_net=self.target_q_alt_net)
		self.checkpoint_manager = tf.train.CheckpointManager(self.checkpoint, 'checkpoints', max_to_keep=10)
		self.load_checkpoint()

	def policy(self, state):
		"""
		Takes a state from the game environment and returns
		a action that should be taken given the current game
		environment.
		"""
		state_input = tf.convert_to_tensor(state[None, :], dtype=tf.float32)
		action_q = self.q_net(state_input)
		action = np.argmax(action_q.numpy()[0], axis=0)
		return action, action_q

	def train(self, batch):
		"""
		Takes a batch of gameplay experiences from replay
		buffer and train the underlying model with the batch
		"""
		state_batch, next_state_batch, action_batch, reward_batch, done_batch = batch
		net_decider = random.randint(0,1)
		current_q =  self.q_net(state_batch) if net_decider == 1 else self.q_alt_net(state_batch)
		target_q = np.copy(current_q)
		next_q = self.target_q_net(next_state_batch) if net_decider == 1 else self.target_q_alt_net(next_state_batch)
		max_next_q = np.amax(next_q, axis=1)
		for i in range(state_batch.shape[0]):
			target_q[i][action_batch[i]] = reward_batch[i] if done_batch[i] else reward_batch[i] + 0.95 * max_next_q[i]

		result = self.q_net.fit(x=state_batch, y=target_q)

		return result.history['loss']

	def collect_policy(self, state, epsilon=0.05):
		policy, action_q = self.policy(state)
		if np.random.random() < epsilon:
			return np.random.randint(0, action.ACTION_SPACE_SIZE), action_q
		return policy, action_q

	def update_target_network(self):
		print('==== UPDATE TARGET NET ====')
		for a, b in zip(self.target_q_net.variables, self.q_net.variables):
			a.assign(b)  # copies the variables of model_b into model_a
		# self.target_q_net = self.q_net
		# self.q_net = self._build_dqn_model()

	def save_checkpoint(self):
		self.checkpoint_manager.save()

	def load_checkpoint(self):
		self.checkpoint.restore(self.checkpoint_manager.latest_checkpoint)
		if self.checkpoint.net:
			self.q_net = self.checkpoint.net
		if self.checkpoint.target_net:
			self.target_q_net = self.checkpoint.target_net

	def save_model(self):
		tf.saved_model.save(self.q_net, self.model_location)

	def load_model(self):
		self.q_net = tf.saved_model.load(self.model_location)

	@staticmethod
	def _build_dqn_model():
		q_net = Sequential()

		q_net.add(Flatten())

		q_net.add(Dense(400, activation='relu', kernel_initializer='he_uniform'))
		q_net.add(Dense(200, activation='relu', kernel_initializer='he_uniform'))
		q_net.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
		q_net.add(Dense(5, activation='linear', kernel_initializer='he_uniform'))
		q_net.compile(optimizer=tf.optimizers.Adam(learning_rate=0.001), loss='mse')
		return q_net
