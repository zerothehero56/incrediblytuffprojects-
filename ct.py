import pygame
import random
import sys

pygame.init()

# Constants
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 60
FPS = 60 

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.generate()
    
    def generate(self):
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self._carve(1, 1)
    
    def _carve(self, x, y):
        self.grid[y][x] = 0
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.grid[ny][nx] == 1:
                self.grid[y + dy // 2][x + dx // 2] = 0
                self._carve(nx, ny)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.maze = Maze(GRID_SIZE, GRID_SIZE)
        self.player_pos = [1, 1]
        self.goal_pos = [GRID_SIZE - 2, GRID_SIZE - 2]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.maze.generate()
                    self.player_pos = [1, 1]
        
        keys = pygame.key.get_pressed()
        x, y = self.player_pos
        
        if keys[pygame.K_UP] and y > 0 and self.maze.grid[y - 1][x] == 0:
            self.player_pos[1] -= 1
        if keys[pygame.K_DOWN] and y < GRID_SIZE - 1 and self.maze.grid[y + 1][x] == 0:
            self.player_pos[1] += 1
        if keys[pygame.K_LEFT] and x > 0 and self.maze.grid[y][x - 1] == 0:
            self.player_pos[0] -= 1
        if keys[pygame.K_RIGHT] and x < GRID_SIZE - 1 and self.maze.grid[y][x + 1] == 0:
            self.player_pos[0] += 1
        
        return True
    
    def draw(self):
        self.screen.fill(WHITE)
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.maze.grid[y][x] == 1:
                    pygame.draw.rect(self.screen, BLACK, rect)
        
        goal_rect = pygame.Rect(self.goal_pos[0] * CELL_SIZE, self.goal_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, RED, goal_rect)
        
        player_rect = pygame.Rect(self.player_pos[0] * CELL_SIZE, self.player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, GREEN, player_rect)
        
        pygame.draw.line(self.screen, GRAY, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)
        controls_text = self.font.render("Controls: Arrow Keys to move | R to regenerate maze", True, BLACK)
        self.screen.blit(controls_text, (10, HEIGHT - 50))
        
        if self.player_pos == self.goal_pos:
            win_text = self.font.render("YOU WIN! Press R for new maze", True, BLUE)
            self.screen.blit(win_text, (WIDTH // 2 - 150, HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()