import pygame
import random

# Init
pygame.init()
WIDTH, HEIGHT = 300, 650  # Extra height for score
ROWS, COLS = 20, 10
BLOCK_SIZE = WIDTH // COLS
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Grid & Colors
grid = [[(0, 0, 0) for _ in range(COLS)] for _ in range(ROWS)]
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}
COLORS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128),
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)
]
font = pygame.font.SysFont("Arial", 24)

def rotate(shape):
    return [list(row)[::-1] for row in zip(*shape)]

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(win, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE + 50, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(win, (50, 50, 50), (x * BLOCK_SIZE, y * BLOCK_SIZE + 50, BLOCK_SIZE, BLOCK_SIZE), 1)

def clear_lines():
    global grid
    new_grid = [row for row in grid if (0, 0, 0) in row]
    lines_cleared = ROWS - len(new_grid)
    for _ in range(lines_cleared):
        new_grid.insert(0, [(0, 0, 0) for _ in range(COLS)])
    grid = new_grid
    return lines_cleared

class Piece:
    def __init__(self):
        self.shape = random.choice(list(SHAPES.values()))
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def draw(self):
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val:
                    pygame.draw.rect(win, self.color,
                                     ((self.x + c) * BLOCK_SIZE, (self.y + r) * BLOCK_SIZE + 50, BLOCK_SIZE, BLOCK_SIZE))

    def valid(self, dx=0, dy=0, shape_override=None):
        shape = shape_override if shape_override else self.shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    nx = self.x + dx + c
                    ny = self.y + dy + r
                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return False
                    if ny >= 0 and grid[ny][nx] != (0, 0, 0):
                        return False
        return True

    def lock(self):
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val:
                    grid[self.y + r][self.x + c] = self.color

def main():
    clock = pygame.time.Clock()
    fall_speed = 500  # ms
    fall_timer = 0

    current = Piece()
    score = 0
    running = True

    key_cooldown = 150
    last_move = 0
    last_rotate = 0

    while running:
        win.fill((0, 0, 0))
        time_passed = clock.tick(60)
        fall_timer += time_passed
        last_move += time_passed
        last_rotate += time_passed

        # Auto fall
        if fall_timer >= fall_speed:
            if current.valid(dy=1):
                current.y += 1
            else:
                current.lock()
                score += 5
                lines = clear_lines()
                score += lines * 100
                current = Piece()
                if not current.valid():
                    print("Game Over")
                    running = False
            fall_timer = 0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                while current.valid(dy=1):
                    current.y += 1
                current.lock()
                score += 5
                lines = clear_lines()
                score += lines * 100
                current = Piece()
                if not current.valid():
                    print("Game Over")
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    while current.valid(dy=1):
                        current.y += 1
                    current.lock()
                    score += 5
                    lines = clear_lines()
                    score += lines * 100
                    current = Piece()
                    if not current.valid():
                        print("Game Over")
                        running = False

        # Movement keys (grid-based)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and last_move >= key_cooldown:
            if current.valid(dx=-1):
                current.x -= 1
                last_move = 0
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and last_move >= key_cooldown:
            if current.valid(dx=1):
                current.x += 1
                last_move = 0
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]) and last_rotate >= key_cooldown:
            rotated = rotate(current.shape)
            if current.valid(shape_override=rotated):
                current.shape = rotated
                last_rotate = 0

        # Draw game
        draw_grid()
        current.draw()
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(score_text, (10, 10))
        pygame.display.update()

    pygame.quit()

main()
