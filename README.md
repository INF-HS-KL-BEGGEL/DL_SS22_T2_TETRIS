# Technical Documentation

## Dockerfile

## docker-compose.yml

## requirements.txt

## tetris_env.py

### class TetrisEnv

#### Variables

#### Methods

##### __init__

##### step

##### render

##### reset

##### __calc_reward_new

##### __calculate_hole_count

##### __calculate_bumps

##### __calc_reward

##### __check_lines_for_placement

##### get_epsilon

## tetris_util.py

## tetris.py

### class Tetris

#### Variables

* level
* score
* state
* field
* height
* weight
* width
* x
* y
* zoom
* figure
* next_figure

#### Methods

##### __init__

##### new_figure

##### intersects

##### break_lines

##### go_space

##### go_down

##### freeze

##### go_side

##### rotate

## headless_optimized.prof

## headless_with_render_enabled.prof

## not_headless.prof

## action.py

### class Action

#### Variables

* ROTATE
* FAST_DROP
* MOVE_LEFT
* MOVE_RIGHT
* INSTANT_DROP
* NOTHING

## agent.py

### class DqnAgent

#### Methods

##### __init__

##### policy

##### train

##### collect_policy

##### update_target_network

##### save_checkpoint

##### load_checkpoint

##### save_model

##### load_model

##### _build_dqn_model

## figure.py

### class Figure

#### Variables

* x
* y

#### Methods

##### __init__

#####  image

##### rotate

##### width

##### height

##### x_adjusted

##### y_adjusted

##### __eq__

## game.py

### class Game

#### Methods

##### handle_human_input

##### handle_input

##### handle_action

##### draw_field

##### draw_falling_piece

##### draw_next_figure

##### draw

##### __init__

##### step

##### __record_frame

##### grab

##### screenshot

##### record

##### save_video

##### screenshot_size

## learn.py

### Methods

#### collect_gameplay_experience

#### generate_model

#### train_model

#### evaluate_training_result

## replay.py

### class Replay Buffer

#### Methods

##### __init__

##### store_gameplay_experience

##### sample_gameplay_batch

## shape.py

### class Rotation

#### Methods

##### __init__

### class Shape

#### Methods

##### __init__

##### height

##### width

##### color

##### rotation

##### offset_x

##### offset_y

##### rotation_count







