import pygame
import math


class Car:
    """
    Top-down F1 car with simple arcade physics.

    Angle convention: 0 = facing right, 90 = facing down (screen coords).
    """

    def __init__(self, start_pos, start_angle, color, name="Car"):
        self.pos = pygame.Vector2(start_pos)
        self.angle = start_angle        # degrees
        self.speed = 0.0               # pixels/sec
        self.color = color
        self.name = name
        self.is_player = False

        # Physics tuning
        self.max_speed = 310.0         # px/s on-track
        self.acceleration = 195.0      # px/s^2
        self.braking = 290.0           # px/s^2
        self.drag = 1.1                # passive speed decay coefficient
        self.steering_rate = 115.0     # deg/s at max speed

        # Race state
        self.total_checkpoints = 1     # already past waypoint-0 (grid start)
        self.laps_completed = 0
        self.lap_time = 0.0
        self.best_lap = float("inf")
        self.total_time = 0.0
        self.finished = False
        self.finish_time = 0.0
        self.total_laps = 3            # overridden by game before race

        self.on_track = True

        # Sprite
        self.car_w = 22
        self.car_h = 12
        self._surf = self._make_surface()

    # ------------------------------------------------------------------
    # Sprite
    # ------------------------------------------------------------------

    def _make_surface(self):
        surf = pygame.Surface((self.car_w, self.car_h), pygame.SRCALPHA)
        # Main body
        surf.fill(self.color)
        # Nose / front end (darker tint)
        darker = tuple(max(0, c - 55) for c in self.color)
        nose_w = self.car_w // 3
        pygame.draw.rect(surf, darker,
                         (self.car_w - nose_w, 0, nose_w, self.car_h))
        # Cockpit
        cockpit_color = (15, 15, 15)
        cx = self.car_w // 3
        pygame.draw.rect(surf, cockpit_color,
                         (cx, 2, self.car_w // 4, self.car_h - 4))
        return surf

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt, controls, track):
        if self.finished:
            self.speed = max(0.0, self.speed - 150.0 * dt)
            self._apply_movement(dt)
            self.total_time += dt
            return

        accel = controls.get("accel", 0.0)
        brake = controls.get("brake", 0.0)
        left  = controls.get("left",  0.0)
        right = controls.get("right", 0.0)

        self.on_track = track.is_on_track(self.pos)
        speed_cap = self.max_speed if self.on_track else self.max_speed * 0.38

        # Longitudinal
        if accel:
            self.speed += self.acceleration * accel * dt
        if brake:
            self.speed -= self.braking * brake * dt

        # Passive drag
        self.speed -= self.speed * self.drag * dt
        self.speed = max(0.0, min(speed_cap, self.speed))

        # Steering (proportional to speed ratio, min 25 %)
        speed_ratio = self.speed / self.max_speed
        steer_factor = max(0.25, speed_ratio)
        self.angle += (right - left) * self.steering_rate * steer_factor * dt

        self._apply_movement(dt)

        self.lap_time += dt
        self.total_time += dt
        self._check_waypoint(track)

    def _apply_movement(self, dt):
        rad = math.radians(self.angle)
        self.pos.x += math.cos(rad) * self.speed * dt
        self.pos.y += math.sin(rad) * self.speed * dt

    # ------------------------------------------------------------------
    # Checkpoint / lap logic
    # ------------------------------------------------------------------

    def _check_waypoint(self, track):
        n = len(track.waypoints)
        target_idx = self.total_checkpoints % n
        target = track.get_target(target_idx)

        if self.pos.distance_to(target) < 48:
            self.total_checkpoints += 1

            # Lap completion: we just passed waypoint-0 (start/finish line)
            if target_idx == 0:
                if self.laps_completed > 0:
                    if self.lap_time < self.best_lap:
                        self.best_lap = self.lap_time
                self.lap_time = 0.0
                self.laps_completed += 1
                if self.laps_completed >= self.total_laps:
                    self.finished = True
                    self.finish_time = self.total_time

    def get_race_progress(self):
        """Monotonically increasing value used for position sorting."""
        return self.total_checkpoints

    def current_lap_display(self):
        return min(self.laps_completed + 1, self.total_laps)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface):
        rotated = pygame.transform.rotate(self._surf, -self.angle)
        rect = rotated.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surface.blit(rotated, rect)


def format_time(seconds):
    """Format seconds as mm:ss.mmm."""
    if seconds == float("inf") or seconds < 0:
        return "--:--.---"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1.0) * 1000)
    return f"{minutes:02d}:{secs:02d}.{ms:03d}"
