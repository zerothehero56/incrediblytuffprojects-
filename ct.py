import random
import sys
import time
import pygame
import os
 
# maze game cause sigma
 
script_dir    = os.path.dirname(__file__)
save_path     = os.path.join(script_dir, "data.txt")
skin_save_path = os.path.join(script_dir, "skins_save.txt")
 
WINDOW_W = 500
WINDOW_H = 535
HUD_H    = 35
VIEW_H   = WINDOW_H - HUD_H
 
pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Maze Game")
 
# ── Global skin state ────────────────────────────────────────────────────────
owned_skins  = ["0_Default.png"]
equipped_skin = "0_Default.png"
 
def save_skin_state():
    with open(skin_save_path, "w") as fh:
        fh.write(equipped_skin + "\n")
        fh.write(",".join(owned_skins))
 
def load_skin_state():
    global owned_skins, equipped_skin
    if os.path.exists(skin_save_path):
        with open(skin_save_path, "r") as fh:
            lines = fh.read().splitlines()
            if len(lines) >= 2:
                equipped_skin = lines[0]
                owned_skins   = lines[1].split(",")
 
load_skin_state()
 
# ── Wins ─────────────────────────────────────────────────────────────────────
try:
    with open(save_path, "r") as fh:
        wins = int(fh.read())
except FileNotFoundError:
    wins = 0
 
def save_wins():
    with open(save_path, "w") as fh:
        fh.write(str(wins))
 
# ── Config ───────────────────────────────────────────────────────────────────
CELL_SIZE  = 100
MAZE_COLS  = 20
MAZE_ROWS  = 20
WALL_COLOR = (40, 40, 40)
BG_COLOR   = (220, 220, 220)
GOAL_COLOR = (30, 160, 30)
FPS        = 60
SKIN_COST  = 10
 
# lerp factors (per frame at 60 fps; scaled by dt each tick)
LERP_CAM    = 0.12
LERP_PLAYER = 0.18
 
pygame.mixer.init()
sound_200 = pygame.mixer.Sound("200.wav")
sound_300 = pygame.mixer.Sound("300.wav")
 
# ── Maze ─────────────────────────────────────────────────────────────────────
DIRS = {
    'N': (0, -1, 0),
    'S': (0,  1, 2),
    'W': (-1, 0, 3),
    'E': ( 1, 0, 1),
}
OPPOSITE = {0: 2, 1: 3, 2: 0, 3: 1}
 
class Cell:
    def __init__(self, col, row):
        self.col   = col
        self.row   = row
        self.walls = [True, True, True, True]
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
        cur = stack[-1]
        nb_list = []
        for _d, (dx, dy, widx) in DIRS.items():
            nc, nr = cur.col + dx, cur.row + dy
            idx = grid_index(nc, nr, cols, rows)
            if idx is not None and not grid[idx].visited:
                nb_list.append((grid[idx], widx))
        if nb_list:
            nb, widx = random.choice(nb_list)
            cur.walls[widx] = False
            nb.walls[OPPOSITE[widx]] = False
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
 
# ── Skin helpers ──────────────────────────────────────────────────────────────
def load_all_skin_images():
    imgs = {}
    folder = "skins"
    if os.path.exists(folder):
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".png"):
                imgs[fname] = pygame.image.load(os.path.join(folder, fname)).convert_alpha()
    return imgs
 
def make_player_surf(skin_name, all_imgs, radius):
    diam = radius * 2
    if skin_name not in all_imgs:
        return None
    scaled = pygame.transform.scale(all_imgs[skin_name], (diam, diam))
    # circular clip mask
    mask = pygame.Surface((diam, diam), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    scaled.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return scaled
 
# ── Skin menu ─────────────────────────────────────────────────────────────────
def skinmenu():
    global wins, owned_skins, equipped_skin
 
    font     = pygame.font.Font(None, 26)
    big_font = pygame.font.Font(None, 44)
 
    skin_folder = "skins"
    skin_list   = []
    if os.path.exists(skin_folder):
        for fname in sorted(os.listdir(skin_folder)):
            if fname.endswith(".png"):
                img = pygame.image.load(os.path.join(skin_folder, fname)).convert_alpha()
                img = pygame.transform.scale(img, (72, 72))
                skin_list.append({"name": fname, "img": img})
 
    COLS      = 3
    THUMB_W   = 72
    THUMB_H   = 72
    BTN_H     = 26
    SPACING_X = 150
    SPACING_Y = 130
    START_X   = 55
    START_Y   = 100
    back_btn  = pygame.Rect(10, 8, 88, 32)
 
    clock = pygame.time.Clock()
    # track whether the mouse button was freshly pressed this frame
    just_clicked = False
 
    running = True
    while running:
        clock.tick(FPS)
        just_clicked = False
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                just_clicked = True
                if back_btn.collidepoint(event.pos):
                    running = False
 
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((22, 22, 30))
 
        # header
        ws = big_font.render(f"WINS: {wins}", True, (255, 215, 0))
        screen.blit(ws, (WINDOW_W // 2 - ws.get_width() // 2, 10))
 
        # back
        pygame.draw.rect(screen, (140, 40, 40), back_btn, border_radius=6)
        screen.blit(font.render("Back", True, (255, 255, 255)), (back_btn.x + 8, back_btn.y + 7))
 
        for idx, skin in enumerate(skin_list):
            row_num = idx // COLS
            col_num = idx % COLS
            sx = START_X + col_num * SPACING_X
            sy = START_Y + row_num * SPACING_Y
 
            is_default  = skin["name"] == "0_Default.png"
            is_owned    = skin["name"] in owned_skins or is_default
            is_equipped = skin["name"] == equipped_skin
 
            # card
            card = pygame.Rect(sx - 8, sy - 8, THUMB_W + 16, THUMB_H + BTN_H + 24)
            pygame.draw.rect(screen, (50, 80, 50) if is_equipped else (38, 38, 55), card, border_radius=8)
            screen.blit(skin["img"], (sx, sy))
 
            btn = pygame.Rect(sx, sy + THUMB_H + 6, THUMB_W, BTN_H)
 
            if is_equipped:
                btn_col = (50, 190, 70);  label = "Equipped"
            elif is_owned:
                btn_col = (70, 100, 220); label = "Equip"
            elif wins >= SKIN_COST:
                btn_col = (200, 150, 40); label = f"Buy {SKIN_COST}W"
            else:
                btn_col = (65, 65, 65);   label = f"Need {SKIN_COST}W"
 
            pygame.draw.rect(screen, btn_col, btn, border_radius=5)
            ls = font.render(label, True, (255, 255, 255))
            screen.blit(ls, ls.get_rect(center=btn.center))
 
            # only act on a fresh click this frame
            if just_clicked and btn.collidepoint(mouse_pos):
                if is_owned and not is_equipped:
                    equipped_skin = skin["name"]
                    save_skin_state()
                elif not is_owned and wins >= SKIN_COST:
                    wins -= SKIN_COST
                    owned_skins.append(skin["name"])
                    equipped_skin = skin["name"]
                    save_wins()
                    save_skin_state()
 
        pygame.display.flip()
 
    mainmenu()
 
# ── Main game ────────────────────────────────────────────────────────────────
def main():
    global wins, equipped_skin
 
    cols, rows = MAZE_COLS, MAZE_ROWS
    clock      = pygame.time.Clock()
    font       = pygame.font.SysFont(None, 26)
    small_font = pygame.font.Font(None, 22)
    radius     = CELL_SIZE // 3
    all_imgs   = load_all_skin_images()
 
    def get_player_surf():
        return make_player_surf(equipped_skin, all_imgs, radius)
 
    def new_game():
        grid      = generate_maze(cols, rows)
        player    = [0, 0]
        goal      = [cols - 1, rows - 1]
        start_t   = time.time()
        # smooth draw positions start at cell centre
        spx = float(0 * CELL_SIZE + CELL_SIZE // 2)
        spy = float(0 * CELL_SIZE + CELL_SIZE // 2)
        csx = float(max(0, spx - WINDOW_W // 2))
        csy = float(max(0, spy - VIEW_H   // 2))
        return grid, player, goal, start_t, False, 0, False, False, spx, spy, csx, csy
 
    (grid, player, goal, start_t,
     won, steps, played_200, played_300,
     smooth_px, smooth_py, cam_sx, cam_sy) = new_game()
 
    canwin   = True
    win_time = 0.0
    player_surf = get_player_surf()
 
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
 
        # sound triggers
        if steps >= 300 and not played_300:
            sound_300.play(); played_300 = True
        elif steps >= 200 and not played_200:
            sound_200.play(); played_200 = True
 
        # player colour
        if steps >= 300:
            player_color = (255, 0, 0)
        elif steps >= 200:
            player_color = (255, 126, 0)
        else:
            player_color = (0, 150, 30)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    (grid, player, goal, start_t,
                     won, steps, played_200, played_300,
                     smooth_px, smooth_py, cam_sx, cam_sy) = new_game()
                    canwin = True
                    win_time = 0.0
                    player_surf = get_player_surf()
                    continue
 
                if event.key == pygame.K_c:
                    running = False
                    mainmenu()
                    return
 
                if not won:
                    col_p, row_p = player
                    cur   = grid[grid_index(col_p, row_p, cols, rows)]
                    moved = False
 
                    if event.key in (pygame.K_UP, pygame.K_w):
                        if not cur.walls[0] and row_p > 0:
                            player[1] -= 1; moved = True
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if not cur.walls[2] and row_p < rows - 1:
                            player[1] += 1; moved = True
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if not cur.walls[3] and col_p > 0:
                            player[0] -= 1; moved = True
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if not cur.walls[1] and col_p < cols - 1:
                            player[0] += 1; moved = True
 
                    if moved:
                        steps += 1
                        if player == goal:
                            won = True
                            win_time = time.time() - start_t
                            if canwin:
                                wins   += 1
                                canwin  = False
                                save_wins()
 
        # ── Smooth player (lerp toward logical cell centre) ───────────────
        target_px = float(player[0] * CELL_SIZE + CELL_SIZE // 2)
        target_py = float(player[1] * CELL_SIZE + CELL_SIZE // 2)
        tp = min(1.0, LERP_PLAYER * 60 * dt)
        smooth_px += (target_px - smooth_px) * tp
        smooth_py += (target_py - smooth_py) * tp
 
        # ── Smooth camera (lerp toward player) ────────────────────────────
        maze_pw = cols * CELL_SIZE
        maze_ph = rows * CELL_SIZE
        tcx = max(0, min(smooth_px - WINDOW_W // 2, maze_pw - WINDOW_W))
        tcy = max(0, min(smooth_py - VIEW_H   // 2, maze_ph - VIEW_H))
        tc  = min(1.0, LERP_CAM * 60 * dt)
        cam_sx += (tcx - cam_sx) * tc
        cam_sy += (tcy - cam_sy) * tc
 
        cam_ix = int(cam_sx)
        cam_iy = int(cam_sy)
 
        # ── Draw ─────────────────────────────────────────────────────────
        screen.fill((125, 115, 105))
        draw_maze(screen, grid, CELL_SIZE, cam_ix, cam_iy)
 
        # goal
        gsx = goal[0] * CELL_SIZE - cam_ix
        gsy = goal[1] * CELL_SIZE - cam_iy
        pygame.draw.rect(screen, GOAL_COLOR, (gsx + 4, gsy + 4, CELL_SIZE - 8, CELL_SIZE - 8))
 
        # player
        draw_px = int(smooth_px) - cam_ix
        draw_py = int(smooth_py) - cam_iy
        pygame.draw.circle(screen, player_color, (draw_px, draw_py), radius)
 
        # skin texture mapped onto circle
        if player_surf:
            screen.blit(player_surf, (draw_px - radius, draw_py - radius))
 
        # HUD
        elapsed = time.time() - start_t
        pygame.draw.rect(screen, (255, 255, 255), (0, VIEW_H, WINDOW_W, HUD_H))
        hud = font.render(
            f"Steps:{steps}  Time:{int(elapsed)}s  Wins:{wins}  R=new  C=menu",
            True, (10, 10, 10))
        screen.blit(hud, (8, VIEW_H + 9))
 
        # win overlay
        if won:
            msg      = f"Won in {steps} steps & {int(win_time)}s!  R=new  C=menu"
            win_surf = small_font.render(msg, True, (0, 0, 0))
            wrect    = win_surf.get_rect(center=(WINDOW_W // 2, VIEW_H // 2))
            overlay  = pygame.Surface((wrect.width + 20, wrect.height + 20))
            overlay.fill((240, 240, 180))
            screen.blit(overlay, (wrect.x - 10, wrect.y - 10))
            screen.blit(win_surf, wrect)
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
# ── Main menu ────────────────────────────────────────────────────────────────
def mainmenu():
    font     = pygame.font.Font(None, 44)
    sub_font = pygame.font.Font(None, 28)
    bg_col   = (22, 22, 30)
    btn_col  = (55, 55, 78)
    btn_hov  = (85, 85, 118)
 
    btn_play  = pygame.Rect(125, 115, 250, 78)
    btn_skins = pygame.Rect(125, 222, 250, 78)
    btn_quit  = pygame.Rect(125, 329, 250, 78)
 
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(FPS)
        mouse       = pygame.mouse.get_pos()
        hover_play  = btn_play.collidepoint(mouse)
        hover_skins = btn_skins.collidepoint(mouse)
        hover_quit  = btn_quit.collidepoint(mouse)
 
        screen.fill(bg_col)
 
        title = font.render("MAZE", True, (210, 210, 255))
        screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 52)))
        sub = sub_font.render(f"Wins: {wins}", True, (255, 215, 0))
        screen.blit(sub, sub.get_rect(center=(WINDOW_W // 2, 84)))
 
        for btn, hov, label in [
            (btn_play,  hover_play,  "Play"),
            (btn_skins, hover_skins, "Skins"),
            (btn_quit,  hover_quit,  "Quit"),
        ]:
            pygame.draw.rect(screen, btn_hov if hov else btn_col, btn, border_radius=10)
            txt = font.render(label, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=btn.center))
 
        pygame.display.flip()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hover_play:
                    main(); return
                if hover_skins:
                    skinmenu(); return
                if hover_quit:
                    pygame.quit(); sys.exit()
 
mainmenu()
