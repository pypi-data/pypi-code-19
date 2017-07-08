import json
import os.path
import pygame

from pyrogi import FONT_CONFIG_EXTENSION, FONT_PATH
from pyrogi.drawing import Graphics
from pyrogi.util import Vec2

GRAYSCALE_FONT_TYPE = 'grayscale'
ALPHA_FONT_TYPE = 'alpha'

class PyGameGraphics(Graphics):
    def __init__(self):
        self.font_cache = {}
        self.tile_cache = {}

    def init_window(self, window_dimensions, tile_dimensions, caption):
        self.screen = pygame.display.set_mode((window_dimensions*tile_dimensions).to_tuple())
        self.window_dimensions = window_dimensions
        self.tile_dimensions = tile_dimensions
        pygame.display.set_caption(caption)

    def clear_screen(self):
        self.screen.fill((0, 0, 0, 0))

    def draw_tile(self, position, character, fg_color, bg_color):
        key = ('brogue.png', character, fg_color, bg_color)
        if key not in self.tile_cache:
            font_image, font_config = self._load_font('brogue.png')
            tile_image = self._get_tile_image(font_image, font_config, font_config.get_index(character), fg_color, bg_color)
            tile_image = pygame.transform.smoothscale(tile_image, self.tile_dimensions.to_tuple())
            self.tile_cache[key] = tile_image

        self.screen.blit(self.tile_cache[key], (position*self.tile_dimensions).to_tuple())

    def _load_font(self, filename):
        if filename not in self.font_cache:
            font_image = pygame.image.load(os.path.join(FONT_PATH, filename)).convert_alpha()
            config_filename = os.path.splitext(filename)[0] + FONT_CONFIG_EXTENSION
            font_config = self._load_font_json(os.path.join(FONT_PATH, config_filename))
            if font_config.font_type == GRAYSCALE_FONT_TYPE:
                font_image = self._grayscale_to_alpha(font_image)
            self.font_cache[filename] = (font_image, font_config)

        return self.font_cache[filename]

    def _grayscale_to_alpha(self, image):
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                color = image.get_at((x, y))
                image.set_at((x, y), (255, 255, 255, color.r))
        return image

    def _load_font_json(self, filename):
        with open(filename) as f:
            data = json.load(f)
            font_config = FontConfig(
                Vec2(data['tileWidth'], data['tileHeight']),
                data['fontType'] if 'fontType' in data else GRAYSCALE_FONT_TYPE,
                data['characterMap']
            )
            return font_config

    def _get_tile_image(self, image, config, index, fg_color, bg_color):
        dim = config.tile_dimensions
        fg_image, bg_image = self._separate_into_fg_bg(image, dim, index, fg_color, bg_color)
        tile_image = pygame.Surface((dim.x, dim.y)).convert_alpha()
        tile_image.blit(bg_image, (0, 0))
        tile_image.blit(fg_image, (0, 0))

        return tile_image

    def _separate_into_fg_bg(self, image, dim, index, fg_color, bg_color):
        fg_image = pygame.Surface((dim.x, dim.y)).convert_alpha()
        fg_image.fill((255, 255, 255, 0))
        fg_image.blit(image, (0, 0), (index.x*dim.x, index.y*dim.y, (index.x+1)*dim.x, (index.y+1)*dim.y))
        fg_image.fill(fg_color.to_RGBA_tuple(), special_flags=pygame.BLEND_RGBA_MIN)

        bg_image = pygame.Surface((dim.x, dim.y)).convert()
        bg_image.fill(bg_color.to_RGB_tuple())
        bg_image.set_alpha(bg_color.a)

        return fg_image, bg_image

class FontConfig(object):
    def __init__(self, tile_dimensions, font_type, character_map):
        self.tile_dimensions = tile_dimensions
        self.font_type = font_type
        self.character_map = character_map

    def get_index(self, character):
        index = self.character_map[character]
        return Vec2(index[0], index[1])
