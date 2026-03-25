# saves.py
import os

base = os.path.dirname(__file__)
save_path      = os.path.join(base, "data.txt")
skin_save_path = os.path.join(base, "skins_save.txt")

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

try:
    with open(save_path, "r") as fh:
        wins = int(fh.read())
except FileNotFoundError:
    wins = 0

def save_wins():
    with open(save_path, "w") as fh:
        fh.write(str(wins))
