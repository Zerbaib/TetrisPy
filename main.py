import pygame
import random
import sys

# Initialisation de Pygame
pygame.init()

# Paramètres du jeu
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 500
BLOCK_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = 10, 20
FPS = 15
FONT_SIZE = 30

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Formes des blocs du Tetris (avec les 4 rotations possibles)
SHAPES = [
    [[1, 1, 1, 1]],                                 # I-shape
    [[1, 1, 1], [0, 1, 0]],                         # T-shape
    [[1, 1, 0], [0, 1, 1]],                         # Z-shape
    [[0, 1, 1], [1, 1, 0]],                         # S-shape
    [[1, 1, 1], [0, 0, 1]],                         # L-shape
    [[1, 1, 1], [1, 0, 0]],                         # J-shape
    [[1, 1], [1, 1]],                               # O-shape
]

# Couleurs des blocs
SHAPE_COLORS = [CYAN, MAGENTA, YELLOW, GREEN, BLUE, ORANGE, RED]

# Classe pour gérer le jeu
class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()  # Nouvelle propriété pour la prochaine pièce
        self.next_piece_x = GRID_WIDTH + 2
        self.next_piece_y = 4
        self.game_over = False
        self.score = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 0.5  # Vitesse de descente initiale (secondes)
        self.lines_completed = 0
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.can_rotate = True
        self.rotate_delay = 150
        self.last_rotate_time = pygame.time.get_ticks()
        self.move_delay = 100  # Délai entre chaque déplacement latéral (100ms ici)
        self.last_move_time = pygame.time.get_ticks()

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(SHAPE_COLORS)
        piece = {
            'shape': shape,
            'color': color,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }
        return piece

    def check_collision(self, x, y, shape):
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j] and (
                    x + j < 0 or x + j >= GRID_WIDTH or y + i >= GRID_HEIGHT or self.grid[y + i][x + j]
                ):
                    return True
        return False

    def place_piece(self, x, y, shape):
        for i in range(len(shape)):
            for j in range(len(shape[0])):
                if shape[i][j]:
                    self.grid[y + i][x + j] = shape[i][j]

    def check_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0] * GRID_WIDTH)
            self.lines_completed += 1
        if lines_to_clear:
            self.score += (10 * (2 ** (len(lines_to_clear) - 1))) * self.level

    def draw_grid(self):
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                # Si la case est occupée par un bloc, dessiner en gris
                if self.grid[i][j]:
                    pygame.draw.rect(self.screen, (128, 128, 128), (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                # Sinon, dessiner en utilisant la couleur du bloc
                else:
                    pygame.draw.rect(self.screen, BLACK, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.screen, WHITE, (j * BLOCK_SIZE + 1, i * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))

    def draw_piece(self):
        for i in range(len(self.current_piece['shape'])):
            for j in range(len(self.current_piece['shape'][0])):
                if self.current_piece['shape'][i][j]:
                    pygame.draw.rect(
                        self.screen,
                        self.current_piece['color'],
                        ((self.current_piece['x'] + j) * BLOCK_SIZE, (self.current_piece['y'] + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

    def rotate_piece_clockwise(self, shape):
        return [[shape[j][i] for j in range(len(shape))] for i in range(len(shape[0]) - 1, -1, -1)]

    def rotate_piece(self):
        now = pygame.time.get_ticks()
        if now - self.last_rotate_time > self.rotate_delay:
            new_shape = self.rotate_piece_clockwise(self.current_piece['shape'])
            if not self.check_collision(self.current_piece['x'], self.current_piece['y'], new_shape):
                self.current_piece['shape'] = new_shape
            self.last_rotate_time = now

    def move_piece(self, dx, dy):
        now = pygame.time.get_ticks()
        if now - self.last_move_time > self.move_delay:
            if not self.check_collision(self.current_piece['x'] + dx, self.current_piece['y'] + dy, self.current_piece['shape']):
                self.current_piece['x'] += dx
                self.current_piece['y'] += dy
            self.last_move_time = now

    def draw_next_piece(self):
        for i in range(len(self.next_piece['shape'])):
            for j in range(len(self.next_piece['shape'][0])):
                if self.next_piece['shape'][i][j]:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece['color'],
                        ((self.next_piece_x + j) * BLOCK_SIZE, (self.next_piece_y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_completed}", True, WHITE)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 3 * FONT_SIZE))
        self.screen.blit(level_text, (10, SCREEN_HEIGHT - 2 * FONT_SIZE))
        self.screen.blit(lines_text, (10, SCREEN_HEIGHT - FONT_SIZE))

    def run(self):
        while not self.game_over:
            self.screen.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.move_piece(-1, 0)
            if keys[pygame.K_RIGHT]:
                self.move_piece(1, 0)
            if keys[pygame.K_DOWN]:
                self.fall_speed = 0.05  # Vitesse de descente rapide lorsque la touche de descente est enfoncée
            else:
                self.fall_speed = 0.5  # Vitesse de descente normale
            if keys[pygame.K_UP]:
                self.rotate_piece()

            now = pygame.time.get_ticks()
            if now - self.fall_time > 1000 * self.fall_speed:
                self.fall_time = now
                if not self.check_collision(self.current_piece['x'], self.current_piece['y'] + 1, self.current_piece['shape']):
                    self.current_piece['y'] += 1
                else:
                    self.place_piece(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape'])
                    self.check_lines()
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    self.current_piece['x'] = GRID_WIDTH // 2 - len(self.current_piece['shape'][0]) // 2
                    self.current_piece['y'] = 0
                    if self.check_collision(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape']):
                        self.game_over = True

            self.draw_grid()
            self.draw_piece()
            self.draw_next_piece()
            self.draw_score()

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
