import itertools
from colorsys import hls_to_rgb, rgb_to_hls
from random import randint, choice

import pygame
from pygame.locals import *

from colorgame import cfg


def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.
		
		
class WinMessage:

    continue_button = K_SPACE
    exit = K_ESCAPE
    

    def __init__(self):
        """This function gets called once, just to create the text (but not display it)."""
        pygame.font.init() 
        self.myfont = pygame.font.SysFont('TimesNewRoman', 30)

    def draw(self, screen):
        """This is the function that gets called to actually display on the screen."""
        #textsurface = self.myfont.render('Congratulations! You found each other!', False, (0, 0, 0))
        text="Congratulations! You found each other! \n \nTo play again press the Space Button \n \nIf you want to exit the game, Press ESC"
        screen.fill((75,166,193))
        blit_text(screen, text, (99,250), self.myfont)
      
        return
	


class StartGame:

    #continue_button = K_SPACE
    easy_mode=K_1
    normal_mode=K_2
    hard_mode=K_3
	
    

    def __init__(self):
        """This function gets called once, just to create the text (but not display it)."""
        pygame.font.init()
        self.myfont = pygame.font.SysFont('TimesNewRoman', 25)

    def draw(self, screen):
        """This is the function that gets called to actually display on the screen."""
        text = "Welcome to the Game! \n \nTo start the game please press the following buttons \n \n-To play an Easy Mode Press 1 \n \n-To Play a Normal Mode Press 2 \n \n-To Play a Hard Mode Press 3"
        #textsurface = self.myfont.render("This is Start Screen \nPress the Space Button to start", False, (0, 0, 0))
        screen.fill((75,166,193))
        blit_text(screen, text, (99,250), self.myfont)
        return


class GameText:
    continue_button = K_SPACE
    def __init__(self):
        """This function gets called once, just to create the text (but not display it)."""
        pygame.font.init()
        self.myfont = pygame.font.SysFont('TimesNewRoman', 25)

    def draw(self, screen):
        """This is the function that gets called to actually display on the screen."""
        text = "How to Play the Game!? \n \n-To move up - Press the Up or W Button \n \n-To move down - Press the Down  or S Button \n \n-To move left - Press the Left or A Button \n \n-To move right - Press the Right or D Button \n \nReady to Start? \nLet's Go! Press the Space Button!"
        screen.fill((75,166,193))
        blit_text(screen, text, (30,30), self.myfont)
        
        return


class Tile:

    def __init__(self, x, y, px, py, r, g, b):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * px, y * py, px, py)
        self.color = color.Color(r, g, b, 50)

    def draw(self, screen):
        r, g, b = self.color.r, self.color.g, self.color.b
        pygame.draw.rect(screen, (r, g, b), self.rect)

    def randomize_color(self):
        self.color.r = randint(0, 255)
        self.color.g = randint(0, 255)
        self.color.b = randint(0, 255)

    def randomize_color_from_theme(self, theme):
        r, g, b = choice(theme)  # choose a color from the theme
        self.color.r, self.color.g, self.color.b = r, g, b

    @classmethod
    def from_theme(cls, x, y, px, py, theme):
        r, g, b = choice(theme)  # choose a color from the theme
        return cls(x, y, px, py, r, g, b)


class Player:

    def __init__(self, name, x=None, y=None):
        self.name = name
        if type(x) == None and type(y) == None:
            self.randomize_position()
        else:
            self.x = x
            self.y = y

    @property
    def xy(self):
        return self.x, self.y

    def randomize_position(self):
        self.x = randint(0, cfg.board_size)
        self.y = randint(0, cfg.board_size)



class Game:

    def __init__(self, width, height, theme):
        self.theme = theme

        self.screen = pygame.display.set_mode(cfg.screen_resolution)
        self.screen.fill((100, 0, 0))

        self.clock = pygame.time.Clock()

        self.width = width
        self.height = height
        self.board = self.generate_board()
        self.players = [Player(name='Player 1', x=randint(0, cfg.board_size), y=randint(0, cfg.board_size)),
                        Player(name='Player 2', x=randint(0, cfg.board_size), y=randint(0, cfg.board_size)), ]
        self.ai_players = [Player('', x=randint(0, cfg.board_size), y=randint(0, cfg.board_size)) for _ in range(
            cfg.ai_players)]


    def move_player(self, player, dx, dy, dt):

        def cycle(val, min, max):
            if val < min:
                return max - (val - min) - 2
            elif val >= max:
                return min + (val - max) + 0
            else:
                return val

        print(player.x + dx, player.y + dy, flush=False)
        x = cycle(player.x + dx, min=0, max=self.width)
        y = cycle(player.y + dy, min=0, max=self.height)
        print(x, y)

        player.x, player.y = x, y
        new_tile = self.board[y][x]
        old_hue = rgb_to_hls(new_tile.color.r, new_tile.color.g, new_tile.color.b)[0]

        while old_hue == rgb_to_hls(new_tile.color.r, new_tile.color.g, new_tile.color.b)[0]:
            new_tile.randomize_color_from_theme(self.theme)


    def check_for_win(self):
        for p1, p2 in itertools.combinations(self.players, 2):
            if p1.xy == p2.xy:
                return True
        else:
            return False


    def draw(self):
        for tile in itertools.chain(*self.board):
            for player in self.players:
                if player.x == tile.x and player.y == tile.y:
                    # if max(tile.color.r, tile.color.g, tile.color.b) < 255 - cfg.brighten_rate:

                    h, l, s = rgb_to_hls(tile.color.r, tile.color.g, tile.color.b)
                    if l > cfg.min_lightness:
                        l += cfg.brighten_rate
                        r, g, b = hls_to_rgb(h, l, s)
                        tile.color.r = int(r)
                        tile.color.g = int(g)
                        tile.color.b = int(b)
            tile.draw(self.screen)

        pygame.display.flip()

    def generate_board(self):
        px = self.screen.get_width() // self.width
        py = self.screen.get_height() // self.height
        return [[Tile.from_theme(x, y, px, py, self.theme) for x in range(self.width)] for y in range(self.height)]

    def handle_keys(self, dt, event):
        movement_inputs = {
            K_UP: (self.players[0], 0, -1),
            K_DOWN: (self.players[0], 0, 1),
            K_LEFT: (self.players[0], -1, 0),
            K_RIGHT: (self.players[0], 1, 0),
            K_w: (self.players[1], 0, -1),
            K_s: (self.players[1], 0, 1),
            K_a: (self.players[1], -1, 0),
            K_d: (self.players[1], 1, 0),
        }

        if event.key == K_ESCAPE:
            pygame.quit()
        else:
            try:
                player, x, y, = movement_inputs[event.key]
                self.move_player(player, x, y, dt)
            except KeyError:
                pass


    def show_start_screen(self):
        start_msg = StartGame()
        while True:
            start_msg.draw(self.screen)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == KEYUP:
                    #if event.key == start_msg.continue_button:
                       # return
					#Anna
                    if event.key ==start_msg.easy_mode:
                        cfg.ai_players = 3
                        cfg.ai_move_probability = 1
                        return
                    if event.key ==start_msg.normal_mode:
                        cfg.ai_players = 7
                        cfg.ai_move_probability = 5
                        return
                    if event.key ==start_msg.hard_mode:
                        cfg.ai_players = 15
                        cfg.ai_move_probability = 10
                        return
					#Anna
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
						
    def show_game_text(self):
        game_text=GameText()
        while True:
            game_text.draw(self.screen)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==KEYUP:
                    if event.key ==game_text.continue_button:
                        return
					
					
                    if event.key==K_ESCAPE:
                       pygame.quit()
                       sys.exit()
						 
	    

    def show_win_screen(self):
        win_msg = WinMessage()
        while True:
            win_msg.draw(self.screen)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == KEYUP:
                    if event.key == win_msg.continue_button:
                        return
					
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def show_game(self):
        # GamePlay
        while True:
            dt = self.clock.tick(60)

            for ai in self.ai_players:
                if randint(0, 100) < cfg.ai_move_probability:
                    self.move_player(ai, randint(-1, 1), randint(-1, 1), dt)

            for event in pygame.event.get():
                if event.type == KEYUP:
                    self.handle_keys(dt, event)

            self.draw()
            win = self.check_for_win()
            if win:
                return

    def run(self):
        while True:
            self.show_start_screen()
            self.show_game_text()
            self.show_game()
            self.show_win_screen()
            for player in self.players:
                player.randomize_position()


def main():
    theme = cfg.themes[0]
    game = Game(width=cfg.board_size, height=cfg.board_size, theme=theme)
    game.run()


if __name__ == '__main__':
    main()



