# skins.py
import os
import sys
import pygame
import saves
from config import screen, WINDOW_W, WINDOW_H, FPS, SKIN_COST

def load_all_skin_images():
    imgs   = {}
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
    mask   = pygame.Surface((diam, diam), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    scaled.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return scaled

def skinmenu():
    import main as m
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
    back_btn  = pygame.Rect(10, 8, 112, 32)
    SCROLL_SPEED = 30
    scroll_y  = 0
    total_rows = (len(skin_list) + COLS - 1) // COLS
    max_scroll = max(0, total_rows * SPACING_Y - (WINDOW_H - START_Y))
    clock      = pygame.time.Clock()
    just_clicked = False
    running    = True

    while running:
        clock.tick(FPS)
        just_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - SCROLL_SPEED)
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(max_scroll, scroll_y + SCROLL_SPEED)
            if event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * SCROLL_SPEED
                scroll_y  = max(0, min(max_scroll, scroll_y))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                just_clicked = True
                if back_btn.collidepoint(event.pos):
                    running = False

        mouse_pos = pygame.mouse.get_pos()
        screen.fill((22, 22, 30))

        ws = big_font.render(f"WINS: {saves.wins}", True, (255, 215, 0))
        screen.blit(ws, (WINDOW_W // 2 - ws.get_width() // 2, 10))

        pygame.draw.rect(screen, (140, 40, 40), back_btn, border_radius=6)
        screen.blit(font.render("Back (Esc)", True, (255, 255, 255)),
                    (back_btn.x + 8, back_btn.y + 7))

        for idx, skin in enumerate(skin_list):
            row_num = idx // COLS
            col_num = idx  % COLS
            sx = START_X + col_num * SPACING_X
            sy = START_Y + row_num * SPACING_Y - scroll_y
            if sy + THUMB_H + BTN_H + 24 < 0 or sy > WINDOW_H:
                continue
            is_default  = skin["name"] == "0_Default.png"
            is_owned    = skin["name"] in saves.owned_skins or is_default
            is_equipped = skin["name"] == saves.equipped_skin

            card = pygame.Rect(sx - 8, sy - 8, THUMB_W + 16, THUMB_H + BTN_H + 24)
            pygame.draw.rect(screen, (50, 80, 50) if is_equipped else (38, 38, 55),
                             card, border_radius=8)
            screen.blit(skin["img"], (sx, sy))

            btn = pygame.Rect(sx, sy + THUMB_H + 6, THUMB_W, BTN_H)
            if is_equipped:
                btn_col, label = (50, 190, 70),  "Equipped"
            elif is_owned:
                btn_col, label = (70, 100, 220), "Equip"
            elif saves.wins >= SKIN_COST:
                btn_col, label = (200, 150, 40), f"Buy {SKIN_COST}W"
            else:
                btn_col, label = (65, 65, 65),   f"Need {SKIN_COST}W"

            pygame.draw.rect(screen, btn_col, btn, border_radius=5)
            ls = font.render(label, True, (255, 255, 255))
            screen.blit(ls, ls.get_rect(center=btn.center))

            if just_clicked and btn.collidepoint(mouse_pos):
                if is_owned and not is_equipped:
                    saves.equipped_skin = skin["name"]
                    saves.save_skin_state()
                elif not is_owned and saves.wins >= SKIN_COST:
                    saves.wins -= SKIN_COST
                    saves.owned_skins.append(skin["name"])
                    saves.equipped_skin = skin["name"]
                    saves.save_wins()
                    saves.save_skin_state()

        pygame.display.flip()

    m.mainmenu()
