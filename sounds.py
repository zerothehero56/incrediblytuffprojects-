# sounds.py
import os
import pygame

pygame.mixer.init()
pygame.mixer.set_num_channels(64)

base = os.path.dirname(__file__)
sound_fah      = pygame.mixer.Sound(os.path.join(base, "sounds", "fah.wav"))
sound_idk      = pygame.mixer.Sound(os.path.join(base, "sounds", "IDK.mp3"))
sound_sunshine = pygame.mixer.Sound(os.path.join(base, "sounds", "LebronShine.wav"))
sound_win      = pygame.mixer.Sound(os.path.join(base, "sounds", "win.wav"))
sound_cmonman  = pygame.mixer.Sound(os.path.join(base, "sounds", "thastooeas.wav"))
sound_flight   = pygame.mixer.Sound(os.path.join(base, "sounds", "LEBRONN.wav"))
sound_rizz     = pygame.mixer.Sound(os.path.join(base, "sounds", "rizz.mp3"))

channel  = pygame.mixer.Channel(1)
canel    = pygame.mixer.Channel(4)
chanel   = pygame.mixer.Channel(2)
cannel   = pygame.mixer.Channel(3)

sound_fah.set_volume(0.15)
sound_idk.set_volume(0.15)
sound_flight.set_volume(0.1)
