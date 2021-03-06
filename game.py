from cv2 import VideoWriter_fourcc
import pygame, os, sys, cv2
import os.path
from datetime import datetime

import numpy as np
import tensorflow as tf

from action import Action, ACTION_SPACE_SIZE

# Initialize the game engine
from tetris import Tetris
from tetris_util import colors, WHITE, GRAY, BLACK, GREEN, ORANGE


ACTION_MAP = {
    Action.ROTATE.value: pygame.K_UP,
    Action.FAST_DROP.value: pygame.K_DOWN,
    Action.MOVE_LEFT.value: pygame.K_LEFT,
    Action.MOVE_RIGHT.value: pygame.K_RIGHT,
    Action.INSTANT_DROP.value: pygame.K_SPACE,
    Action.NOTHING.value: None
}

class Game:

    def handle_human_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.KEYDOWN:
                self.handle_input(event.key)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.pressing_down = False

    def handle_input(self, key):
        if key == pygame.K_UP:
            self.tetris.rotate()
        if key == pygame.K_DOWN:
            self.pressing_down = True
        if key == pygame.K_LEFT:
            self.tetris.go_side(-1)
        if key == pygame.K_RIGHT:
            self.tetris.go_side(1)
        if key == pygame.K_SPACE:
            self.tetris.go_space()
        if key == pygame.K_ESCAPE:
            self.tetris.__init__(20, 10)

    def handle_action(self, action):
        for event in pygame.event.get():
            pass  # this is stupid

        key = ACTION_MAP[action]
        if key is None:
            return
        self.handle_input(key)

    def draw_field(self):
        for i in range(self.tetris.height):
            for j in range(self.tetris.width):
                pygame.draw.rect(self.screen, GRAY,
                                 [self.tetris.x + self.tetris.zoom * j, self.tetris.y + self.tetris.zoom * i,
                                  self.tetris.zoom, self.tetris.zoom], 1)
                if self.tetris.field[i][j] > 0:
                    pygame.draw.rect(self.screen, colors[int(self.tetris.field[i][j])],
                                     [self.tetris.x + self.tetris.zoom * j + 1,
                                      self.tetris.y + self.tetris.zoom * i + 1, self.tetris.zoom - 2,
                                      self.tetris.zoom - 1])

    def draw_falling_piece(self):
        if self.tetris.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.tetris.figure.image():
                        pygame.draw.rect(self.screen, colors[self.tetris.figure.color],
                                         [self.tetris.x + self.tetris.zoom * (j + self.tetris.figure.x) + 1,
                                          self.tetris.y + self.tetris.zoom * (i + self.tetris.figure.y) + 1,
                                          self.tetris.zoom - 2, self.tetris.zoom - 2])

    def draw_next_figure(self):
        if self.tetris.next_figure is not None:
            pygame.draw.rect(self.screen, GRAY,
                             [self.tetris.x + self.tetris.zoom * self.tetris.width + self.tetris.zoom,
                              self.tetris.y, 5 * self.tetris.zoom, 5 * self.tetris.zoom], 2)
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    x = self.tetris.x + self.tetris.zoom * self.tetris.width + self.tetris.zoom * (j + 1 + (
                        0.5 if self.tetris.next_figure.width() % 2 == 1 else 0)) + self.tetris.zoom / 2 + 2
                    y = self.tetris.y + self.tetris.zoom * (i + (
                        0.5 if self.tetris.next_figure.height() % 2 == 1 else 0)) + self.tetris.zoom / 2 + 2
                    if p in self.tetris.next_figure.image():
                        pygame.draw.rect(self.screen, colors[self.tetris.next_figure.color],
                                         [x, y,
                                          self.tetris.zoom - 2, self.tetris.zoom - 2])

    def draw(self):
        if self.recording or 'headless' not in sys.argv:
            self.screen.fill(WHITE)
            self.draw_field()
            self.draw_falling_piece()
            self.draw_next_figure()

            font = pygame.font.SysFont('Calibri', 25, True, False)
            font1 = pygame.font.SysFont('Calibri', 65, True, False)
            text = font.render("Score: " + str(self.tetris.score), True, BLACK)
            text_game_over = font1.render("Game Over", True, (255, 125, 0))
            text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

            self.screen.blit(text, [0, 0])
            if self.tetris.state == "gameover":
                self.screen.blit(text_game_over, [20, 200])
                self.screen.blit(text_game_over1, [25, 265])

            pygame.display.flip()

    def __init__(self, fps=25):
        self.headless = 'headless' in sys.argv
        if self.headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()

        self.size = (500, 500)
        self.screen = pygame.display.set_mode(self.size)

        pygame.display.set_caption("Tetris")

        # Loop until the user clicks the close button.
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.tetris = Tetris(20, 10)
        self.counter = 0

        self.pressing_down = False
        self.snapshot_dir_name = None
        self.frame = 0
        self.games_played = 0
        self.recording = False
        self.start_time = datetime.now().strftime("snapshot_%Y-%m-%d_%H-%M-%S")

    def step(self, mode='human', action=None, action_q=None):
        if self.tetris.figure is None:
            self.tetris.new_figure()
        if self.recording:
            self.__record_frame(action, action_q)

        max_counter = 2 if mode == 'ai' else 100000
        self.counter += 1
        if self.counter > max_counter:
            self.counter = 0

        if self.counter % (self.fps // self.tetris.level // 2) == 0 or self.pressing_down:
            if self.tetris.state == "start":
                self.tetris.go_down()

        if mode == 'human':
            self.handle_human_input()
        else:
            self.pressing_down = False
            self.handle_action(action)

    def __record_frame(self, action=None, action_q=None):
        self.frame += 1
        copied_screen = self.screen.copy()
        if action is not None and action_q is not None:
            max_rect_length = 50
            rect_height = 10
            font = pygame.font.SysFont('Calibri', rect_height)
            rect_pos_x = 420
            sum = tf.math.reduce_sum(tf.abs(action_q)).numpy()
            argmax = action = np.argmax(action_q.numpy()[0], axis=0)
            color = BLACK
            for i in range(ACTION_SPACE_SIZE):
                color = BLACK
                if i == action:
                    if argmax == action:
                        color = GREEN
                    else:
                        color = ORANGE
                value = action_q[0][i].numpy() / sum
                length = min(max_rect_length * abs(value), max_rect_length)
                rect_origin = rect_pos_x if value >= 0 else rect_pos_x - length
                pygame.draw.rect(copied_screen, color, [rect_origin, 300 + i * rect_height * 1.5, length, rect_height])
                text = font.render(Action(i).name, True, BLACK)
                copied_screen.blit(text, [310, 300 + i * rect_height * 1.5])
                value_text = font.render(str(value), True, BLACK)
                copied_screen.blit(value_text, [450, 300 + i * rect_height * 1.5])
        # 	pygame.draw.rect(self.copied_screen, BLACK,
        # 					 [self.tetris.x + self.tetris.zoom * self.tetris.width + self.tetris.zoom,
        # 					  self.tetris.y, 5 * self.tetris.zoom, 5 * self.tetris.zoom], 2)
        pygame.image.save(copied_screen, f'{self.snapshot_dir_name}/frame-{self.frame:05d}.png')

    def grab(self, x, y, width, height):
        "Grab a part of the screen"
        # get the dimension of the surface
        rect = pygame.Rect(x, y, width, height)
        # copy the part of the screen
        sub = self.screen.subsurface(rect)
        # create another surface with dimensions
        # This is done to unlock the screen surface
        screenshot = pygame.Surface((width, height))
        screenshot.blit(sub, (0, 0))
        return screenshot

    def screenshot(self):
        surface = self.grab(self.tetris.x, self.tetris.y, 500 - self.tetris.x - (500 - (
                self.tetris.x + self.tetris.zoom * self.tetris.width + self.tetris.zoom + 5 * self.tetris.zoom)),
                            500 - self.tetris.y)
        image = pygame.surfarray.array3d(surface)
        return image

    def record(self):
        if not self.headless:
            return

        self.frame = 0
        self.recording = True
        self.snapshot_dir_name = "snapshots/" + self.start_time

        if not os.path.exists("snapshots"):
            os.mkdir("snapshots")
        if not os.path.exists(self.snapshot_dir_name):
            os.mkdir(self.snapshot_dir_name)
        self.snapshot_dir_name += "/game_" + str(self.games_played)
        if not os.path.exists(self.snapshot_dir_name):
            os.mkdir(self.snapshot_dir_name)

    def save_video(self):
        self.recording = False
        if not self.headless:
            return
        video_name = self.snapshot_dir_name + ".mp4"

        self.draw()
        self.__record_frame()

        images = [img for img in sorted(os.listdir(self.snapshot_dir_name)) if img.endswith(".png")]
        frame = cv2.imread(os.path.join(self.snapshot_dir_name, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(video_name, 0x7634706d, self.fps, (width, height))
        for image in images:
            video.write(cv2.imread(os.path.join(self.snapshot_dir_name, image)))

        cv2.destroyAllWindows()
        video.release()

        for file_name in os.listdir(self.snapshot_dir_name):
            file = self.snapshot_dir_name + "/" + file_name
            if os.path.isfile(file):
                os.remove(file)

        os.rmdir(self.snapshot_dir_name, dir_fd=None)

        print("Created video!")

    def screenshot_size(self):
        return (500 - self.tetris.x - (500 - (
                self.tetris.x + self.tetris.zoom * self.tetris.width + self.tetris.zoom + 5 * self.tetris.zoom)),
                500 - self.tetris.y, 3)


if __name__ == '__main__':

    game = Game()

    while not game.done:
        game.step()
        game.draw()
        game.clock.tick(game.fps)

    pygame.quit()
