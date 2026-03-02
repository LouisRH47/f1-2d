import math
import pygame


class AIDriver:
    """
    Waypoint-following AI with predictive corner braking and basic overtaking.
    """

    LOOKAHEAD = 4          # waypoints to inspect for upcoming corners
    STEER_GAIN = 45.0      # degrees at which full steering is applied
    CORNER_THRESH_HARD = 42.0   # angle delta → heavy braking
    CORNER_THRESH_SOFT = 22.0   # angle delta → moderate speed reduction
    OVERTAKE_RADIUS = 65        # px: proximity that triggers lateral offset
    OVERTAKE_OFFSET = 22        # px lateral shift when overtaking

    def __init__(self, car, difficulty=0.88):
        self.car = car
        self.difficulty = difficulty   # 0–1; scales max speed
        self._lateral_offset = 0.0    # current lateral offset for overtaking

    # ------------------------------------------------------------------
    # Main entry – called every frame
    # ------------------------------------------------------------------

    def get_controls(self, track, all_cars, player_car=None):
        car = self.car
        n = len(track.waypoints)
        target_idx = car.total_checkpoints % n
        target = track.get_target(target_idx)

        # Optional lateral overtake offset
        target = self._apply_overtake_offset(target, track, target_idx, all_cars)

        to_target = target - car.pos
        dist = to_target.length()

        if dist < 1:
            return {"accel": 1.0, "brake": 0.0, "left": 0.0, "right": 0.0}

        # Steering
        target_angle = math.degrees(math.atan2(to_target.y, to_target.x))
        angle_diff = (target_angle - car.angle + 180) % 360 - 180  # -180..180

        right = min(1.0, max(0.0,  angle_diff / self.STEER_GAIN))
        left  = min(1.0, max(0.0, -angle_diff / self.STEER_GAIN))

        # Speed management
        corner_sharpness = self._corner_sharpness(track, target_idx)
        target_speed = self._target_speed(car.max_speed, corner_sharpness)
        target_speed *= self.difficulty

        # Rubber-band: boost if player is far ahead
        if player_car and not car.finished:
            if player_car.laps_completed > car.laps_completed + 1:
                target_speed = min(car.max_speed, target_speed * 1.12)

        if car.speed > target_speed + 5:
            accel, brake = 0.0, min(1.0, (car.speed - target_speed) / 60.0)
        else:
            accel, brake = 1.0, 0.0

        return {"accel": accel, "brake": brake, "left": left, "right": right}

    # ------------------------------------------------------------------
    # Corner anticipation
    # ------------------------------------------------------------------

    def _corner_sharpness(self, track, current_idx):
        """Max angle change over the next LOOKAHEAD waypoints (degrees)."""
        n = len(track.waypoints)
        max_delta = 0.0
        for i in range(self.LOOKAHEAD):
            w0 = (current_idx + i)     % n
            w1 = (current_idx + i + 1) % n
            w2 = (current_idx + i + 2) % n
            p0 = pygame.Vector2(track.waypoints[w0])
            p1 = pygame.Vector2(track.waypoints[w1])
            p2 = pygame.Vector2(track.waypoints[w2])
            v1 = p1 - p0
            v2 = p2 - p1
            if v1.length() < 1 or v2.length() < 1:
                continue
            a1 = math.degrees(math.atan2(v1.y, v1.x))
            a2 = math.degrees(math.atan2(v2.y, v2.x))
            delta = abs((a2 - a1 + 180) % 360 - 180)
            max_delta = max(max_delta, delta)
        return max_delta

    def _target_speed(self, max_spd, sharpness):
        if sharpness >= self.CORNER_THRESH_HARD:
            return max_spd * 0.42
        if sharpness >= self.CORNER_THRESH_SOFT:
            t = (sharpness - self.CORNER_THRESH_SOFT) / (
                self.CORNER_THRESH_HARD - self.CORNER_THRESH_SOFT)
            return max_spd * (0.42 + (1.0 - 0.42) * (1.0 - t)) * 0.78
        return max_spd * 0.96

    # ------------------------------------------------------------------
    # Overtaking
    # ------------------------------------------------------------------

    def _apply_overtake_offset(self, target, track, target_idx, all_cars):
        """Shift the look-ahead target laterally when another car is close."""
        car = self.car
        n = len(track.waypoints)

        for other in all_cars:
            if other is car:
                continue
            if car.pos.distance_to(other.pos) > self.OVERTAKE_RADIUS:
                continue

            # Which side is the other car relative to our heading?
            rad = math.radians(car.angle)
            fwd = pygame.Vector2(math.cos(rad), math.sin(rad))
            to_other = other.pos - car.pos
            if fwd.dot(to_other) < 0:
                continue  # other car is behind us

            perp = pygame.Vector2(-fwd.y, fwd.x)
            side = 1 if perp.dot(to_other) > 0 else -1
            # Offset toward opposite side
            offset = -side * self.OVERTAKE_OFFSET

            # Get perpendicular of the track segment
            seg_dir = (track.get_target((target_idx + 1) % n) - target)
            if seg_dir.length() > 0:
                seg_dir = seg_dir.normalize()
            seg_perp = pygame.Vector2(-seg_dir.y, seg_dir.x)
            target = pygame.Vector2(target) + seg_perp * offset
            break

        return target
