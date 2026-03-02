# Product Requirements Document — 2D Top-Down F1-Style Racing Game

## 1. Project Goal

Build a 2D bird's-eye racing game where the player drives a top-down formula car on four real-world circuits, with a polished loop:

**Main Menu → Track Select → Race → Results → Replay / Change Track**

- Reliable lap counting (checkpoints + start/finish direction)
- Timing (current lap, best lap, session total)
- Clean track presentation with circuit name, city, country, and flag

---

## 2. Circuits

| Circuit | City / Region | Country | Length | Turns |
|---|---|---|---|---|
| Bahrain International Circuit | Sakhir | Bahrain | 5.412 km | 15 |
| Autodromo Internazionale Enzo e Dino Ferrari (Imola) | Imola, Emilia-Romagna | Italy | 4.909 km | — |
| Autodromo Nazionale Monza | Monza | Italy | 5.793 km | 11 |
| Autódromo Hermanos Rodríguez | Mexico City | Mexico | 4.304 km | 17 |

> Turn counts from Wikipedia where F1 site omits them; lengths from the official F1 site.

---

## 3. Non-Negotiable Design Decisions

### 3.1 Platform
**Python + Pygame** (current implementation)

### 3.2 Track Representation

**v1 — Image-mask tracks**
- Each track: a visual image + a surface-map image defining asphalt, off-track, and wall pixels
- Collision: pixel sampling under car corners (rectangle collider)

**v2 (planned upgrade) — Vector tracks**
- Centerline polyline + width; boundaries from geometry
- Better collision stability, consistent physics, easier AI

---

## 4. Data Model

### 4.1 Track Metadata (per circuit)
- Circuit display name
- Alternate/official name (e.g. Imola's full name)
- City / region
- Country
- Flag reference (ISO code or asset key)
- Circuit length (km)
- Turn count

### 4.2 Gameplay Geometry (per circuit)
- Spawn position + heading
- Start/finish line segment (two points) + direction vector
- Ordered checkpoints: 6–12 gates per lap, must be crossed in order
- Reset zones (optional, for returning car to track)

### 4.3 Scaling & Tuning (per circuit)
- `pixels_per_meter` (or inverse)
- Recommended camera zoom
- Surface grip multipliers (asphalt / off-track)
- Wall restitution + collision damping

---

## 5. Game States

```
Boot/Loading → Main Menu → Track Select → Race → Pause → Results
                                          ↑________________________↓ (restart / change track)
```

---

## 6. Systems (build once, reuse across tracks)

| System | Responsibility |
|---|---|
| Input | Keyboard + optional controller |
| Physics | Fixed timestep; forces per tick |
| Collision & Surface | Pixel sampling (v1); vector (v2) |
| Track Renderer | Visual map + minimap |
| Lap Timing | Checkpoint validation + time tracking |
| HUD | Timers, lap counter, best lap, speed, minimap |
| Audio | Engine loop, skid, collision sounds |
| Save / Settings | Controls, volume, best times per track |

---

## 7. Driving Model

### 7.1 Car State
- Position `(x, y)`
- Velocity vector
- Heading angle
- Angular velocity

### 7.2 Forces
- Engine acceleration (forward)
- Braking (opposes forward motion)
- Lateral friction (reduces sideways sliding gradually)
- Drag (limits top speed)
- Surface modifiers:
  - Asphalt → normal grip
  - Off-track → lower grip + higher drag
  - Wall → collision response + speed loss

### 7.3 Handling Targets
- **Low speed**: responsive steering, easy hairpins
- **High speed**: stable, but understeer if entry is too fast
- **Off-track**: noticeably slower and harder to steer, still controllable

---

## 8. Collision

### v1 (image-mask)
- Collider: bounding rectangle
- Each physics tick: sample pixels under corners (+ optionally centre)
  - Wall pixel → push car out along minimum penetration direction + damp velocity
  - Off-track pixel → lower grip + extra drag

### v2 (vector, planned)
- Distance-to-boundary-spline checks
- Continuous collision → stable at high speed
- Enables consistent checkpoint generation + easier AI

---

## 9. Lap Timing & Validation

### Checkpoint Rules
- Must be crossed in strict order
- Wrong-order crossing → ignored until sequence rejoins correctly
- Lap only counts when **all** checkpoints cleared in order **then** start/finish crossed in correct direction

### Timing Data (tracked per session)
- Current lap time (running)
- Best lap time
- Previous lap time
- Optional: delta to best lap

### Persistence
- Best lap times saved per track locally

---

## 10. UI Requirements

### 10.1 Track Select Card (per circuit)
- Circuit name
- City, Country + flag
- Circuit length (km)
- Track thumbnail

### 10.2 In-Race HUD
- Lap number
- Current lap time
- Best lap time
- Speed
- Minimap (optional but recommended)

### 10.3 Results Screen
- Lap list (Lap 1, Lap 2, …)
- Best lap highlighted
- Total session time
- Buttons: **Restart** / **Track Select**

---

## 11. Asset Requirements (per track)

| Asset | Purpose |
|---|---|
| Visual map image | Rendered track |
| Surface / collision mask | Pixel-based collision + grip |
| Thumbnail | Track select card |
| Start/finish + checkpoints | Stored in track data file |

**Art rules:**
- All tracks: same orientation convention (north-up preferred)
- Standardised `pixels_per_meter` across all tracks for consistent car feel
- Collision boundaries slightly inside drawn walls (fairness)

---

## 12. Milestones

### M1 — Driving on a blank plane
- Game loop + fixed timestep
- Car controls + physics feel
- Camera follow + zoom
- Debug overlay (speed, slip angle)

**Done when:** driving feels stable and fun.

### M2 — One track playable (Bahrain)
- Render track image
- Surface mask collision
- Start/finish + checkpoints
- Lap timing + valid lap detection

**Done when:** 3 valid laps completable; best lap recorded reliably.

### M3 — All 4 tracks integrated
- Imola, Monza, Mexico track packages (assets + checkpoints)
- Track select UI with city / country / flag / length

**Done when:** all tracks playable, laps count correctly on each.

### M4 — Polish pass
- Better collision response (less snagging)
- Off-track penalties tuned
- Audio: engine loop, skid, crash
- Results screen + saved best laps per track

**Done when:** feels like a real game loop, not a demo.

### M5 — AI & Racing Line (optional)
- Racing line polyline per track
- AI follows line with lookahead steering
- Basic speed control by curvature
- Ghost car as easier first step before full AI

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Track mask production takes too long | Start with simplified shapes; refine later |
| Collision feels janky at speed | Smaller substeps + corner sampling + velocity damping; plan v2 vector collision |
| Lap cheating (corner cutting) | Dense checkpoints at cut-prone zones; require correct direction at start/finish |
| Inconsistent feel across tracks | Enforce one shared `pixels_per_meter` guideline; tune once and lock |

---

## 14. Status

| Milestone | Status |
|---|---|
| M1 — Driving on blank plane | ✅ Complete |
| M2 — One track playable | ✅ Complete (Monza) |
| M3 — All 4 tracks integrated | 🔲 In progress |
| M4 — Polish pass | 🔲 Not started |
| M5 — AI & Racing Line | 🔲 Not started |
