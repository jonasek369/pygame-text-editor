import json

import pygame

pygame.init()
pygame.font.init()

settings = None
default_settings = {
    "font": "Arial",
    "font-size": 24,
    "font-antialias": True,
    "window-resizable": True,
    "window-resolution": [1280, 720],
    "window-refreshrate": 240,
    "color-background": [24, 24, 24],
    "color-text": [255, 255, 255]
}

# load aliases for easier and more readable use
vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3

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


BACKGROUND = get_setting("color-background")
FPS = get_setting("window-refreshrate")


class TextWindow:
    def __init__(self, screen):
        fontsize = get_setting("font-size")
        self.textresolutin = vec2(screen.get_width() / fontsize, screen.get_height() / fontsize)


# problem of pygame vector is that their floats so they cant be used as indexes into buffer so using this
class vec2i:
    def __init__(self, x0=0, y0=0):
        self.x: int = x0
        self.y: int = y0


class Cursor:
    def __init__(self):
        self.pos = vec2i(0, 0)
        self.scroll = vec2i(0, 0)


class Buffer:
    def __init__(self):
        self.data = ["import math", "def main():", "    return math.sqrt(1)"]


class Editor:
    def __init__(self):
        self.text_renderer = pygame.font.SysFont(get_setting("font"), get_setting("font-size"))
        self.clock = pygame.time.Clock()

        if get_setting("window-resizable"):
            self.screen = pygame.display.set_mode(get_setting("window-resolution"), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.set_mode(get_setting("window-resolution"))

        self.running = True

        self.window = TextWindow(self.screen)
        self.buffer = Buffer()
        self.cursor = Cursor()

    def start(self):
        self.loop()

    def draw_buffer(self):
        size = get_setting("font-size")
        # draw cursor
        text = self.buffer.data[self.cursor.pos.y][:self.cursor.pos.x]
        pre_render = self.text_renderer.render(text, get_setting("font-antialias"), get_setting("color-text"))
        pygame.draw.line(self.screen, get_setting("color-text"),
                         [pre_render.get_width(), self.cursor.pos.y * size],
                         [pre_render.get_width(), (self.cursor.pos.y * size) + pre_render.get_height()]
                         )
        self.cursor.pos.x = len(text)

        # draw buffer
        for pos, line in enumerate(self.buffer.data):
            render = self.text_renderer.render(line, get_setting("font-antialias"), get_setting("color-text"))
            self.screen.blit(render, (0, pos * size))

    def handle_texinput_event(self, event: pygame.event.Event):
        pass

    def handle_key_event(self, event: pygame.event.Event):
        if event.key == pygame.K_UP:
            if not self.cursor.pos.y <= 0:
                self.cursor.pos.y -= 1
        if event.key == pygame.K_DOWN:
            self.cursor.pos.y += 1

        # add newline to the buffer
        for i in range(self.cursor.pos.y - len(self.buffer.data)+1):
            self.buffer.data.append("")

        if event.key == pygame.K_LEFT:
            if not self.cursor.pos.x <= 0:
                self.cursor.pos.x -= 1
        if event.key == pygame.K_RIGHT:
            if len(self.buffer.data[self.cursor.pos.y]) >= self.cursor.pos.x + 1:
                self.cursor.pos.x += 1

    def loop(self):
        while self.running:
            self.screen.fill(BACKGROUND)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.TEXTINPUT:
                    self.handle_texinput_event(event)
                if event.type == pygame.KEYDOWN:
                    self.handle_key_event(event)
            self.draw_buffer()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    e = Editor()
    e.start()
