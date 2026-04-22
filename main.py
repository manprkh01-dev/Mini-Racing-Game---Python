import pygame
import math
import random
import sys
import os

# ─── INIT ────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60

# Colours
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GRAY        = (80,  80,  80)
DARK_GRAY   = (40,  40,  40)
ASPHALT     = (50,  52,  55)
LINE_WHITE  = (220, 220, 200)
GRASS       = (34,  85,  34)
GRASS2      = (28,  72,  28)
RED         = (220, 40,  40)
BLUE        = (40,  100, 220)
YELLOW      = (230, 200, 30)
ORANGE      = (230, 130, 20)
CYAN        = (40,  210, 210)
PINK        = (220, 60,  160)
GREEN       = (50,  200, 80)
DARK_RED    = (140, 20,  20)
GOLD        = (255, 215, 0)
SILVER      = (192, 192, 192)
BRONZE      = (205, 127, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("APEX RACER")
clock = pygame.time.Clock()

# ─── FONTS ───────────────────────────────────────────────────────────────────
font_big    = pygame.font.SysFont("Impact", 72)
font_med    = pygame.font.SysFont("Impact", 36)
font_small  = pygame.font.SysFont("Arial", 22)
font_tiny   = pygame.font.SysFont("Arial", 16)
font_hud    = pygame.font.SysFont("Consolas", 20)

# ─── TRACK DEFINITION ────────────────────────────────────────────────────────
# Waypoints define the centre-line of the track (closed loop)
RAW_WAYPOINTS = [
    (500, 80),
    (800, 80),
    (900, 160),
    (920, 300),
    (880, 420),
    (780, 500),
    (680, 560),
    (600, 620),
    (500, 640),
    (380, 620),
    (260, 570),
    (160, 490),
    (100, 380),
    (90,  260),
    (140, 160),
    (240, 90),
    (360, 70),
]
TRACK_WIDTH = 72          # half-width of drivable surface

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def normalize(v):
    mag = math.hypot(v[0], v[1])
    return (v[0]/mag, v[1]/mag) if mag else (0, 0)

def perpendicular(v):
    return (-v[1], v[0])

def lerp(a, b, t):
    return a + (b - a) * t

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def angle_diff(a, b):
    d = (b - a + 360) % 360
    if d > 180: d -= 360
    return d

# ─── BUILD TRACK POLYGON ─────────────────────────────────────────────────────
def build_track_polys(waypoints, half_w):
    pts = waypoints + [waypoints[0], waypoints[1]]  # wrap-around
    inner, outer = [], []
    n = len(waypoints)
    for i in range(n):
        prev = waypoints[(i-1) % n]
        curr = waypoints[i]
        nxt  = waypoints[(i+1) % n]
        d1   = normalize((curr[0]-prev[0], curr[1]-prev[1]))
        d2   = normalize((nxt[0]-curr[0],  nxt[1]-curr[1]))
        tang = normalize((d1[0]+d2[0], d1[1]+d2[1]))
        perp = perpendicular(tang)
        inner.append((curr[0] + perp[0]*half_w, curr[1] + perp[1]*half_w))
        outer.append((curr[0] - perp[0]*half_w, curr[1] - perp[1]*half_w))
    return inner, outer

INNER_POLY, OUTER_POLY = build_track_polys(RAW_WAYPOINTS, TRACK_WIDTH)

# ─── TRACK SURFACE (pre-rendered) ────────────────────────────────────────────
track_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
track_surf.fill((0,0,0,0))

# grass background
pygame.draw.rect(track_surf, GRASS, (0, 0, WIDTH, HEIGHT))
# subtle grass pattern
for gx in range(0, WIDTH, 20):
    for gy in range(0, HEIGHT, 20):
        if (gx//20 + gy//20) % 2 == 0:
            pygame.draw.rect(track_surf, GRASS2, (gx, gy, 20, 20))

# asphalt road
pygame.draw.polygon(track_surf, ASPHALT, OUTER_POLY)
pygame.draw.polygon(track_surf, GRASS, INNER_POLY)   # cut out inner

# road edge markings
pygame.draw.polygon(track_surf, (220,220,200), OUTER_POLY, 3)
pygame.draw.polygon(track_surf, (220,220,200), INNER_POLY, 3)

# dashed centre line
n = len(RAW_WAYPOINTS)
for i in range(n):
    a = RAW_WAYPOINTS[i]
    b = RAW_WAYPOINTS[(i+1)%n]
    # draw dash every 40px along segment
    seg_len = dist(a, b)
    steps   = max(1, int(seg_len / 40))
    for s in range(steps):
        if s % 2 == 0:
            t0 = s / steps
            t1 = (s+0.5) / steps
            p0 = (lerp(a[0],b[0],t0), lerp(a[1],b[1],t0))
            p1 = (lerp(a[0],b[0],t1), lerp(a[1],b[1],t1))
            pygame.draw.line(track_surf, (200,190,100), (int(p0[0]),int(p0[1])), (int(p1[0]),int(p1[1])), 2)

# kerbs (red/white stripes on outer edge)
KERB_W = 10
for i in range(n):
    a_out = OUTER_POLY[i]
    b_out = OUTER_POLY[(i+1)%n]
    a_in  = INNER_POLY[i]
    b_in  = INNER_POLY[(i+1)%n]
    colour = RED if i % 2 == 0 else WHITE
    # outer kerb
    d = normalize((b_out[0]-a_out[0], b_out[1]-a_out[1]))
    p = perpendicular(d)
    kerb = [a_out, b_out,
            (b_out[0]+p[0]*KERB_W, b_out[1]+p[1]*KERB_W),
            (a_out[0]+p[0]*KERB_W, a_out[1]+p[1]*KERB_W)]
    pygame.draw.polygon(track_surf, colour, kerb)

# start/finish line
sf_a = RAW_WAYPOINTS[0]
sf_b = RAW_WAYPOINTS[1]
d_sf  = normalize((sf_b[0]-sf_a[0], sf_b[1]-sf_a[1]))
p_sf  = perpendicular(d_sf)
# perpendicular line at waypoint 0
wpt   = RAW_WAYPOINTS[0]
for k in range(-TRACK_WIDTH, TRACK_WIDTH, 8):
    col = WHITE if (k//8) % 2 == 0 else BLACK
    p0 = (wpt[0]+p_sf[0]*k,       wpt[1]+p_sf[1]*k)
    p1 = (wpt[0]+p_sf[0]*(k+8),   wpt[1]+p_sf[1]*(k+8))
    pygame.draw.line(track_surf, col, (int(p0[0]),int(p0[1])), (int(p1[0]),int(p1[1])), 5)

# ─── POINT-ON-TRACK CHECK ────────────────────────────────────────────────────
def point_in_polygon(pt, poly):
    x, y = pt
    inside = False
    n2 = len(poly)
    j = n2 - 1
    for i in range(n2):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-9)+xi):
            inside = not inside
        j = i
    return inside

def on_track(pt):
    return point_in_polygon(pt, OUTER_POLY) and not point_in_polygon(pt, INNER_POLY)

# ─── NEAREST WAYPOINT ────────────────────────────────────────────────────────
def nearest_waypoint(pos):
    best_i, best_d = 0, 1e9
    for i, wp in enumerate(RAW_WAYPOINTS):
        d = dist(pos, wp)
        if d < best_d:
            best_d, best_i = d, i
    return best_i

def progress(pos):
    """Returns a float 0..N representing track progress."""
    n2 = len(RAW_WAYPOINTS)
    bi = nearest_waypoint(pos)
    ni = (bi+1) % n2
    seg_len = dist(RAW_WAYPOINTS[bi], RAW_WAYPOINTS[ni])
    d_to_next = dist(pos, RAW_WAYPOINTS[ni])
    frac = max(0, min(1, 1 - d_to_next / (seg_len+1e-9)))
    return (bi + frac) % n2

# ─── CAR ─────────────────────────────────────────────────────────────────────
class Car:
    W, H = 16, 30   # half-width, half-height for drawing

    def __init__(self, x, y, angle, colour, name, is_player=False):
        self.x      = float(x)
        self.y      = float(y)
        self.angle  = float(angle)   # degrees, 0=up
        self.speed  = 0.0
        self.colour = colour
        self.name   = name
        self.is_player = is_player

        # physics params
        self.max_speed    = 5.8 if is_player else random.uniform(5.0, 5.6)
        self.accel        = 0.18
        self.brake_str    = 0.25
        self.friction     = 0.97
        self.steer_speed  = 3.5
        self.off_track_fric = 0.88

        # race state
        self.lap          = 0
        self.waypoint     = 0
        self.finished     = False
        self.finish_time  = None
        self.place        = 0
        self.total_prog   = 0.0   # laps + progress
        self.crossed_sf   = False  # start/finish crossed

        # AI
        self.ai_target_wp = 1
        self.ai_wobble    = 0.0
        self.ai_wobble_t  = 0

        # visual
        self.trail = []
        self.smoke = []

    def rect_corners(self):
        """Return the 4 corners of the car rectangle in world space."""
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        hw, hh = self.W, self.H
        corners = [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]
        result = []
        for cx, cy in corners:
            rx = cos_a*cx - sin_a*cy + self.x
            ry = sin_a*cx + cos_a*cy + self.y
            result.append((rx, ry))
        return result

    def update_player(self, keys):
        if self.finished: return
        acc = 0
        steer = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            acc = self.accel
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            acc = -self.brake_str
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer = -self.steer_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer = self.steer_speed

        self._physics(acc, steer)

    def update_ai(self, difficulty=1.0):
        if self.finished: return
        n2 = len(RAW_WAYPOINTS)
        target = RAW_WAYPOINTS[self.ai_target_wp]
        dx = target[0] - self.x
        dy = target[1] - self.y
        d  = math.hypot(dx, dy)
        if d < 40:
            self.ai_target_wp = (self.ai_target_wp + 1) % n2

        # desired heading
        desired = math.degrees(math.atan2(dx, -dy)) % 360
        current = self.angle % 360
        diff    = angle_diff(current, desired)

        # wobble (makes AI imperfect)
        self.ai_wobble_t += 1
        if self.ai_wobble_t > 60:
            self.ai_wobble_t = 0
            self.ai_wobble = random.uniform(-8, 8) / difficulty

        steer = max(-self.steer_speed, min(self.steer_speed, diff * 0.18 + self.ai_wobble))

        # speed control: slow for sharp turns
        speed_factor = 1.0 - abs(diff)/180 * 0.5
        target_speed = self.max_speed * speed_factor * difficulty
        acc = self.accel if self.speed < target_speed else -0.05

        self._physics(acc, steer)

    def _physics(self, acc, steer):
        self.speed += acc
        self.speed  = max(-2.0, min(self.max_speed, self.speed))

        # steer only when moving
        if abs(self.speed) > 0.2:
            self.angle += steer * (abs(self.speed) / self.max_speed)

        # move
        rad = math.radians(self.angle)
        nx  = self.x + math.sin(rad) * self.speed
        ny  = self.y - math.cos(rad) * self.speed

        # off-track friction
        if on_track((nx, ny)):
            self.x, self.y = nx, ny
            self.speed *= self.friction
        else:
            self.x, self.y = nx, ny
            self.speed *= self.off_track_fric

        # trail
        if abs(self.speed) > 0.5:
            self.trail.append((self.x, self.y))
        if len(self.trail) > 30:
            self.trail.pop(0)

        # smoke when off-track
        if not on_track((self.x, self.y)) and abs(self.speed) > 1:
            self.smoke.append([self.x, self.y, random.uniform(-1,1), random.uniform(-2,-0.5), 20])
        for s in self.smoke:
            s[0] += s[2]; s[1] += s[3]; s[4] -= 1
        self.smoke = [s for s in self.smoke if s[4] > 0]

    def update_lap(self, race):
        if self.finished: return
        n2 = len(RAW_WAYPOINTS)
        # detect start/finish crossing
        sf_wp  = RAW_WAYPOINTS[0]
        d_sf   = dist((self.x, self.y), sf_wp)
        # simple: if near start waypoint and came from last waypoint
        wi = nearest_waypoint((self.x, self.y))
        # waypoint-gate laps
        if wi != self.waypoint:
            expected = (self.waypoint + 1) % n2
            if wi == expected:
                self.waypoint = wi
                if wi == 0:
                    self.lap += 1
                    if self.lap > race.total_laps:
                        self.finished    = True
                        self.finish_time = pygame.time.get_ticks()
                        race.car_finished(self)

        self.total_prog = self.lap * n2 + progress((self.x, self.y))

    def draw(self, surf):
        # draw trail
        for i, pt in enumerate(self.trail):
            alpha = int(180 * i / len(self.trail))
            r = max(1, int(2 * i / len(self.trail)))
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.colour, alpha), (r, r), r)
            surf.blit(s, (int(pt[0])-r, int(pt[1])-r))

        # draw smoke
        for sp in self.smoke:
            alpha = int(sp[4] * 8)
            r = 4
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 200, 200, alpha), (r, r), r)
            surf.blit(s, (int(sp[0])-r, int(sp[1])-r))

        # draw car body
        rad  = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        hw, hh = self.W, self.H

        def rotpt(cx, cy):
            rx = cos_a*cx - sin_a*cy + self.x
            ry = sin_a*cx + cos_a*cy + self.y
            return (int(rx), int(ry))

        # shadow
        shadow_offset = 3
        shadow_pts = [rotpt(-hw+shadow_offset, -hh+shadow_offset),
                      rotpt( hw+shadow_offset, -hh+shadow_offset),
                      rotpt( hw+shadow_offset,  hh+shadow_offset),
                      rotpt(-hw+shadow_offset,  hh+shadow_offset)]
        pygame.draw.polygon(surf, (20,20,20,100), shadow_pts)

        # body
        body_pts = [rotpt(-hw, -hh), rotpt(hw, -hh),
                    rotpt(hw,   hh), rotpt(-hw,  hh)]
        pygame.draw.polygon(surf, self.colour, body_pts)

        # windshield (lighter front third)
        ws_y = -hh * 0.2
        ws_pts = [rotpt(-hw+3, -hh+4), rotpt(hw-3, -hh+4),
                  rotpt(hw-3, ws_y),   rotpt(-hw+3, ws_y)]
        pygame.draw.polygon(surf, (200, 230, 255, 180), ws_pts)

        # outline
        pygame.draw.polygon(surf, BLACK, body_pts, 2)

        # headlights
        for sx in [-hw+3, hw-3]:
            p = rotpt(sx, -hh+2)
            pygame.draw.circle(surf, YELLOW, p, 3)

        # name tag (player only shown differently)
        if self.is_player:
            tag = font_tiny.render("YOU", True, WHITE)
            surf.blit(tag, (int(self.x) - tag.get_width()//2, int(self.y) - hh - 16))

# ─── OBSTACLE ────────────────────────────────────────────────────────────────
class OilSlick:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.r = 22

    def draw(self, surf):
        for i in range(5, 0, -1):
            col = (20, 20+i*5, 30+i*8, 80)
            s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
            pygame.draw.ellipse(s, col, (0, 0, self.r*2, int(self.r*1.3)))
            surf.blit(s, (int(self.x)-self.r, int(self.y)-self.r//2))

    def check(self, car):
        return dist((car.x, car.y), (self.x, self.y)) < self.r + car.W

# ─── PARTICLES ───────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, colour):
        self.x, self.y = x, y
        angle = random.uniform(0, math.pi*2)
        spd = random.uniform(2, 6)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.life = random.randint(20, 40)
        self.colour = colour

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.15
        self.vx *= 0.95; self.vy *= 0.95
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            alpha = int(255 * self.life / 40)
            r = max(1, int(self.life / 10))
            s = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.colour, alpha), (r,r), r)
            surf.blit(s, (int(self.x)-r, int(self.y)-r))

# ─── RACE ────────────────────────────────────────────────────────────────────
class Race:
    def __init__(self, total_laps=3, difficulty=1.0):
        self.total_laps = total_laps
        self.difficulty = difficulty
        self.finished_order = []
        self.particles = []
        self.start_time = None
        self.countdown  = 3
        self.countdown_timer = 0
        self.state = "countdown"   # countdown | racing | finished

        # spawn grid (staggered near waypoint 0)
        spawn_wp = RAW_WAYPOINTS[0]
        perp_d   = normalize(perpendicular(normalize((
            RAW_WAYPOINTS[1][0]-spawn_wp[0],
            RAW_WAYPOINTS[1][1]-spawn_wp[1]
        ))))
        back_d   = normalize((spawn_wp[0]-RAW_WAYPOINTS[1][0],
                               spawn_wp[1]-RAW_WAYPOINTS[1][1]))

        def grid_pos(row, col):
            # 2 columns, rows behind start
            ox = perp_d[0]*(col*36 - 18) + back_d[0]*(row*55 + 30)
            oy = perp_d[1]*(col*36 - 18) + back_d[1]*(row*55 + 30)
            return spawn_wp[0]+ox, spawn_wp[1]+oy

        heading = math.degrees(math.atan2(
            RAW_WAYPOINTS[1][0]-spawn_wp[0],
            -(RAW_WAYPOINTS[1][1]-spawn_wp[1])
        ))

        ai_configs = [
            (RED,    "Blaze",   (0,0)),
            (BLUE,   "Ice",     (0,1)),
            (ORANGE, "Turbo",   (1,0)),
            (CYAN,   "Nova",    (1,1)),
            (PINK,   "Drift",   (2,0)),
        ]

        px, py = grid_pos(2, 1)
        self.player = Car(px, py, heading, GREEN, "Player", is_player=True)
        self.player.waypoint = 0

        self.ai_cars = []
        for colour, name, (row, col) in ai_configs:
            ax, ay = grid_pos(row, col)
            c = Car(ax, ay, heading, colour, name)
            c.waypoint = 0
            self.ai_cars.append(c)

        self.all_cars = [self.player] + self.ai_cars

        # oil slicks on track
        self.oil_slicks = []
        oil_spots = [3, 7, 11, 14]
        for wi in oil_spots:
            wp = RAW_WAYPOINTS[wi]
            # slightly off-centre
            rx = wp[0] + random.randint(-20, 20)
            ry = wp[1] + random.randint(-20, 20)
            self.oil_slicks.append(OilSlick(rx, ry))

    def car_finished(self, car):
        self.finished_order.append(car)
        for i, p in enumerate(self.particles):
            pass
        # spawn celebration particles
        for _ in range(40):
            self.particles.append(Particle(car.x, car.y, GOLD))

    def rankings(self):
        return sorted(self.all_cars, key=lambda c: (-c.lap*100 - c.total_prog
                       + (1000 if c.finished else 0)*c.lap))

    def update(self):
        dt_ms = clock.get_time()

        if self.state == "countdown":
            self.countdown_timer += dt_ms
            if self.countdown_timer >= 1000:
                self.countdown_timer = 0
                self.countdown -= 1
                if self.countdown <= 0:
                    self.state = "racing"
                    self.start_time = pygame.time.get_ticks()
            return

        if self.state == "finished":
            for p in self.particles: p.update()
            self.particles = [p for p in self.particles if p.life > 0]
            return

        keys = pygame.key.get_pressed()
        self.player.update_player(keys)

        for ai in self.ai_cars:
            ai.update_ai(self.difficulty)

        for car in self.all_cars:
            car.update_lap(self)

            # oil slick effect
            for oil in self.oil_slicks:
                if oil.check(car):
                    car.angle += random.uniform(-6, 6)
                    car.speed *= 0.85

        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # check if all done or player done
        if self.player.finished and self.state == "racing":
            self.state = "finished"

    def draw(self, surf):
        # static track
        surf.blit(track_surf, (0, 0))

        # oil slicks
        for oil in self.oil_slicks:
            oil.draw(surf)

        # cars (sort by y for pseudo-depth)
        for car in sorted(self.all_cars, key=lambda c: c.y):
            car.draw(surf)

        # particles
        for p in self.particles:
            p.draw(surf)

        self.draw_hud(surf)

        if self.state == "countdown":
            self.draw_countdown(surf)

        if self.state == "finished":
            self.draw_finish(surf)

    def draw_hud(self, surf):
        # ── speed bar ──
        sp_pct = abs(self.player.speed) / self.player.max_speed
        bar_w  = 180
        bar_h  = 14
        bx, by = 20, HEIGHT - 60
        pygame.draw.rect(surf, DARK_GRAY, (bx, by, bar_w, bar_h), border_radius=7)
        col = GREEN if sp_pct < 0.7 else (YELLOW if sp_pct < 0.9 else RED)
        pygame.draw.rect(surf, col, (bx, by, int(bar_w*sp_pct), bar_h), border_radius=7)
        pygame.draw.rect(surf, WHITE, (bx, by, bar_w, bar_h), 2, border_radius=7)
        sp_label = font_hud.render(f"SPEED  {int(sp_pct*200)} km/h", True, WHITE)
        surf.blit(sp_label, (bx, by - 22))

        # ── lap counter ──
        lap_str = f"LAP  {min(self.player.lap+1, self.total_laps)} / {self.total_laps}"
        lap_txt = font_med.render(lap_str, True, WHITE)
        surf.blit(lap_txt, (WIDTH//2 - lap_txt.get_width()//2, 10))

        # ── timer ──
        if self.start_time:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            timer_txt = font_hud.render(f"{elapsed:.1f}s", True, (180,230,180))
            surf.blit(timer_txt, (WIDTH - 90, 12))

        # ── position board ──
        rankings = self.rankings()
        px2, py2 = WIDTH - 170, HEIGHT - 180
        board_surf = pygame.Surface((160, 175), pygame.SRCALPHA)
        pygame.draw.rect(board_surf, (0,0,0,160), (0,0,160,175), border_radius=8)
        board_surf.blit(font_tiny.render("STANDINGS", True, (200,200,200)), (8, 6))
        for i, car in enumerate(rankings[:6]):
            y_off = 24 + i*23
            medal = ["🥇","🥈","🥉","  4.","  5.","  6."][i]
            name_col = GOLD if car.is_player else WHITE
            board_surf.blit(font_tiny.render(f"{i+1}. {car.name}", True, name_col), (8, y_off))
            lap_info = font_tiny.render(f"L{car.lap}", True, (150,150,150))
            board_surf.blit(lap_info, (130, y_off))
        surf.blit(board_surf, (px2, py2))

        # ── controls reminder ──
        ctrl = font_tiny.render("WASD / ↑↓←→  to drive", True, (150,150,150))
        surf.blit(ctrl, (20, HEIGHT - 25))

    def draw_countdown(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        surf.blit(overlay, (0,0))
        if self.countdown > 0:
            txt = font_big.render(str(self.countdown), True, YELLOW)
        else:
            txt = font_big.render("GO!", True, GREEN)
        surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))

    def draw_finish(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,170))
        surf.blit(overlay, (0,0))

        rankings = self.rankings()
        player_pos = next((i+1 for i,c in enumerate(rankings) if c.is_player), 6)

        title_col = GOLD if player_pos == 1 else (SILVER if player_pos == 2 else
                    (BRONZE if player_pos == 3 else RED))
        pos_strs = {1:"1ST PLACE!", 2:"2ND PLACE", 3:"3RD PLACE",
                    4:"4TH PLACE", 5:"5TH PLACE", 6:"6TH PLACE"}
        title = font_big.render(pos_strs.get(player_pos, "FINISHED"), True, title_col)
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        sub = font_med.render("FINAL STANDINGS", True, WHITE)
        surf.blit(sub, (WIDTH//2 - sub.get_width()//2, 170))

        for i, car in enumerate(rankings):
            col = GOLD if i==0 else (SILVER if i==1 else (BRONZE if i==2 else (200,200,200)))
            if car.is_player: col = GREEN
            t = font_med.render(f"{i+1}.  {car.name}", True, col)
            surf.blit(t, (WIDTH//2 - 120, 215 + i*42))

        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000 if self.start_time else 0
        time_txt = font_small.render(f"Your time:  {elapsed:.2f}s", True, (180,220,255))
        surf.blit(time_txt, (WIDTH//2 - time_txt.get_width()//2, 490))

        restart_txt = font_med.render("R  –  Restart     Q  –  Quit", True, (200,200,200))
        surf.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, 540))

# ─── MENU ────────────────────────────────────────────────────────────────────
def draw_menu(surf, selected_diff, selected_laps):
    surf.fill(DARK_GRAY)
    surf.blit(track_surf, (0,0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    surf.blit(overlay, (0,0))

    title = font_big.render("APEX  RACER", True, GOLD)
    surf.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    sub = font_small.render("A top-down racing game", True, (180,180,180))
    surf.blit(sub, (WIDTH//2 - sub.get_width()//2, 158))

    # difficulty
    diff_label = font_med.render("DIFFICULTY", True, WHITE)
    surf.blit(diff_label, (WIDTH//2 - diff_label.get_width()//2, 230))
    diffs = ["Easy", "Normal", "Hard"]
    for i, d in enumerate(diffs):
        col = YELLOW if i == selected_diff else (150,150,150)
        t = font_med.render(d, True, col)
        surf.blit(t, (WIDTH//2 - 160 + i*130, 270))

    # laps
    laps_label = font_med.render("LAPS", True, WHITE)
    surf.blit(laps_label, (WIDTH//2 - laps_label.get_width()//2, 330))
    laps_opts = [1, 2, 3, 5]
    for i, lp in enumerate(laps_opts):
        col = YELLOW if i == selected_laps else (150,150,150)
        t = font_med.render(str(lp), True, col)
        surf.blit(t, (WIDTH//2 - 150 + i*100, 370))

    controls = [
        ("← →",  "Change selection"),
        ("↑ ↓",  "Change category"),
        ("ENTER", "Start Race"),
    ]
    for i, (key, desc) in enumerate(controls):
        k_txt = font_hud.render(key, True, YELLOW)
        d_txt = font_hud.render(desc, True, (180,180,180))
        surf.blit(k_txt, (WIDTH//2 - 120, 450 + i*30))
        surf.blit(d_txt, (WIDTH//2 - 40,  450 + i*30))

    # animated car
    t = pygame.time.get_ticks() / 1000
    car_x = int(WIDTH//2 + math.sin(t*0.8)*200)
    car_y = 620
    dummy = pygame.Rect(car_x - 12, car_y - 20, 24, 40)
    pygame.draw.rect(surf, GREEN, dummy, border_radius=4)
    pygame.draw.rect(surf, BLACK, dummy, 2, border_radius=4)

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
def main():
    diff_map   = [0.80, 1.00, 1.30]
    diff_names = ["Easy", "Normal", "Hard"]
    laps_opts  = [1, 2, 3, 5]

    state        = "menu"
    sel_row      = 0   # 0=difficulty 1=laps
    sel_diff     = 1
    sel_laps_idx = 2

    race = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        sel_row = (sel_row - 1) % 2
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        sel_row = (sel_row + 1) % 2
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if sel_row == 0: sel_diff     = (sel_diff - 1) % 3
                        else:            sel_laps_idx = (sel_laps_idx - 1) % 4
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        if sel_row == 0: sel_diff     = (sel_diff + 1) % 3
                        else:            sel_laps_idx = (sel_laps_idx + 1) % 4
                    if event.key == pygame.K_RETURN:
                        race  = Race(total_laps=laps_opts[sel_laps_idx],
                                     difficulty=diff_map[sel_diff])
                        state = "race"

            elif state == "race":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        race  = Race(total_laps=laps_opts[sel_laps_idx],
                                     difficulty=diff_map[sel_diff])
                        state = "race"
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        state = "menu"
                    if event.key == pygame.K_p:
                        # pause toggle
                        pass

        if state == "menu":
            draw_menu(screen, sel_diff, sel_laps_idx)

        elif state == "race":
            race.update()
            race.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()