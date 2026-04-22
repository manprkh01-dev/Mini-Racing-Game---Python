"""
APEX RACER — Title Screen
Run this file to launch the game.
"""

import pygame
import math
import sys
import os
import subprocess
import random

# ─── INIT ────────────────────────────────────────────────────────────────────
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("APEX RACER")
clock  = pygame.time.Clock()
FPS    = 60

# ─── COLOURS ─────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GOLD       = (255, 215,   0)
GOLD_DIM   = (180, 140,   0)
DARK       = (12,  12,  18)
DARKER     = (8,   8,  14)
ASPHALT    = (50,  52,  55)
GRASS      = (34,  85,  34)
RED        = (220,  40,  40)
GREEN      = (50,  200,  80)
BLUE       = (40,  100, 220)
ORANGE     = (230, 130,  20)
CYAN       = (40,  210, 210)
PINK       = (220,  60, 160)
YELLOW     = (230, 200,  30)
GRAY       = (80,   80,  80)
LIGHT_GRAY = (180, 180, 180)
PANEL_BG   = (20,  20,  30, 210)

# ─── FONTS ───────────────────────────────────────────────────────────────────
font_title  = pygame.font.SysFont("Impact",  96)
font_sub    = pygame.font.SysFont("Impact",  28)
font_btn    = pygame.font.SysFont("Impact",  34)
font_med    = pygame.font.SysFont("Arial",   22)
font_small  = pygame.font.SysFont("Arial",   18)
font_tiny   = pygame.font.SysFont("Consolas",15)

# ─── STAR FIELD ──────────────────────────────────────────────────────────────
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
          random.uniform(0.3, 1.5)) for _ in range(180)]

# ─── MINI TRACK (background decoration) ─────────────────────────────────────
# Scaled-down version of the game track, used as animated BG
MINI_WP = [
    (500, 80), (800, 80), (900, 160), (920, 300), (880, 420),
    (780, 500), (680, 560), (600, 620), (500, 640), (380, 620),
    (260, 570), (160, 490), (100, 380), (90, 260),  (140, 160),
    (240, 90),  (360, 70),
]

def norm(v):
    m = math.hypot(v[0], v[1])
    return (v[0]/m, v[1]/m) if m else (0, 0)

def perp(v):
    return (-v[1], v[0])

def build_polys(wps, hw):
    n  = len(wps)
    inn, out = [], []
    for i in range(n):
        prev = wps[(i-1)%n]; curr = wps[i]; nxt = wps[(i+1)%n]
        d1 = norm((curr[0]-prev[0], curr[1]-prev[1]))
        d2 = norm((nxt[0]-curr[0],  nxt[1]-curr[1]))
        t  = norm((d1[0]+d2[0], d1[1]+d2[1]))
        p  = perp(t)
        inn.append((curr[0]+p[0]*hw, curr[1]+p[1]*hw))
        out.append((curr[0]-p[0]*hw, curr[1]-p[1]*hw))
    return inn, out

INNER_P, OUTER_P = build_polys(MINI_WP, 68)

# Pre-render the background track
bg_surf = pygame.Surface((WIDTH, HEIGHT))
bg_surf.fill(DARKER)
# subtle grid lines
for x in range(0, WIDTH, 40):
    pygame.draw.line(bg_surf, (20, 20, 30), (x, 0), (x, HEIGHT))
for y in range(0, HEIGHT, 40):
    pygame.draw.line(bg_surf, (20, 20, 30), (0, y), (WIDTH, y))
# draw track
pygame.draw.polygon(bg_surf, (30, 32, 35), OUTER_P)
pygame.draw.polygon(bg_surf, DARKER,       INNER_P)
pygame.draw.polygon(bg_surf, (60, 62, 65), OUTER_P, 3)
pygame.draw.polygon(bg_surf, (60, 62, 65), INNER_P, 3)

# ─── ANIMATED CARS ON TRACK ──────────────────────────────────────────────────
class TrackCar:
    """A small car that drives around the mini track on the title screen."""
    def __init__(self, colour, speed, offset):
        self.colour = colour
        self.speed  = speed          # waypoints per second
        self.t      = offset         # current position (float index into MINI_WP)
        self.x      = float(MINI_WP[0][0])
        self.y      = float(MINI_WP[0][1])
        self.angle  = 0.0
        n = len(MINI_WP)

    def update(self, dt):
        n   = len(MINI_WP)
        self.t = (self.t + self.speed * dt) % n
        i0  = int(self.t) % n
        i1  = (i0 + 1) % n
        frac = self.t - int(self.t)
        ax, ay = MINI_WP[i0]
        bx, by = MINI_WP[i1]
        self.x = ax + (bx - ax) * frac
        self.y = ay + (by - ay) * frac
        dx, dy = bx - ax, by - ay
        self.angle = math.degrees(math.atan2(dx, -dy))

    def draw(self, surf, alpha=255):
        rad   = math.radians(self.angle)
        ca, sa = math.cos(rad), math.sin(rad)
        hw, hh = 7, 13

        def rp(cx, cy):
            return (int(ca*cx - sa*cy + self.x),
                    int(sa*cx + ca*cy + self.y))

        body = [rp(-hw,-hh), rp(hw,-hh), rp(hw,hh), rp(-hw,hh)]
        # shadow
        shadow = [(p[0]+2, p[1]+2) for p in body]
        pygame.draw.polygon(surf, (0,0,0), shadow)
        pygame.draw.polygon(surf, self.colour, body)
        pygame.draw.polygon(surf, BLACK, body, 1)
        # windshield
        ws = [rp(-hw+2, -hh+2), rp(hw-2, -hh+2),
              rp(hw-2, -hh+7),  rp(-hw+2, -hh+7)]
        pygame.draw.polygon(surf, (160, 200, 240), ws)

demo_cars = [
    TrackCar(GREEN,  1.4, 0.0),
    TrackCar(RED,    1.3, 4.0),
    TrackCar(BLUE,   1.25, 8.5),
    TrackCar(ORANGE, 1.35, 12.0),
    TrackCar(CYAN,   1.2, 15.5),
]

# ─── BUTTON ──────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, cx, cy, w, h, label, colour=GOLD, text_col=BLACK):
        self.rect      = pygame.Rect(cx - w//2, cy - h//2, w, h)
        self.label     = label
        self.colour    = colour
        self.text_col  = text_col
        self.hovered   = False
        self._anim     = 0.0   # 0..1 hover animation

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self._anim += (target - self._anim) * 0.18

    def draw(self, surf):
        a   = self._anim
        # glow effect
        if a > 0.05:
            glow = pygame.Surface((self.rect.w + 20, self.rect.h + 20), pygame.SRCALPHA)
            gc   = (*self.colour, int(60 * a))
            pygame.draw.rect(glow, gc, (0, 0, self.rect.w+20, self.rect.h+20), border_radius=14)
            surf.blit(glow, (self.rect.x-10, self.rect.y-10))

        # body
        scale  = 1.0 + a * 0.04
        w2     = int(self.rect.w * scale)
        h2     = int(self.rect.h * scale)
        rx     = self.rect.centerx - w2//2
        ry     = self.rect.centery - h2//2
        r      = pygame.Rect(rx, ry, w2, h2)

        # base fill (dark + tinted)
        base_col = (
            int(18 + self.colour[0] * 0.12 * a),
            int(18 + self.colour[1] * 0.12 * a),
            int(28 + self.colour[2] * 0.12 * a),
        )
        pygame.draw.rect(surf, base_col, r, border_radius=10)

        # border
        border_col = tuple(int(c * (0.5 + 0.5*a)) for c in self.colour)
        pygame.draw.rect(surf, border_col, r, 2, border_radius=10)

        # top sheen
        sheen = pygame.Surface((r.w, r.h//3), pygame.SRCALPHA)
        sheen.fill((255, 255, 255, int(18 + 18*a)))
        surf.blit(sheen, (r.x, r.y))

        # label
        txt_col = tuple(int(self.text_col[i]*(1-a) + self.colour[i]*a) for i in range(3))
        lbl     = font_btn.render(self.label, True, txt_col)
        surf.blit(lbl, (r.centerx - lbl.get_width()//2,
                        r.centery - lbl.get_height()//2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))

# ─── HELP SCREEN ─────────────────────────────────────────────────────────────
class HelpScreen:
    def __init__(self):
        self.visible = False
        self.btn_back = Button(WIDTH//2, 610, 260, 52, "◀  BACK TO MENU", GOLD, BLACK)
        self._slide   = 0.0   # 0=hidden, 1=shown (animated)

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def update(self, mouse_pos, events):
        target = 1.0 if self.visible else 0.0
        self._slide += (target - self._slide) * 0.15
        self.btn_back.update(mouse_pos)
        for ev in events:
            if self.btn_back.clicked(ev) or (
               ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                self.hide()
                return "menu"
        return None

    def draw(self, surf):
        if self._slide < 0.01:
            return

        alpha = int(255 * self._slide)
        panel = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        panel.fill((8, 8, 18, min(230, alpha)))
        surf.blit(panel, (0, 0))

        # Title
        t  = font_title.render("HOW TO PLAY", True, GOLD)
        ts = pygame.transform.scale(t, (int(t.get_width()*self._slide),
                                        int(t.get_height()*self._slide)))
        surf.blit(ts, (WIDTH//2 - ts.get_width()//2, 30))

        sections = [
            ("🎮  CONTROLS", [
                ("W  /  ↑",      "Accelerate"),
                ("S  /  ↓",      "Brake  /  Reverse"),
                ("A  /  ←",      "Steer Left"),
                ("D  /  →",      "Steer Right"),
                ("R",            "Restart Race"),
                ("Q  /  ESC",    "Back to Menu"),
            ]),
            ("🏁  OBJECTIVE", [
                ("",  "Finish all laps before the AI opponents."),
                ("",  "Stay on the asphalt — grass slows you down!"),
                ("",  "Watch out for oil slicks: they spin you out."),
                ("",  "First to cross the finish line wins."),
            ]),
            ("⚙️  SETTINGS", [
                ("Difficulty",  "Easy / Normal / Hard — changes AI speed & aggression."),
                ("Laps",        "Choose 1, 2, 3 or 5 laps per race."),
            ]),
            ("🏆  STANDINGS", [
                ("",  "Live position board shown during the race."),
                ("",  "Gold = 1st · Silver = 2nd · Bronze = 3rd"),
            ]),
        ]

        col_colours = {
            "🎮  CONTROLS":  CYAN,
            "🏁  OBJECTIVE": GREEN,
            "⚙️  SETTINGS":  ORANGE,
            "🏆  STANDINGS": GOLD,
        }

        # Layout: 2 columns x 2 rows
        positions = [(80, 140), (530, 140), (80, 380), (530, 380)]
        for idx, (heading, items) in enumerate(sections):
            if idx >= len(positions): break
            px, py = positions[idx]
            col    = col_colours.get(heading, WHITE)

            # section card
            card = pygame.Surface((410, 210), pygame.SRCALPHA)
            pygame.draw.rect(card, (255,255,255,10), (0,0,410,210), border_radius=10)
            pygame.draw.rect(card, (*col, 80),       (0,0,410,210), 2, border_radius=10)
            surf.blit(card, (px-10, py-10))

            h_lbl = font_sub.render(heading, True, col)
            surf.blit(h_lbl, (px, py))
            for j, (key, desc) in enumerate(items):
                y2 = py + 38 + j*28
                if key:
                    k_lbl = font_small.render(key, True, YELLOW)
                    surf.blit(k_lbl, (px + 10, y2))
                    d_lbl = font_small.render(desc, True, LIGHT_GRAY)
                    surf.blit(d_lbl, (px + 160, y2))
                else:
                    d_lbl = font_small.render(f"•  {desc}", True, LIGHT_GRAY)
                    surf.blit(d_lbl, (px + 10, y2))

        self.btn_back.draw(surf)

# ─── TITLE SCREEN ────────────────────────────────────────────────────────────
class TitleScreen:
    def __init__(self):
        self.btn_play  = Button(WIDTH//2, 430, 320, 60, "▶   PLAY RACE",   GREEN,      BLACK)
        self.btn_help  = Button(WIDTH//2, 510, 320, 52, "?   HOW TO PLAY", CYAN,       BLACK)
        self.btn_quit  = Button(WIDTH//2, 585, 320, 52, "✕   EXIT GAME",   (180,60,60),(255,200,200))
        self.help      = HelpScreen()
        self._t        = 0.0
        self._logo_y   = -120.0   # slides down on entry
        self._btn_alpha= 0.0      # fade-in buttons

    def update(self, dt, events):
        self._t         += dt
        self._logo_y    = min(60.0,  self._logo_y + dt * 280)
        self._btn_alpha = min(1.0,   self._btn_alpha + dt * 1.2)

        mouse = pygame.mouse.get_pos()

        # update demo cars
        for c in demo_cars:
            c.update(dt)

        # update stars
        for i, (sx, sy, spd) in enumerate(stars):
            stars[i] = ((sx - spd * 0.3) % WIDTH, sy, spd)

        if self.help.visible:
            result = self.help.update(mouse, events)
            if result == "menu":
                self.help.hide()
            return None

        self.btn_play.update(mouse)
        self.btn_help.update(mouse)
        self.btn_quit.update(mouse)

        for ev in events:
            if self.btn_play.clicked(ev) or (
               ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN):
                return "play"
            if self.btn_help.clicked(ev) or (
               ev.type == pygame.KEYDOWN and ev.key == pygame.K_h):
                self.help.show()
            if self.btn_quit.clicked(ev) or (
               ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                return "quit"

        return None

    def draw(self, surf):
        # ── background ──
        surf.blit(bg_surf, (0, 0))

        # stars
        for sx, sy, spd in stars:
            r = max(1, int(spd * 0.8))
            brightness = int(80 + spd * 80)
            pygame.draw.circle(surf, (brightness, brightness, brightness+20),
                               (int(sx), int(sy)), r)

        # demo cars on track
        for c in demo_cars:
            c.draw(surf)

        # dark gradient overlay (bottom heavy so track is visible at top)
        grad = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = int(80 + 140 * (y / HEIGHT))
            pygame.draw.line(grad, (8, 8, 18, alpha), (0, y), (WIDTH, y))
        surf.blit(grad, (0, 0))

        # ── speed lines ──
        t = self._t
        for i in range(8):
            angle = (i * 45 + t * 15) % 360
            rad   = math.radians(angle)
            length = 120 + 40 * math.sin(t * 2 + i)
            cx, cy = WIDTH//2, int(self._logo_y) + 50
            x1 = cx + math.cos(rad) * 160
            y1 = cy + math.sin(rad) * 60
            x2 = x1 + math.cos(rad) * length
            y2 = y1 + math.sin(rad) * length * 0.4
            alpha = int(30 + 20 * math.sin(t * 3 + i))
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(s, (255, 215, 0, alpha), (int(x1), int(y1)),
                             (int(x2), int(y2)), 2)
            surf.blit(s, (0, 0))

        # ── APEX RACER logo ──
        logo_y = int(self._logo_y)

        # Shadow
        shadow = font_title.render("APEX  RACER", True, (0, 0, 0))
        surf.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 4, logo_y + 4))

        # Gradient title: gold → white shimmer
        base_surf = font_title.render("APEX  RACER", True, GOLD)
        shim_pos  = int((self._t * 80) % (base_surf.get_width() + 200)) - 100
        shim      = pygame.Surface(base_surf.get_size(), pygame.SRCALPHA)
        shim.blit(base_surf, (0, 0))
        for sx in range(shim_pos - 30, shim_pos + 30):
            if 0 <= sx < shim.get_width():
                fade = 1 - abs(sx - shim_pos) / 30
                pygame.draw.line(shim, (255, 255, 255, int(100 * fade)),
                                 (sx, 0), (sx, shim.get_height()))
        surf.blit(shim, (WIDTH//2 - shim.get_width()//2, logo_y))

        # underline bar
        bar_w = base_surf.get_width() + 20
        bar_x = WIDTH//2 - bar_w//2
        pygame.draw.rect(surf, GOLD, (bar_x, logo_y + 100, bar_w, 4), border_radius=2)
        pygame.draw.rect(surf, WHITE, (bar_x, logo_y + 100, int(bar_w * 0.4), 4),
                         border_radius=2)

        # subtitle
        sub = font_sub.render("TOP-DOWN  RACING  —  BEAT THE AI  —  CLAIM POLE POSITION",
                               True, (160, 160, 180))
        surf.blit(sub, (WIDTH//2 - sub.get_width()//2, logo_y + 116))

        # ── buttons ──
        if self._btn_alpha > 0.02:
            btn_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.btn_play.draw(btn_surf)
            self.btn_help.draw(btn_surf)
            self.btn_quit.draw(btn_surf)
            btn_surf.set_alpha(int(self._btn_alpha * 255))
            surf.blit(btn_surf, (0, 0))

        # ── version / credit footer ──
        ver = font_tiny.render("v1.0  •  Built with Python & Pygame  •  APEX RACER", True, (60, 60, 80))
        surf.blit(ver, (WIDTH//2 - ver.get_width()//2, HEIGHT - 22))

        # keyboard hint
        hint = font_tiny.render("ENTER to Play  •  H for Help  •  ESC to Quit",
                                  True, (70, 70, 90))
        surf.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 42))

        # ── help overlay on top ──
        self.help.draw(surf)


# ─── LAUNCH MAIN GAME ────────────────────────────────────────────────────────
def launch_game():
    """
    Launch main.py in the same process using importlib so we keep the
    same window and don't need a second Python process.
    """
    import importlib.util, importlib.machinery

    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_path  = os.path.join(script_dir, "main.py")

    if not os.path.exists(main_path):
        # Fallback: try same directory
        main_path = "main.py"

    spec   = importlib.util.spec_from_file_location("main_game", main_path)
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
        # main.py defines main() — call it
        module.main(return_to_title=True)
    except SystemExit:
        pass
    except Exception as e:
        # Show error on screen
        screen.fill((20, 0, 0))
        err = font_med.render(f"Error launching main.py: {e}", True, RED)
        screen.blit(err, (40, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)


# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def run_title():
    title = TitleScreen()

    while True:
        dt     = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        result = title.update(dt, events)

        if result == "play":
            launch_game()
            # When main.py returns (player quit back), re-init title
            title = TitleScreen()

        elif result == "quit":
            pygame.quit()
            sys.exit()

        title.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    run_title()