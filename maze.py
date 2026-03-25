# maze.py
import random
import pygame
from config import WALL_COLOR, BG_COLOR, WINDOW_W, VIEW_H

DIRS = {
    'N': (0, -1, 0),
    'S': (0,  1, 2),
    'W': (-1, 0, 3),
    'E': ( 1, 0, 1),
}
OPPOSITE = {0: 2, 1: 3, 2: 0, 3: 1}

class Cell:
    def __init__(self, col, row):
        self.col     = col
        self.row     = row
        self.walls   = [True, True, True, True]
        self.visited = False

def grid_index(col, row, cols, rows):
    if 0 <= col < cols and 0 <= row < rows:
        return row * cols + col
    return None

def generate_maze(cols, rows):
    grid  = [Cell(c, r) for r in range(rows) for c in range(cols)]
    start = grid[0]
    start.visited = True
    stack = [start]
    while stack:
        cur     = stack[-1]
        nb_list = []
        for _d, (dx, dy, widx) in DIRS.items():
            nc, nr = cur.col + dx, cur.row + dy
            idx    = grid_index(nc, nr, cols, rows)
            if idx is not None and not grid[idx].visited:
                nb_list.append((grid[idx], widx))
        if nb_list:
            nb, widx                  = random.choice(nb_list)
            cur.walls[widx]           = False
            nb.walls[OPPOSITE[widx]]  = False
            nb.visited = True
            stack.append(nb)
        else:
            stack.pop()
    for cell in grid:
        cell.visited = False
    return grid

def draw_maze(surface, grid, cell_size, cam_ix, cam_iy):
    for cell in grid:
        sx = cell.col * cell_size - cam_ix
        sy = cell.row * cell_size - cam_iy
        if sx + cell_size < 0 or sx > WINDOW_W or sy + cell_size < 0 or sy > VIEW_H:
            continue
        pygame.draw.rect(surface, BG_COLOR, (sx, sy, cell_size, cell_size))
        if cell.walls[0]:
            pygame.draw.line(surface, WALL_COLOR, (sx, sy), (sx + cell_size, sy), 2)
        if cell.walls[1]:
            pygame.draw.line(surface, WALL_COLOR, (sx + cell_size, sy), (sx + cell_size, sy + cell_size), 2)
        if cell.walls[2]:
            pygame.draw.line(surface, WALL_COLOR, (sx + cell_size, sy + cell_size), (sx, sy + cell_size), 2)
        if cell.walls[3]:
            pygame.draw.line(surface, WALL_COLOR, (sx, sy + cell_size), (sx, sy), 2)
