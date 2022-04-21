from collections import deque
from random import random

import gym
import keras
import numpy as np
import tensorflow as tf
from keras import Input, Model
from keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Dropout, Flatten, Dense
from keras.optimizer_v2.adam import Adam

# RL Constants:
DISCOUNT               = 0.99
REPLAY_MEMORY_SIZE     = 3_000   # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 1_000   # Minimum number of steps in a memory to start training
UPDATE_TARGET_EVERY    = 20      # Terminal states (end of episodes)
MIN_REWARD             = 1000    # For model save
SAVE_MODEL_EVERY       = 1000    # Episodes
SHOW_EVERY             = 20      # Episodes
EPISODES               = 10_000  # Number of episodes
#  Stats settings
AGGREGATE_STATS_EVERY = 20  # episodes
SHOW_PREVIEW          = False
MINIBATCH_SIZE = 16


class DQNAgent:
    def __init__(self, name, env):
        self.env = env
        self.name = name

        # Main model
        self.model = self.create_model()

        # Target network
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        # An array with last n steps for training
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        # Custom tensorboard object
        self.tensorboard = tf.keras.callbacks.TensorBoard(log_dir='./logs', histogram_freq=1)

        # Used to count when to update target network with main network's weights
        self.target_update_counter = 0

    # Creates the model with the given specifications:
    def create_model(self):
        return tf.keras.Sequential(layers=[
            keras.Input(shape=self.env.getShape(), batch_size=MINIBATCH_SIZE),
            tf.keras.layers.Conv2D(filters=2, kernel_size=3, activation='relu'),
            tf.keras.layers.MaxPool2D(pool_size=(3, 3)),
            tf.keras.layers.Conv2D(filters=4, kernel_size=3, activation='relu'),
            tf.keras.layers.MaxPool2D(pool_size=(3, 3)),
            tf.keras.layers.Conv2D(filters=8, kernel_size=3, activation='relu'),
            tf.keras.layers.MaxPool2D(pool_size=(3, 3)),

            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(units=1000, activation='relu'),
            tf.keras.layers.Dense(units=1000, activation='relu'),
            tf.keras.layers.Dense(units=self.env.ACTION_SPACE_SIZE, activation='softmax', name='output')
        ])

    # Adds step's data to a memory replay array
    # (observation space, action, reward, new observation space, done)
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    # Trains main network every step during episode
    def train(self, terminal_state):
        # Start training only if certain number of samples is already saved
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states.reshape(-1, self.env.ENVIRONMENT_SHAPE))

        # Get future states from minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried
        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states.reshape(-1, self.env.ENVIRONMENT_SHAPE))

        X = []
        y = []

        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of equation here
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)

        # Fit on all samples as one batch, log only on terminal state
        self.model.fit(x=np.array(X).reshape(-1, self.env.ENVIRONMENT_SHAPE),
                       y=np.array(y),
                       batch_size=MINIBATCH_SIZE, verbose=0,
                       shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter += 1

        # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    # Queries main network for Q values given current observation space (environment state)
    def get_qs(self, state):
        return self.model.predict(state.reshape(-1, self.env.ENVIRONMENT_SHAPE))