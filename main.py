import json

import pygame

pygame.init()
pygame.font.init()

settings = None
default_settings = {
    "font": "Arial",
    "font-size": 12,
    "window-resizable": True,
    "window-resolution": [1280, 720],
    "color-background": [24, 24, 24]
}

# loads users settings
try:
    with open("settings/editor.json", "r") as file:
        settings = json.loads(file.read())
except FileNotFoundError:
    raise FileNotFoundError("Could not load settings from 'settings/editor.json' make sure file exists")


# gets the users settings or default if not set by user
def get_setting(key_name):
    if settings.get(key_name):
        return settings.get(key_name)
    else:
        default_settings.get(key_name)


text_renderer = pygame.font.SysFont(get_setting("font"), get_setting("font-size"))

if get_setting("window-resizable"):
    screen = pygame.display.set_mode(get_setting("window-resolution"), pygame.RESIZABLE)
else:
    screen = pygame.display.set_mode(get_setting("window-resolution"))

running = True

BACKGROUND = get_setting("color-background")

while running:
    screen.fill(BACKGROUND)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()
