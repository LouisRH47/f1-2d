import pygame
import math

SCREEN_W = 1200
SCREEN_H = 800


class Track:
    def __init__(self, name, waypoints, track_width, bg_color,
                 track_color, border_color, description=""):
        self.name = name
        self.waypoints = waypoints          # list of (x, y) tuples
        self.track_width = track_width
        self.bg_color = bg_color
        self.track_color = track_color
        self.border_color = border_color
        self.description = description

        # Pre-render and build collision mask
        self.surface = self._render()
        self.mask = self._build_mask()
        self.start_positions = self._compute_starts()

    # ------------------------------------------------------------------
    # Pre-rendering
    # ------------------------------------------------------------------

    def _render(self):
        surf = pygame.Surface((SCREEN_W, SCREEN_H))
        surf.fill(self.bg_color)
        n = len(self.waypoints)

        # Draw track surface
        for i in range(n):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % n]
            pygame.draw.line(surf, self.track_color, p1, p2, self.track_width)

        # Fill gaps at joints with circles
        for p in self.waypoints:
            pygame.draw.circle(surf, self.track_color, p, self.track_width // 2)

        # Draw white border lines
        for i in range(n):
            p1 = pygame.Vector2(self.waypoints[i])
            p2 = pygame.Vector2(self.waypoints[(i + 1) % n])
            seg = p2 - p1
            if seg.length() < 1:
                continue
            perp = pygame.Vector2(-seg.y, seg.x).normalize() * (self.track_width // 2 - 3)
            pygame.draw.line(surf, self.border_color,
                             (int(p1.x + perp.x), int(p1.y + perp.y)),
                             (int(p2.x + perp.x), int(p2.y + perp.y)), 2)
            pygame.draw.line(surf, self.border_color,
                             (int(p1.x - perp.x), int(p1.y - perp.y)),
                             (int(p2.x - perp.x), int(p2.y - perp.y)), 2)

        # Draw start/finish line at waypoint 0
        self._draw_start_line(surf)

        return surf

    def _draw_start_line(self, surf):
        p0 = pygame.Vector2(self.waypoints[0])
        p1 = pygame.Vector2(self.waypoints[1])
        seg = p1 - p0
        if seg.length() < 1:
            return
        perp = pygame.Vector2(-seg.y, seg.x).normalize() * (self.track_width // 2)

        # Checkered pattern across track width
        steps = 8
        for k in range(steps):
            t0 = k / steps
            t1 = (k + 1) / steps
            a = p0 - perp + perp * 2 * t0
            b = p0 - perp + perp * 2 * t1
            color = (255, 255, 255) if k % 2 == 0 else (0, 0, 0)
            pygame.draw.line(surf, color,
                             (int(a.x), int(a.y)),
                             (int(b.x), int(b.y)), 6)

    # ------------------------------------------------------------------
    # Collision mask
    # ------------------------------------------------------------------

    def _build_mask(self):
        mask_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        mask_surf.fill((0, 0, 0, 0))
        n = len(self.waypoints)
        WHITE = (255, 255, 255, 255)
        for i in range(n):
            p1 = self.waypoints[i]
            p2 = self.waypoints[(i + 1) % n]
            pygame.draw.line(mask_surf, WHITE, p1, p2, self.track_width)
        for p in self.waypoints:
            pygame.draw.circle(mask_surf, WHITE, p, self.track_width // 2)
        return pygame.mask.from_surface(mask_surf)

    def is_on_track(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < SCREEN_W and 0 <= y < SCREEN_H:
            try:
                return bool(self.mask.get_at((x, y)))
            except IndexError:
                return False
        return False

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))

    def get_target(self, checkpoint_idx):
        return pygame.Vector2(self.waypoints[checkpoint_idx % len(self.waypoints)])

    def _compute_starts(self):
        """Return list of (Vector2 pos, float angle_degrees) for 5 grid slots."""
        p0 = pygame.Vector2(self.waypoints[0])
        p1 = pygame.Vector2(self.waypoints[1])
        direction = p1 - p0
        if direction.length() < 1:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()

        perp = pygame.Vector2(-direction.y, direction.x)
        angle = math.degrees(math.atan2(direction.y, direction.x))

        positions = []
        for i in range(5):
            row = i // 2
            col = i % 2
            side = 16 if col == 1 else -16
            pos = p0 - direction * (40 + row * 55) + perp * side
            positions.append((pygame.Vector2(pos), angle))
        return positions

    def minimap_points(self, rect):
        """Scale waypoints to fit inside a pygame.Rect for mini-map display."""
        xs = [p[0] for p in self.waypoints]
        ys = [p[1] for p in self.waypoints]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        scale = min(rect.width / span_x, rect.height / span_y) * 0.9
        off_x = rect.x + (rect.width  - span_x * scale) / 2
        off_y = rect.y + (rect.height - span_y * scale) / 2
        return [
            (int(off_x + (p[0] - min_x) * scale),
             int(off_y + (p[1] - min_y) * scale))
            for p in self.waypoints
        ]
