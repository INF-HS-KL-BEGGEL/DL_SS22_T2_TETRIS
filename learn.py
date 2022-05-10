import os

from agent import DqnAgent
from replay import ReplayBuffer
from tetris_env import TetrisEnv

from datetime import datetime

import tensorflow as tf

UPDATE_TARGET_EPISODES = 100
CHECKPOINT_EPISODES = 100

TENSORBOARD_DIR = './logs'

learner_name = os.getenv('TENSORBOARD_NAME')
logdir = f'logs/scalars/{learner_name + "-" if learner_name is not None else ""}{datetime.now().strftime("%Y%m%d-%H%M%S")}'
file_writer = tf.summary.create_file_writer(logdir + "/metrics")
file_writer.set_as_default()

done_eval_runs = 0


def collect_gameplay_experience(env, agent, buffer, episode):
	"""
	The collect_gameplay_experience function plays the game "env" with the
	instructions produced by "agent" and stores the gameplay experiences
	into "buffer" for later training.
	"""
	state = env.reset()
	done = False
	total_reward = 0
	total_lines_cleared = 0
	while not done:
		action, action_q = agent.collect_policy(state)
		next_state, reward, done, info = env.step(action, action_q)
		buffer.store_gameplay_experience(state, next_state, reward, action, done)
		state = next_state
		total_reward += reward
		total_lines_cleared += info
	print(f'{total_reward=}')
	tf.summary.scalar('total reward', data=total_reward, step=episode)
	tf.summary.scalar('total lines', data=total_lines_cleared, step=episode)


def generate_model():
	env = TetrisEnv()
	agent = DqnAgent()
	buffer = ReplayBuffer(maxlen=10000)
	return env, agent, buffer


def train_model(env, agent, buffer, episodes=6000):
	for episode_cnt in range(episodes):  # Train the agent for 6000 episodes of the game
		collect_gameplay_experience(env, agent, buffer,  episode_cnt)
		for i in range(4):
			gameplay_experience_batch = buffer.sample_gameplay_batch(max_batch_size=32)
			loss = agent.train(gameplay_experience_batch)
		if (episode_cnt + 1) % CHECKPOINT_EPISODES == 0:
			agent.save_checkpoint()
		if (episode_cnt + 1) % UPDATE_TARGET_EPISODES == 0:
			agent.update_target_network()

	return env, agent, buffer


def evaluate_training_result(env, agent):
	global done_eval_runs
	total_reward = 0.0
	episodes_to_play = 10
	for i in range(episodes_to_play):  # Play 10 episode and take the average
		state = env.reset(eval=True)
		done = False
		episode_reward = 0.0
		while not done:
			action, action_q = agent.policy(state)
			next_state, reward, done, _ = env.step(action, action_q)
			episode_reward += reward
			state = next_state
		total_reward += episode_reward
	average_reward = total_reward / episodes_to_play
	done_eval_runs += 1
	tf.summary.scalar('avg eval reward', data=average_reward, step=done_eval_runs)
	return average_reward


if __name__ == '__main__':
	evals = int(os.getenv('EVALS') or 1)
	episodes_per_eval = int(os.getenv('EPISODES_PER_EVAL') or 10)
	env, agent, buffer = generate_model()
	for i in range(evals):
		env, agent, buffer = train_model(env, agent, buffer, episodes_per_eval)
		evaluate_training_result(env, agent)
