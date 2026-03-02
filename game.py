import sys
import pygame

from car import Car
from ai import AIDriver
from hud import HUD
import tracks as track_registry

SCREEN_W = 1200
SCREEN_H = 800

# Car identities: (name, color)
CAR_DEFS = [
    ("Player",       (220,  50,  50)),   # Red   – player
    ("Hamilton",     ( 50, 110, 220)),   # Blue
    ("Vettel",       (220, 200,  50)),   # Yellow
    ("Leclerc",      ( 50, 185,  80)),   # Green
    ("Verstappen",   (220, 135,  50)),   # Orange
]

TOTAL_LAPS = 3

# Difficulty per AI slot (index 0 is player, indices 1-4 are AI)
AI_DIFFICULTIES = [0.82, 0.88, 0.85, 0.92]


class Game:
    STATE_MENU   = "menu"
    STATE_RACE   = "race"
    STATE_FINISH = "finish"

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self.state  = self.STATE_MENU
        self.hud    = HUD()

        # Menu selection
        self.track_names  = list(track_registry.TRACKS.keys())
        self.selected_idx = 0          # index into track_names

        # Race objects (created when race starts)
        self.track    = None
        self.cars     = []
        self.ai_list  = []

        # Pre-load fonts for menu
        pygame.font.init()
        self.f_title  = pygame.font.SysFont("freesansbold", 72)
        self.f_large  = pygame.font.SysFont("freesansbold", 36)
        self.f_medium = pygame.font.SysFont("freesansbold", 24)
        self.f_small  = pygame.font.SysFont("freesansbold", 18)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)   # cap physics timestep

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            self._update(dt)
            self._draw()
            pygame.display.flip()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_event(self, event):
        if self.state == self.STATE_MENU:
            self._menu_event(event)
        elif self.state == self.STATE_FINISH:
            self._finish_event(event)
        # Race input is polled via pygame.key.get_pressed()

    def _menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_idx = (self.selected_idx - 1) % len(self.track_names)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_idx = (self.selected_idx + 1) % len(self.track_names)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_race(self.track_names[self.selected_idx])
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self._card_rects()):
                if rect.collidepoint(mx, my):
                    self.selected_idx = i
                    self._start_race(self.track_names[i])

    def _finish_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.state = self.STATE_MENU
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt):
        if self.state != self.STATE_RACE:
            return

        keys = pygame.key.get_pressed()
        player_controls = {
            "accel": 1.0 if (keys[pygame.K_UP]    or keys[pygame.K_w]) else 0.0,
            "brake": 1.0 if (keys[pygame.K_DOWN]  or keys[pygame.K_s]) else 0.0,
            "left":  1.0 if (keys[pygame.K_LEFT]  or keys[pygame.K_a]) else 0.0,
            "right": 1.0 if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) else 0.0,
        }

        player = self.cars[0]
        player.update(dt, player_controls, self.track)

        for ai_driver in self.ai_list:
            controls = ai_driver.get_controls(self.track, self.cars, player)
            ai_driver.car.update(dt, controls, self.track)

        # End race when player finishes
        if player.finished:
            self.state = self.STATE_FINISH

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_RACE:
            self._draw_race()
        elif self.state == self.STATE_FINISH:
            self._draw_finish()

    # ---- Menu --------------------------------------------------------

    def _card_rects(self):
        n = len(self.track_names)
        card_w, card_h = 330, 360
        total_w = n * card_w + (n - 1) * 20
        start_x = (SCREEN_W - total_w) // 2
        y = 240
        return [
            pygame.Rect(start_x + i * (card_w + 20), y, card_w, card_h)
            for i in range(n)
        ]

    def _draw_menu(self):
        self.screen.fill((10, 12, 22))

        # Title
        title = self.f_title.render("F1 2D RACING", True, (220, 50, 50))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        sub = self.f_medium.render("SELECT TRACK  ←/→  ENTER to race", True, (160, 160, 160))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 165))

        cards = self._card_rects()
        for i, (name, rect) in enumerate(zip(self.track_names, cards)):
            track_fn = track_registry.TRACKS[name]

            selected = (i == self.selected_idx)
            border_c = (220, 200, 50) if selected else (60, 60, 80)
            bg_c     = (25, 30, 50)   if selected else (18, 20, 32)

            pygame.draw.rect(self.screen, bg_c, rect, border_radius=10)
            pygame.draw.rect(self.screen, border_c, rect, 3, border_radius=10)

            # Track name
            nt = self.f_large.render(name, True, (255, 255, 255))
            self.screen.blit(nt, (rect.x + rect.w // 2 - nt.get_width() // 2,
                                  rect.y + 18))

            # Mini track preview
            preview = pygame.Rect(rect.x + 15, rect.y + 70, rect.w - 30, 210)
            # Draw a tiny track outline using a temporary Track object
            self._draw_track_preview(name, preview, selected)

            # Description
            try:
                tmp = track_fn()
                desc_lines = tmp.description.split("\n")
            except Exception:
                desc_lines = []
            for j, line in enumerate(desc_lines):
                dt_ = self.f_small.render(line, True, (180, 180, 180))
                self.screen.blit(dt_, (rect.x + rect.w // 2 - dt_.get_width() // 2,
                                       rect.y + 290 + j * 22))

        # Controls hint
        hint = self.f_small.render("Controls: WASD or Arrow Keys", True, (100, 100, 120))
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 55))

    _preview_cache: dict = {}

    def _draw_track_preview(self, name, rect, selected):
        cache_key = (name, rect.width, rect.height)
        if cache_key not in self._preview_cache:
            # Build Track temporarily to get waypoints
            track_fn = track_registry.TRACKS[name]
            tmp = track_fn()
            self._preview_cache[cache_key] = tmp.minimap_points(rect)

        pts = self._preview_cache[cache_key]
        color = (120, 120, 120) if not selected else (170, 170, 170)
        if len(pts) >= 2:
            pygame.draw.lines(self.screen, color, True, pts, 4)

    # ---- Race --------------------------------------------------------

    def _draw_race(self):
        self.track.draw(self.screen)
        for car in self.cars:
            car.draw(self.screen)
        player = self.cars[0]
        self.hud.draw(self.screen, player, self.cars, self.track, TOTAL_LAPS)
        self.hud.draw_off_track(self.screen, player)

    # ---- Finish ------------------------------------------------------

    def _draw_finish(self):
        self.track.draw(self.screen)
        for car in self.cars:
            car.draw(self.screen)
        self.hud.draw_finish(self.screen, self.cars, self.cars[0], self.track.name)

    # ------------------------------------------------------------------
    # Race setup
    # ------------------------------------------------------------------

    def _start_race(self, track_name):
        track_fn = track_registry.TRACKS[track_name]
        self.track = track_fn()

        start_pos = self.track.start_positions   # list of (Vector2, angle)

        self.cars = []
        self.ai_list = []

        for i, (name, color) in enumerate(CAR_DEFS):
            if i >= len(start_pos):
                break
            pos, angle = start_pos[i]
            car = Car(pos, angle, color, name)
            car.total_laps = TOTAL_LAPS
            if i == 0:
                car.is_player = True
            self.cars.append(car)

        for idx, car in enumerate(self.cars[1:]):
            diff = AI_DIFFICULTIES[idx % len(AI_DIFFICULTIES)]
            self.ai_list.append(AIDriver(car, difficulty=diff))

        self.state = self.STATE_RACE
