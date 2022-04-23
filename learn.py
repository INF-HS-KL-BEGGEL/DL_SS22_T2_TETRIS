from agent import DqnAgent
from replay import ReplayBuffer
from tetris_env import TetrisEnv


def collect_gameplay_experience(env, agent, buffer):
	"""
	The collect_gameplay_experience function plays the game "env" with the
	instructions produced by "agent" and stores the gameplay experiences
	into "buffer" for later training.
	"""
	state = env.reset()
	done = False
	while not done:
		action = agent.policy(state)
		next_state, reward, done, info = env.step(action)
		buffer.store_gameplay_experience(state, next_state, reward, action, done)
		state = next_state


def train_model(episodes=6000):
	env = TetrisEnv()
	agent = DqnAgent()
	buffer = ReplayBuffer()
	for episode_cnt in range(episodes):  # Train the agent for 6000 episodes of the game
		collect_gameplay_experience(env, agent, buffer)
		gameplay_experience_batch = buffer.sample_gameplay_batch()
		loss = agent.train(gameplay_experience_batch)
		if episode_cnt % 20 == 0:
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
