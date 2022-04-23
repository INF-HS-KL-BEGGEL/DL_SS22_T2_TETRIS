from agent import DqnAgent
from replay import ReplayBuffer
from tetris_env import TetrisEnv

from datetime import datetime

import tensorflow as tf

UPDATE_TARGET_EPISODES = 30

TENSORBOARD_DIR = './logs'

logdir = "logs/scalars/" + datetime.now().strftime("%Y%m%d-%H%M%S")
file_writer = tf.summary.create_file_writer(logdir + "/metrics")
file_writer.set_as_default()

def collect_gameplay_experience(env, agent, buffer, episode):
	"""
	The collect_gameplay_experience function plays the game "env" with the
	instructions produced by "agent" and stores the gameplay experiences
	into "buffer" for later training.
	"""
	state = env.reset()
	done = False
	total_reward = 0
	while not done:
		action = agent.collect_policy(state)
		next_state, reward, done, info = env.step(action)
		buffer.store_gameplay_experience(state, next_state, reward, action, done)
		state = next_state
		total_reward += reward
	print(f'{total_reward=}')
	tf.summary.scalar('total reward', data=total_reward, step=episode)


def train_model(episodes=6000):
	env = TetrisEnv()
	agent = DqnAgent()
	buffer = ReplayBuffer(maxlen=100000)
	for episode_cnt in range(episodes):  # Train the agent for 6000 episodes of the game
		collect_gameplay_experience(env, agent, buffer,  episode_cnt)
		gameplay_experience_batch = buffer.sample_gameplay_batch()
		loss = agent.train(gameplay_experience_batch)
		if episode_cnt % UPDATE_TARGET_EPISODES == 0:
			agent.save_checkpoint()
			agent.update_target_network()

	return env, agent, buffer


def evaluate_training_result(env, agent):
	total_reward = 0.0
	episodes_to_play = 10
	for i in range(episodes_to_play):  # Play 10 episode and take the average
		state = env.reset()
		done = False
		episode_reward = 0.0
		while not done:
			action = agent.policy(state)
			next_state, reward, done, _ = env.step(action)
			episode_reward += reward
			state = next_state
		total_reward += episode_reward
	average_reward = total_reward / episodes_to_play
	return average_reward


if __name__ == '__main__':
	env, agent, buffer = train_model(1000)

	print(evaluate_training_result(env, agent))
