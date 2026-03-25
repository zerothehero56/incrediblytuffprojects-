# main.py
import random
import sys
import time
import pygame

import config
import saves
import sounds
import skins
from config import (screen, WINDOW_W, WINDOW_H, HUD_H, VIEW_H,
                    FPS, LERP_CAM, LERP_PLAYER, GOAL_COLOR)
from maze import generate_maze, draw_maze, grid_index

# ── Difficulty / slider ────────────────────────────────────────────────────────
def slider():
    global winz
    import config as cfg
    font     = pygame.font.Font(None, 44)
    sub_font = pygame.font.Font(None, 28)
    bg_col   = (50, 30, 30)
    clock    = pygame.time.Clock()
    pygame.mixer.stop()

    MIN_SIZE = 10
    MAX_SIZE = 100
    current  = min(cfg.MAZE_COLS, MAX_SIZE)
    slider_x = 100
    slider_y = 280
    slider_w = 300
    slider_h = 8
    handle_r = 12
    confirm_btn = pygame.Rect(175, 360, 150, 50)

    def size_to_x(val):
        t = (val - MIN_SIZE) / (MAX_SIZE - MIN_SIZE)
        return int(slider_x + t * slider_w)

    def x_to_size(x):
        t = (x - slider_x) / slider_w
        return round(MIN_SIZE + t * (MAX_SIZE - MIN_SIZE))

    dragging = True
    running  = True
    while running:
        clock.tick(FPS)
        mouse    = pygame.mouse.get_pos()
        handle_x = size_to_x(current)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainmenu(); return
                if event.key == pygame.K_LEFT:
                    current = max(MIN_SIZE, current - 1)
                if event.key == pygame.K_RIGHT:
                    current = min(MAX_SIZE, current + 1)
                if event.key == pygame.K_RETURN:
                    cfg.MAZE_COLS = current
                    cfg.MAZE_ROWS = current
                    main(); return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if abs(mouse[0] - handle_x) <= handle_r + 4 and abs(mouse[1] - slider_y) <= handle_r + 4:
                    dragging = True
                if confirm_btn.collidepoint(mouse):
                    cfg.MAZE_COLS = current
                    cfg.MAZE_ROWS = current
                    main(); return
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                current = x_to_size(max(slider_x, min(slider_x + slider_w, mouse[0])))

        screen.fill(bg_col)

        title = font.render("DIFFICULTY", True, (210, 210, 255))
        screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 80)))

        if current <= 20:
            diff_label = "Easy";      diff_col = (80, 200, 80);   winz = 1
        elif current <= 40:
            diff_label = "Medium";    diff_col = (255, 200, 40);  winz = 1
        elif current <= 60:
            diff_label = "Hard";      diff_col = (255, 120, 40);  winz = 1
        elif current <= 80:
            diff_label = "Insane";    diff_col = (220, 40, 40);   winz = 1
        elif current < 100:
            diff_label = "Crazy";     diff_col = (0, 0, 0);       winz = 1
        else:           
            diff_label = "Mentally Unstable"; diff_col = (255, 255, 255); winz = 1

        label = font.render(f"{diff_label} ({current}x{current})", True, diff_col)
        screen.blit(label, label.get_rect(center=(WINDOW_W // 2, 200)))

        pygame.draw.rect(screen, (60, 60, 80),
                         (slider_x, slider_y - slider_h // 2, slider_w, slider_h), border_radius=4)
        pygame.draw.rect(screen, diff_col,
                         (slider_x, slider_y - slider_h // 2, handle_x - slider_x, slider_h), border_radius=4)
        pygame.draw.circle(screen, (210, 210, 255), (handle_x, slider_y), handle_r)
        pygame.draw.circle(screen, diff_col,        (handle_x, slider_y), handle_r - 3)

        cfg.vis = max(1, current + 2)

        hover = confirm_btn.collidepoint(mouse)
        pygame.draw.rect(screen, (85, 85, 118) if hover else (55, 55, 78),
                         confirm_btn, border_radius=10)
        btn_txt = sub_font.render("Play!", True, (255, 255, 255))
        screen.blit(btn_txt, btn_txt.get_rect(center=confirm_btn.center))

        hint = sub_font.render("<- -> to adjust | Enter to confirm", True, (120, 120, 150))
        screen.blit(hint, hint.get_rect(center=(WINDOW_W // 2, 440)))

        pygame.display.flip()

# ── Main game ──────────────────────────────────────────────────────────────────
def main():
    import config as cfg
    global winz
    sunshine = True
    cols, rows = cfg.MAZE_COLS, cfg.MAZE_ROWS
    clock      = pygame.time.Clock()
    font       = pygame.font.SysFont(None, 23)
    small_font = pygame.font.Font(None, 22)
    radius     = cfg.CELL_SIZE // 3
    all_imgs   = skins.load_all_skin_images()

    def get_player_surf():
        return skins.make_player_surf(saves.equipped_skin, all_imgs, radius)

    def new_game():
        grid   = generate_maze(cols, rows)
        player = [0, 0]
        goal   = [cols - 1, rows - 1]
        start_t = time.time()
        spx = float(0 * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
        spy = float(0 * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
        csx = float(max(0, spx - WINDOW_W // 2))
        csy = float(max(0, spy - VIEW_H  // 2))
        return grid, player, goal, start_t, False, 0, False, False, spx, spy, csx, csy

    sunshine = True
    (grid, player, goal, start_t, won, steps,
     played_200, played_300, smooth_px, smooth_py, cam_sx, cam_sy) = new_game()

    canwin   = True
    winplay  = True
    win_time = 0.0
    player_surf = get_player_surf()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        if saves.equipped_skin == "lebron.png":
            if sunshine == True:
                sounds.chanel.play(sounds.sound_sunshine, loops=-1)
                sunshine = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    (grid, player, goal, start_t, won, steps,
                     played_200, played_300, smooth_px, smooth_py,
                     cam_sx, cam_sy) = new_game()
                    canwin   = True
                    sunshine = True
                    win_time = 0.0
                    player_surf = get_player_surf()
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                    mainmenu()
                    return
                if event.key == pygame.K_q:
                    running = False
                    slider()
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
                        if saves.equipped_skin == "Hillo.png" and steps != 200 and steps != 300:
                            sounds.sound_fah.play()
                        if saves.equipped_skin == "imattheclub.png" and steps != 200 and steps != 300:
                            sounds.sound_idk.play()
                        if saves.equipped_skin == "lebron.png":
                            sounds.sound_flight.play()
                        if saves.equipped_skin == "dingle.png":
                            sounds.sound_rizz.play()
                    if player == goal:
                        won      = True
                        win_time = time.time() - start_t
                        if canwin:
                            saves.wins += 1
                            canwin = False
                            saves.save_wins()

        target_px = float(player[0] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
        target_py = float(player[1] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
        tp         = min(1.0, LERP_PLAYER * 60 * dt)
        smooth_px += (target_px - smooth_px) * tp
        smooth_py += (target_py - smooth_py) * tp

        maze_pw = cols * cfg.CELL_SIZE
        maze_ph = rows * cfg.CELL_SIZE
        tcx     = max(0, min(smooth_px - WINDOW_W // 2, maze_pw - WINDOW_W))
        tcy     = max(0, min(smooth_py - VIEW_H  // 2,  maze_ph - VIEW_H))
        tc      = min(1.0, LERP_CAM * 60 * dt)
        cam_sx += (tcx - cam_sx) * tc
        cam_sy += (tcy - cam_sy) * tc
        cam_ix  = int(cam_sx)
        cam_iy  = int(cam_sy)

        screen.fill((125, 115, 105))
        draw_maze(screen, grid, cfg.CELL_SIZE, cam_ix, cam_iy)

        gsx = goal[0] * cfg.CELL_SIZE - cam_ix
        gsy = goal[1] * cfg.CELL_SIZE - cam_iy
        pygame.draw.rect(screen, GOAL_COLOR,
                         (gsx + 4, gsy + 4, cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8))

        draw_px = int(smooth_px) - cam_ix
        draw_py = int(smooth_py) - cam_iy
        pygame.draw.circle(screen, (255, 255, 0), (draw_px, draw_py), radius)
        if player_surf:
            screen.blit(player_surf, (draw_px - radius, draw_py - radius))

        elapsed = time.time() - start_t
        pygame.draw.rect(screen, (255, 255, 255), (0, VIEW_H, WINDOW_W, HUD_H))
        hud = font.render(
            f"Time:{int(elapsed)}s",
            True, (10, 10, 10))
        screen.blit(hud, (8, VIEW_H + 9))

        if won:
            if winplay == True:
                if saves.equipped_skin == "lebron.png":
                    sounds.canel.play(sounds.sound_cmonman)
                else:
                    sounds.sound_win.play()
                winplay = False

            # dark semi-transparent full overlay
            overlay = pygame.Surface((WINDOW_W, VIEW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            # card
            card_w, card_h = 420, 220
            card_x = (WINDOW_W - card_w) // 2
            card_y = (VIEW_H  - card_h) // 2
            card   = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card.fill((30, 30, 50, 230))
            screen.blit(card, (card_x, card_y))
            pygame.draw.rect(screen, (120, 120, 200),
                             (card_x, card_y, card_w, card_h), 2, border_radius=12)

            title_font = pygame.font.Font(None, 56)
            stat_font  = pygame.font.Font(None, 30)
            btn_font   = pygame.font.Font(None, 26)
            key_font   = pygame.font.Font(None, 20)

            # YOU WIN
            t = title_font.render("YOU WIN!", True, (255, 215, 0))
            screen.blit(t, t.get_rect(center=(WINDOW_W // 2, card_y + 44)))

            # stats
            s1 = stat_font.render(f"Steps: {steps}", True, (200, 200, 255))
            s2 = stat_font.render(f"Time:  {int(win_time)}s", True, (200, 200, 255))
            screen.blit(s1, s1.get_rect(center=(WINDOW_W // 2, card_y + 90)))
            screen.blit(s2, s2.get_rect(center=(WINDOW_W // 2, card_y + 118)))

            # buttons — label on top, small hotkey below
            mouse = pygame.mouse.get_pos()
            btn_w, btn_h = 118, 44
            gap          = 10
            total_w      = 3 * btn_w + 2 * gap
            bx           = (WINDOW_W - total_w) // 2
            by           = card_y + 152

            win_btn_labels = [("Regenerate", "R"),
                              ("Menu",       "Esc"),
                              ("Resize",     "Q")]
            win_btn_rects  = []
            for i, (label, hotkey) in enumerate(win_btn_labels):
                r = pygame.Rect(bx + i * (btn_w + gap), by, btn_w, btn_h)
                win_btn_rects.append(r)
                hov = r.collidepoint(mouse)
                pygame.draw.rect(screen, (85, 85, 118) if hov else (55, 55, 78), r, border_radius=8)
                pygame.draw.rect(screen, (120, 120, 200), r, 1, border_radius=8)
                lt = btn_font.render(label, True, (255, 255, 255))
                kt = key_font.render(hotkey, True, (150, 150, 200))
                screen.blit(lt, lt.get_rect(center=(r.centerx, r.y + 16)))
                screen.blit(kt, kt.get_rect(center=(r.centerx, r.y + 32)))

            # handle clicks on win screen buttons
            for event_w in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                if event_w.button == 1:
                    if win_btn_rects[0].collidepoint(event_w.pos):
                        (grid, player, goal, start_t, won, steps,
                         played_200, played_300, smooth_px, smooth_py,
                         cam_sx, cam_sy) = new_game()
                        canwin = True; sunshine = True; win_time = 0.0; winplay = True
                        player_surf = get_player_surf()
                    elif win_btn_rects[1].collidepoint(event_w.pos):
                        pygame.mixer.stop(); mainmenu(); return
                    elif win_btn_rects[2].collidepoint(event_w.pos):
                        pygame.mixer.stop(); slider(); return

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ── Main menu ──────────────────────────────────────────────────────────────────
def mainmenu():
    btn_font    = pygame.font.Font(None, 44)
    sub_font    = pygame.font.Font(None, 28)
    key_font    = pygame.font.Font(None, 22)
    bg_col      = (22, 22, 30)
    btn_col     = (55, 55, 78)
    btn_sec     = (23, 23, 31)
    btn_sec_hov = (23, 23, 31)
    btn_hov     = (85, 85, 118)

    btn_play    = pygame.Rect(125, 115, 250, 78)
    btn_skins   = pygame.Rect(125, 222, 250, 78)
    btn_quit    = pygame.Rect(125, 329, 250, 78)
    btn_seceret = pygame.Rect(0, 0, 50, 50)

    clock   = pygame.time.Clock()
    running = True
    pygame.mixer.stop()

    while running:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        hover_play    = btn_play.collidepoint(mouse)
        hover_skins   = btn_skins.collidepoint(mouse)
        hover_quit    = btn_quit.collidepoint(mouse)
        hover_seceret = btn_seceret.collidepoint(mouse)

        screen.fill(bg_col)
        title_font = pygame.font.Font(None, 44)
        title = title_font.render("MAZE GAME", True, (210, 210, 255))
        screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 52)))

        sub = sub_font.render(f"Wins: {saves.wins}", True, (255, 215, 0))
        screen.blit(sub, sub.get_rect(center=(WINDOW_W // 2, 84)))

        for btn, hov, label, hotkey, col, hov_col in [
            (btn_play,    hover_play,    "Play",  "E",   btn_col, btn_hov),
            (btn_skins,   hover_skins,   "Skins", "S",   btn_col, btn_hov),
            (btn_quit,    hover_quit,    "Quit",  "Esc", btn_col, btn_hov),
            (btn_seceret, hover_seceret, "",      "",    btn_sec, btn_sec_hov),
        ]:
            pygame.draw.rect(screen, hov_col if hov else col, btn, border_radius=10)
            if label:
                lt = btn_font.render(label, True, (255, 255, 255))
                kt = key_font.render(hotkey, True, (150, 150, 200))
                screen.blit(lt, lt.get_rect(center=(btn.centerx, btn.centery - 10)))
                screen.blit(kt, kt.get_rect(center=(btn.centerx, btn.centery + 18)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hover_play:   slider(); return
                if hover_skins:  skins.skinmenu(); return
                if hover_quit:   pygame.quit(); sys.exit()
                if hover_seceret: sounds.sound_flight.play()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:       slider()
                if event.key == pygame.K_ESCAPE:  pygame.quit(); running = False; sys.exit()
                if event.key == pygame.K_s:       skins.skinmenu()

winz = 0
mainmenu()
