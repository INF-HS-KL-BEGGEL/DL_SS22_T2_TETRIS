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

## Training


