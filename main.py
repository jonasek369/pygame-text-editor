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
    "color-text": [255, 255, 255],
    "color-commandline": [0, 0, 255]
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
        self.data = [""]


class Editor:
    def __init__(self):
        self.text_renderer = pygame.font.SysFont(get_setting("font"), get_setting("font-size"))
        self.clock = pygame.time.Clock()

        if get_setting("window-resizable"):
            self.screen = pygame.display.set_mode(get_setting("window-resolution"), pygame.RESIZABLE)
        else:
            self.screen = pygame.display.set_mode(get_setting("window-resolution"))

        self.running = True
        self.cmd_mode = False

        self.window = TextWindow(self.screen)
        self.buffer = Buffer()
        self.cmd_buffer = Buffer()
        self.cursor = Cursor()
        self.cmd_cursor = Cursor()

        self.operating_file_name = "untitled"

    def start(self):
        self.loop()

    def draw_buffer(self):
        size = get_setting("font-size")

        # draw vim like command line
        if self.cmd_mode:
            res = get_setting("window-resolution")
            pygame.draw.rect(self.screen, get_setting("color-commandline"),
                             pygame.Rect([0, res[1] - size], [res[0], size]))

            for pos, line in enumerate(self.cmd_buffer.data):
                render = self.text_renderer.render(line, get_setting("font-antialias"), get_setting("color-text"))
                self.screen.blit(render, (0, res[1] - size))

        # draw cursor
        current_buffer = self.cmd_buffer.data if self.cmd_mode else self.buffer.data
        current_cursor = self.cmd_cursor if self.cmd_mode else self.cursor
        start_pos = get_setting("window-resolution")[1] - size if self.cmd_mode else self.cursor.pos.y * size

        text = current_buffer[current_cursor.pos.y][:current_cursor.pos.x]
        pre_render = self.text_renderer.render(text, get_setting("font-antialias"), get_setting("color-text"))
        pygame.draw.line(self.screen, get_setting("color-text"),
                         [pre_render.get_width(), start_pos],
                         [pre_render.get_width(), start_pos + pre_render.get_height()], 2
                         )
        current_cursor.pos.x = len(text)

        # draw buffer
        for pos, line in enumerate(self.buffer.data):
            render = self.text_renderer.render(line, get_setting("font-antialias"), get_setting("color-text"))
            self.screen.blit(render, (0, pos * size))

    def handle_texinput_event(self, event: pygame.event.Event):
        current_buffer = self.cmd_buffer.data if self.cmd_mode else self.buffer.data
        current_cursor = self.cmd_cursor if self.cmd_mode else self.cursor

        current_buffer[current_cursor.pos.y] = current_buffer[current_cursor.pos.y][
                                               :current_cursor.pos.x] + event.text + \
                                               current_buffer[current_cursor.pos.y][current_cursor.pos.x:]
        current_cursor.pos.x += 1

    def parse_command(self):
        buf = self.cmd_buffer.data
        cmd = buf[0].lower().split(" ")
        if cmd[0] == ":w":
            with open(self.operating_file_name, "w") as file:
                text = "\n".join(self.buffer.data)
                file.write(text)
        if cmd[0] == ":chn":
            self.operating_file_name = "".join(cmd[1:])
        if cmd[0] == ":sav":
            name = "".join(cmd[1:])
            with open(name, "w") as file:
                text = "\n".join(self.buffer.data)
                file.write(text)
        if cmd[0] == ":q":
            exit(0)

    def handle_key_event(self, event: pygame.event.Event):
        current_buffer = self.cmd_buffer.data if self.cmd_mode else self.buffer.data
        current_cursor = self.cmd_cursor if self.cmd_mode else self.cursor

        if not self.cmd_mode:
            if event.key == pygame.K_UP:
                if not self.cursor.pos.y <= 0:
                    self.cursor.pos.y -= 1
            if event.key == pygame.K_DOWN:
                self.cursor.pos.y += 1

        for i in range(self.cursor.pos.y - len(self.buffer.data) + 1):
            self.buffer.data.append("")

        if event.key == pygame.K_LEFT:
            if not current_cursor.pos.x <= 0:
                current_cursor.pos.x -= 1
        if event.key == pygame.K_RIGHT:
            if len(current_buffer[current_cursor.pos.y]) >= current_cursor.pos.x + 1:
                current_cursor.pos.x += 1

        if event.key == pygame.K_BACKSPACE:
            if current_cursor.pos.x == 0 and current_cursor.pos.y != 0:
                removed = current_buffer.pop(current_cursor.pos.y)
                current_cursor.pos.y -= 1
                current_cursor.pos.x = len(current_buffer[current_cursor.pos.y])
                current_buffer[current_cursor.pos.y] += removed
            else:
                if not current_cursor.pos.x <= 0:
                    current_buffer[current_cursor.pos.y] = current_buffer[current_cursor.pos.y][
                                                           :current_cursor.pos.x - 1] + \
                                                           current_buffer[current_cursor.pos.y][current_cursor.pos.x:]
                    current_cursor.pos.x -= 1

        if event.key == pygame.K_ESCAPE:
            self.cmd_mode = not self.cmd_mode
            if not self.cmd_mode:
                self.cmd_buffer.data = [""]

        if event.key == pygame.K_RETURN:
            if self.cmd_mode:
                self.parse_command()
                self.cmd_mode = False
                self.cmd_buffer.data = [""]
            else:
                first, second = self.buffer.data[self.cursor.pos.y][:self.cursor.pos.x], self.buffer.data[
                                                                                             self.cursor.pos.y][
                                                                                         self.cursor.pos.x:]
                self.buffer.data.pop(self.cursor.pos.y)
                self.buffer.data.insert(self.cursor.pos.y, first)
                self.buffer.data.insert(self.cursor.pos.y + 1, second)
                self.cursor.pos.y += 1
                self.cursor.pos.x = len(self.buffer.data[self.cursor.pos.y]) - len(second)

    def loop(self):
        dt = 0
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
            pygame.display.set_caption(self.operating_file_name)
            dt = self.clock.tick(FPS)


if __name__ == '__main__':
    e = Editor()
    e.start()
