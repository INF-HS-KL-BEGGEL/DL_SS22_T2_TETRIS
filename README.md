# Development & Running

## Docker
This project uses docker to run on university servers.
Building the Image goes as follows:
```shell
docker build . -t tetris:latest
```
You can start the image using the provided `docker-compose.yml` using `docker-compose up -d`. This also starts an instance of TensorBoard, which will be accessible on port 6010.

## Requirements
All python requirements are listed in `requirements.txt`, you can install them by using `python3 -m pip install -r requirements.txt`.

## Running the code
### Training
Training is started via the `learn.py` file.
For training without rendering, pass the `headless` argument.

### Tetris
If you want to run tetris alone, start `game.py`.

# Code Documentation

## Tetris with pygame
The base of this implementation is based on this [article](https://levelup.gitconnected.com/writing-tetris-in-python-2a16bddb5318).

Tetris itself consists of the following files:
* game.py
* tetris.py
* figure.py
* tetris_util.py
* shape.py

## Agent
The agent owns the neural networks and is in charge of generating actions based on states that are given to them.

The networks are managed through a CheckpointManager, which will periodically save checkpoints of the networks in the `./checkpoints` directory.

The policy-methods should be used for collecting actions. The `collect_policy`-method should be used for training, as it has an optional epsilon parameter for generating random actions. If no epsilon is given, the default value of 5% is used.
For playing the game without training the normal `policy`-method should be used, as it will always return the action decided by the neural network.

If you want to change the network architecture, do so in the `_build_dqn_model`-method, as multiple networks are required for the double-q-learning process and this ensures that both networks are of the same architecture at all times.

## Replay Memory
The replay memory is a wrapper around a builtin deque. It stores the last state, the action the agent decided, the calculated reward for said action, and the state that followed.
This memory is sampled randomly during training.

## Tetris Environment
The tetris environment uses the game and the agent to create a learning environment for the network. It describes how the rewards are calculated for each action and controls the rendering and updating of the game loop in the learning process.

Important methods are the `step`-method for updating the game clock, the `render`-method for rendering the game and the `__calc_reward_new`-method, which uses a couple of helper methods to determine how good a move was and how the network should be rewarded.
The Reward depends on multiple factors, which each have an own weight. The `__calculate_hole_count`-method calculated how many holes are in the Current block structure with a hole being defined as an empty space below a block.
The `__calculate_bumps`-method sums up the height difference between each neighbouring column. There is also a factor called `reward_bonus`, which gives the Network a bonus reward for doing actions lower to the ground. This part of the reward is set to 0 if the height of the block-tower is larger than 9.
Additionally the current Score of the Game is also used in the Reward calculation, since scoring a line is ultimately the goal of the Network.

The final weights for the factors by trial and error came out to: (-10 * `hole_delta`) + (-2.5 * `bump_delta`) + (1000 * `score_delta`) + (0.2 * `reward_bonus`). This seemed to give us a consistant learning_curve.

## Training


