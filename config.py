# config.py
import os
import pygame

pygame.mixer.init()
pygame.init()

winz = 0
WINDOW_W = 500
WINDOW_H = 535
HUD_H = 35
VIEW_H = WINDOW_H - HUD_H
player_color = (255, 255, 0)

vis = 4
CELL_SIZE = 500 / vis

MAZE_COLS = 20
MAZE_ROWS = MAZE_COLS

WALL_COLOR = (40, 40, 40)
BG_COLOR = (220, 220, 220)
GOAL_COLOR = (30, 160, 30)

FPS = 240
SKIN_COST = 10

LERP_CAM = 0.12
LERP_PLAYER = 0.18

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Maze Game")
