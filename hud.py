import pygame
from car import format_time

SCREEN_W = 1200
SCREEN_H = 800

# HUD colours
C_WHITE   = (255, 255, 255)
C_YELLOW  = (255, 220,  50)
C_GREEN   = ( 80, 220,  80)
C_RED     = (220,  50,  50)
C_BLACK   = (  0,   0,   0)
C_PANEL   = (  0,   0,   0, 160)   # semi-transparent


def _surface(w, h, color=C_PANEL):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill(color)
    return s


class HUD:
    def __init__(self):
        pygame.font.init()
        self.f_large  = pygame.font.SysFont("freesansbold", 32)
        self.f_medium = pygame.font.SysFont("freesansbold", 22)
        self.f_small  = pygame.font.SysFont("freesansbold", 16)
        self.f_big    = pygame.font.SysFont("freesansbold", 48)

    # ------------------------------------------------------------------
    # Main draw
    # ------------------------------------------------------------------

    def draw(self, surface, player, all_cars, track, total_laps):
        self._draw_lap_panel(surface, player, total_laps)
        self._draw_position_panel(surface, player, all_cars)
        self._draw_speed_panel(surface, player)
        self._draw_minimap(surface, track, all_cars, player)

    # ------------------------------------------------------------------
    # Panels
    # ------------------------------------------------------------------

    def _draw_lap_panel(self, surface, player, total_laps):
        panel = _surface(220, 85)
        surface.blit(panel, (10, 10))
        lap_num = player.current_lap_display()
        txt = self.f_large.render(f"LAP  {lap_num} / {total_laps}", True, C_WHITE)
        surface.blit(txt, (18, 16))
        # Lap time
        lt = self.f_medium.render(format_time(player.lap_time), True, C_YELLOW)
        surface.blit(lt, (18, 52))
        # Best lap
        bl = self.f_small.render(f"Best: {format_time(player.best_lap)}", True, C_GREEN)
        surface.blit(bl, (120, 58))

    def _draw_position_panel(self, surface, player, all_cars):
        # Sort by progress descending
        ranked = sorted(all_cars, key=lambda c: c.get_race_progress(), reverse=True)
        pos = next((i + 1 for i, c in enumerate(ranked) if c is player), 1)

        panel = _surface(130, 55)
        surface.blit(panel, (SCREEN_W - 140, 10))
        pos_color = C_YELLOW if pos == 1 else C_WHITE
        txt = self.f_big.render(f"P{pos}", True, pos_color)
        surface.blit(txt, (SCREEN_W - 130, 12))

    def _draw_speed_panel(self, surface, player):
        # Speed in km/h: 1 px/s ≈ 0.36 km/h (1 px = 0.1 m, so 1 px/s = 0.36 km/h)
        kmh = int(player.speed * 0.36)
        panel = _surface(145, 45)
        surface.blit(panel, (SCREEN_W - 155, SCREEN_H - 55))
        spd = self.f_large.render(f"{kmh:3d} km/h", True, C_WHITE)
        surface.blit(spd, (SCREEN_W - 150, SCREEN_H - 50))

    # ------------------------------------------------------------------
    # Mini-map
    # ------------------------------------------------------------------

    def _draw_minimap(self, surface, track, all_cars, player):
        MAP_W, MAP_H = 180, 145
        MAP_X = SCREEN_W - MAP_W - 10
        MAP_Y = SCREEN_H - MAP_H - 65

        bg = _surface(MAP_W + 4, MAP_H + 4, (0, 0, 0, 180))
        surface.blit(bg, (MAP_X - 2, MAP_Y - 2))

        rect = pygame.Rect(MAP_X, MAP_Y, MAP_W, MAP_H)
        pts = track.minimap_points(rect)
        if len(pts) >= 2:
            pygame.draw.lines(surface, (130, 130, 130), True, pts, 2)

        # Car dots on mini-map
        xs = [p[0] for p in track.waypoints]
        ys = [p[1] for p in track.waypoints]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        scale = min(MAP_W / span_x, MAP_H / span_y) * 0.9
        off_x = MAP_X + (MAP_W - span_x * scale) / 2
        off_y = MAP_Y + (MAP_H - span_y * scale) / 2

        for car in all_cars:
            mx = int(off_x + (car.pos.x - min_x) * scale)
            my = int(off_y + (car.pos.y - min_y) * scale)
            r = 5 if car is player else 3
            pygame.draw.circle(surface, car.color, (mx, my), r)
            if car is player:
                pygame.draw.circle(surface, C_WHITE, (mx, my), r + 2, 1)

    # ------------------------------------------------------------------
    # Finish / results screen
    # ------------------------------------------------------------------

    def draw_finish(self, surface, all_cars, player, track_name):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.f_big.render("RACE FINISHED!", True, C_YELLOW)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))

        sub = self.f_medium.render(track_name, True, (180, 180, 180))
        surface.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 145))

        # Sort: finished by finish_time, then DNF by progress
        finished = sorted([c for c in all_cars if c.finished],
                          key=lambda c: c.finish_time)
        racing  = sorted([c for c in all_cars if not c.finished],
                         key=lambda c: c.get_race_progress(), reverse=True)
        ranked  = finished + racing

        # Table header
        hdr_x = SCREEN_W // 2 - 260
        y = 195
        hdr = self.f_medium.render("POS   DRIVER                TIME", True, (160, 160, 160))
        surface.blit(hdr, (hdr_x, y))
        y += 30
        pygame.draw.line(surface, (100, 100, 100),
                         (hdr_x, y), (hdr_x + 520, y), 1)
        y += 8

        for i, car in enumerate(ranked):
            pos_num = i + 1
            highlight = car is player
            color = C_YELLOW if highlight else C_WHITE
            time_str = format_time(car.finish_time) if car.finished else "DNF"

            row = self.f_medium.render(
                f" {pos_num:2d}    {car.name:<22s}  {time_str}", True, color)

            # Draw colour swatch
            pygame.draw.rect(surface, car.color,
                             (hdr_x - 20, y + 2, 12, 18))
            surface.blit(row, (hdr_x, y))
            y += 30

        # Instructions
        inst = self.f_small.render("SPACE – Race again     ESC – Quit", True, (150, 150, 150))
        surface.blit(inst, (SCREEN_W // 2 - inst.get_width() // 2, SCREEN_H - 70))

    # ------------------------------------------------------------------
    # Off-track warning
    # ------------------------------------------------------------------

    def draw_off_track(self, surface, player):
        if not player.on_track and not player.finished:
            warn = self.f_medium.render("OFF TRACK", True, C_RED)
            surface.blit(warn, (SCREEN_W // 2 - warn.get_width() // 2, 30))
