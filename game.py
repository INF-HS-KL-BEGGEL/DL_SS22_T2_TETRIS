import pygame
import cv2

# Initialize the game engine
from tetris import Tetris
from tetris_util import colors, WHITE, GRAY, BLACK

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
            self.game.rotate()
        if key == pygame.K_DOWN:
            self.pressing_down = True
        if key == pygame.K_LEFT:
            self.game.go_side(-1)
        if key == pygame.K_RIGHT:
            self.game.go_side(1)
        if key == pygame.K_SPACE:
            self.game.go_space()
        if key == pygame.K_ESCAPE:
            self.game.__init__(20, 10)

    def handle_action(self, action):
        key = self.map_action_to_key(action)
        self.handle_input(key)

    def map_action_to_key(self, action):
        pass


    def draw_field(self):
        for i in range(self.game.height):
            for j in range(self.game.width):
                pygame.draw.rect(self.screen, GRAY, [self.game.x + self.game.zoom * j, self.game.y + self.game.zoom * i, self.game.zoom, self.game.zoom], 1)
                if self.game.field[i][j] > 0:
                    pygame.draw.rect(self.screen, colors[self.game.field[i][j]],
                                     [self.game.x + self.game.zoom * j + 1, self.game.y + self.game.zoom * i + 1, self.game.zoom - 2, self.game.zoom - 1])

    def draw_falling_piece(self):
        if self.game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.figure.image():
                        pygame.draw.rect(self.screen, colors[self.game.figure.color],
                                         [self.game.x + self.game.zoom * (j + self.game.figure.x) + 1,
                                          self.game.y + self.game.zoom * (i + self.game.figure.y) + 1,
                                          self.game.zoom - 2, self.game.zoom - 2])

    def draw_next_figure(self):
        if self.game.next_figure is not None:
            pygame.draw.rect(self.screen, BLACK, [self.game.x + self.game.zoom * self.game.width + self.game.zoom, self.game.y, 5 * self.game.zoom, 5 * self.game.zoom], 2)
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    x = self.game.x + self.game.zoom * self.game.width + self.game.zoom * (j + 1 + (0.5 if self.game.next_figure.width() % 2 == 1 else 0)) + self.game.zoom / 2 + 2
                    y = self.game.y + self.game.zoom * (i + (0.5 if self.game.next_figure.height() % 2 == 1 else 0)) + self.game.zoom / 2 + 2
                    if p in self.game.next_figure.image():
                        pygame.draw.rect(self.screen, colors[self.game.next_figure.color],
                                         [x, y,
                                          self.game.zoom - 2, self.game.zoom - 2])

    def draw(self):
        self.screen.fill(WHITE)
        self.draw_field()
        self.draw_falling_piece()
        self.draw_next_figure()

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render("Score: " + str(self.game.score), True, BLACK)
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        self.screen.blit(text, [0, 0])
        if self.game.state == "gameover":
            self.screen.blit(text_game_over, [20, 200])
            self.screen.blit(text_game_over1, [25, 265])

        pygame.display.flip()

    def __init__(self):
        pygame.init()

        self.size = (500, 500)
        self.screen = pygame.display.set_mode(self.size)

        pygame.display.set_caption("Tetris")

        # Loop until the user clicks the close button.
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = 25
        self.game = Tetris(20, 10)
        self.counter = 0

        self.pressing_down = False

    def step(self, mode='human', action=None):
        if self.game.figure is None:
            self.game.new_figure()
        self.counter += 1
        if self.counter > 100000:
            self.counter = 0

        if self.counter % (self.fps // self.game.level // 2) == 0 or self.pressing_down:
            if self.game.state == "start":
                self.game.go_down()

        if mode is 'human':
            self.handle_input()
        else:
            self.handle_action(action)

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


if __name__ == '__main__':

    game = Game()

    # while not game.done:
    game.step()
    game.draw()
    test = game.grab(game.game.x, game.game.y, 500 - game.game.x - (500 - (game.game.x + game.game.zoom * game.game.width + game.game.zoom + 5 * game.game.zoom)), 500 - game.game.y)
    print(pygame.surfarray.array3d(test))
    print(pygame.surfarray.array3d(test).shape)
    pygame.image.save(test, "screenshot.png")
    cv2.imshow('image window', pygame.surfarray.array3d(test))
    cv2.waitKey(0)
        # game.clock.tick(game.fps)
        # input()

    # pygame.quit()
