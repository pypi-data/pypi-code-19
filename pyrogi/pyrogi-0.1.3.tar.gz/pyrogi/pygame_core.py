import pygame
import pyrogi
from pyrogi.drawing.pygame_graphics import PyGameGraphics
from pyrogi import Backend, KeyDownEvent, KeyUpEvent, MouseMovedEvent, MouseButtonDownEvent, MouseButtonUpEvent, MouseWheelScrolledEvent

TARGET_FRAMERATE = 60

class PyGameBackend(Backend):
    def __init__(self, window_dimensions, tile_dimensions, caption):
        super(PyGameBackend, self).__init__(
            window_dimensions, tile_dimensions, caption
        )
        pygame.init()

    def run(self):
        clock = pygame.time.Clock()
        g = PyGameGraphics()
        g.init_window(
            self.window_dimensions, self.tile_dimensions, self.caption
        )
        while True:
            if pygame.event.peek(pygame.QUIT):
                break
            else:
                self._handle_events(pygame.event.get())

            fps = clock.get_fps()
            pygame.display.set_caption('FPS: ' + str(fps))

            millis = clock.tick(TARGET_FRAMERATE)
            self.on_tick(millis)

            g.clear_screen()
            self.on_draw(g)
            pygame.display.update()

    def _handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_key_down(KeyDownEvent(event.unicode, event.key, event.mod))
            elif event.type == pygame.KEYUP:
                self.handle_key_up(KeyUpEvent(event.key, event.mod))
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_moved(MouseMovedEvent(event.pos, event.rel, event.buttons))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pyrogi.events.SCROLL_WHEEL_UP:
                    self.handle_mouse_wheel_scrolled(MouseWheelScrolledEvent(event.pos, 1))
                elif event.button == pyrogi.events.SCROLL_WHEEL_DOWN:
                    self.handle_mouse_wheel_scrolled(MouseWheelScrolledEvent(event.pos, -1))
                else:
                    self.handle_mouse_button_down(MouseButtonDownEvent(event.pos, event.button))
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_button_up(MouseButtonUpEvent(event.pos, event.button))

