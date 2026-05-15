"""
Fighter Jet Cursor Follower v7.0
Physics exactly matching index.html hamster:
  - angle tracks atan2(dy,dx) to cursor every frame
  - angle += angleDiff * clamp(turnSpeed*dt, 0, 0.35)
  - speed accel/decel, velocity lerp with smoothing=0.08
  - FULL ROTATION: jet pixels rotated around centre every frame
  - 1-second cursor delay
  - 20-30% explosion on catch, else circles cursor
  - Respawn from random screen edge
ESC or middle-click to quit.
"""
import tkinter as tk
import math, time, random

# ── Configuration ─────────────────────────────────────────────────────────────
CONFIG = {
    'canvas_size': 400,
    'bg_color': '#010203',
    'max_particles': 40,
    'jet_scale': 1.0,
    'cursor_delay': 0.15, # Reduced delay for faster reaction
    'max_speed': 320.0,   # Slightly faster
    'smoothing': 0.05,    # More responsive
    'catch_dist': 22,
    'circle_radius': 52,
    'circle_speed': 1.6,
    'explosion_chance': (0.20, 0.30),
    'fps_interval': 16, # ms
    'shoot_dist': 280,
    'shoot_rate': 0.12, # seconds between shots
    'bullet_speed': 800.0,
    'max_bullets': 15,
    'impact_duration': 0.3,
    'bullets_per_burst': 25,
    'missile_speed': 550.0,
    'missile_turn_spd': 8.0,
    'missile_count': 2,
    'afterburner_threshold': 600.0,
    'roll_threshold': 1.2, # radians
    'roll_speed': 10.0,
}

CW = CH = CONFIG['canvas_size']
CX = CY = CW // 2
BG = CONFIG['bg_color']
MAX_PARTICLES = CONFIG['max_particles']

# ── Jet shape defined as filled polygons (pointing RIGHT, centre=0,0) ────────
# Coordinates in jet-local space. Nose = +x, tail = -x, wings = ±y.
# Scale: ~24px long, ~22px wide tip-to-tip

PAL = {
    'fuse_main':   '#8898A8',
    'fuse_hi':     '#AAB8C4',
    'fuse_dark':   '#607080',
    'wing_main':   '#7A8E98',
    'wing_edge':   '#5A6E78',
    'tail_fin':    '#4A5E68',
    'cockpit':     '#1565C0',
    'cockpit_hi':  '#64B5F6',
    'stripe':      '#E53935',
    'engine':      '#2E3D45',
    'nozzle':      '#1A2830',
    'flame1':      '#FFF176',
    'flame2':      '#FFB300',
    'flame3':      '#FF6D00',
}

# Each shape: (color_key, [(x,y), ...] polygon)
JET_SHAPES = [
    # ── Main fuselage ─────────────────────────────────────────────
    ('fuse_dark',  [(-22,-2),(-22,2),(-10,3),(-4,3),(14,2),(20,1),(22,0),(20,-1),(14,-2),(-4,-3),(-10,-3)]),
    ('fuse_main',  [(-18,-2),(-18,2),(-8,2.5),(10,2),(18,1),(20,0),(18,-1),(10,-2),(-8,-2.5)]),
    ('fuse_hi',    [(-10,-1.5),(-10,1.5),(5,1.5),(14,0.5),(16,0),(14,-0.5),(5,-1.5)]),

    # ── Swept wings (large, angled back) ──────────────────────────
    ('wing_edge',  [(-4,-3),(-18,-3),(-22,-14),(-14,-14),(-2,-4)]),      # upper wing outer
    ('wing_main',  [(-4,-3),(-16,-3),(-20,-12),(-12,-12),(-2,-4)]),      # upper wing inner
    ('wing_edge',  [(-4, 3),(-18, 3),(-22, 14),(-14, 14),(-2, 4)]),     # lower wing outer
    ('wing_main',  [(-4, 3),(-16, 3),(-20, 12),(-12, 12),(-2, 4)]),     # lower wing inner

    # ── Tail fins (small, swept) ──────────────────────────────────
    ('tail_fin',   [(-18,-3),(-22,-3),(-24,-8),(-19,-8),(-17,-4)]),      # upper tail
    ('tail_fin',   [(-18, 3),(-22, 3),(-24, 8),(-19, 8),(-17, 4)]),     # lower tail

    # ── Engine nozzles ────────────────────────────────────────────
    ('nozzle',     [(-22,-3),(-22,-1.5),(-26,-1.5),(-26,-3)]),
    ('nozzle',     [(-22, 3),(-22, 1.5),(-26, 1.5),(-26, 3)]),

    # ── Cockpit canopy ────────────────────────────────────────────
    ('cockpit',    [(8,-2),(8,2),(13,1.5),(15,0),(13,-1.5)]),
    ('cockpit_hi', [(9,-1),(9,1),(12,0.8),(13,0),(12,-0.8)]),

    # ── Red accent stripe ─────────────────────────────────────────
    ('stripe',     [(2,-1.5),(2,1.5),(8,1.5),(8,-1.5)]),
]

# Flame shapes (drawn at tail when moving)
FLAME_SHAPES_ALL = [
    # frame 0
    [('flame3', [(-26,-2.5),(-26,2.5),(-32,1.5),(-34,0),(-32,-1.5)]),
     ('flame2', [(-26,-2),  (-26,2),  (-30,1),  (-32,0),(-30,-1)]),
     ('flame1', [(-26,-1),  (-26,1),  (-29,0)])],
    # frame 1
    [('flame3', [(-26,-3),  (-26,3),  (-31,2),  (-35,0),(-31,-2)]),
     ('flame2', [(-26,-2),  (-26,2),  (-29,1.5),(-33,0),(-29,-1.5)]),
     ('flame1', [(-26,-1),  (-26,1),  (-30,0)])],
    # frame 2
    [('flame3', [(-26,-2),  (-26,2),  (-30,1),  (-33,0),(-30,-1)]),
     ('flame2', [(-26,-1.5),(-26,1.5),(-29,1),  (-31,0),(-29,-1)]),
     ('flame1', [(-26,-0.8),(-26,0.8),(-28.5,0)])],
    # frame 3
    [('flame3', [(-26,-3.5),(-26,3.5),(-33,2.5),(-37,0),(-33,-2.5)]),
     ('flame2', [(-26,-2.5),(-26,2.5),(-31,1.5),(-35,0),(-31,-1.5)]),
     ('flame1', [(-26,-1.5),(-26,1.5),(-32,0)])],
]

# Explosion: expanding rings drawn as ovals
EXP_FRAMES = [
    [(8,  '#FFFFFF', 1.0), (5,  '#FFFF88', 0.9)],
    [(14, '#FFDD00', 1.0), (10, '#FF8800', 0.8), (6,  '#FFFFFF', 0.7)],
    [(20, '#FF8800', 0.9), (15, '#FF4400', 0.7), (8,  '#FFCC00', 1.0)],
    [(26, '#FF4400', 0.8), (20, '#CC2200', 0.6), (12, '#FF8800', 0.9)],
    [(32, '#882200', 0.6), (26, '#FF4400', 0.5), (18, '#FF8800', 0.4)],
    [(38, '#441100', 0.3), (30, '#882200', 0.2)],
]


def rotate_pt(x, y, cos_a, sin_a):
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a


class JetFollower:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', BG)
        self.root.configure(bg=BG)

        # Multi-monitor support: Get full virtual desktop dimensions
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        try:
            v_width = self.root.winfo_vrootwidth()
            v_height = self.root.winfo_vrootheight()
            self.sw = max(self.sw, v_width)
            self.sh = max(self.sh, v_height)
            self.sx = self.root.winfo_vrootx()
            self.sy = self.root.winfo_vrooty()
        except:
            self.sx = 0
            self.sy = 0

        self.cv = tk.Canvas(self.root, width=CW, height=CH,
                            bg=BG, highlightthickness=0, bd=0)
        self.cv.pack()

        # Canvas items — persistent items updated via coords()
        self._jet_items = []
        self._flame_items = []
        self._exp_items = []
        self._part_items = []
        self._init_canvas_items()

        # Physics state
        self.x = float(self.sw // 2)
        self.y = float(self.sh // 2)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 0.0
        self.angle = 0.0   # radians, 0=right, matches HTML atan2 convention

        # Particles state: list of [lx, ly, lvx, lvy, life, max_life]
        self.particles = []
        
        # Bullets state: list of [sx, sy, svx, svy, target_pos]
        self.bullets = []
        self.last_shot_t = 0
        
        # Impacts state: list of [sx, sy, life]
        self.impacts = []
        
        # Weapons state
        self.weapon_mode = 'bullets' # 'bullets' | 'missiles'
        self.burst_count = 0
        self.missiles = [] # list of [sx, sy, angle, vx, vy]

        # Maneuver state
        self.roll_angle = 0.0
        self.is_afterburner = False

        # State machine
        self.state = 'flying'   # flying | circling | exploding | dead
        self.fidx  = 0
        self.facc  = 0.0
        self.circle_ang = 0.0
        self.exp_frame  = 0
        self.exp_acc    = 0.0
        self.exp_chance = random.uniform(*CONFIG['explosion_chance'])
        self.respawn_t  = 0.0

        self._cursor_history = []
        self.last_t = time.perf_counter()

        self.root.bind('<Escape>',   lambda e: self.root.destroy())
        self.root.bind('<Button-2>', lambda e: self.root.destroy())

        self._tick()
        self.root.mainloop()

    def _init_canvas_items(self):
        # Create particles (initially hidden)
        for _ in range(MAX_PARTICLES):
            item = self.cv.create_oval(0,0,0,0, fill='#555555', outline='', state='hidden')
            self._part_items.append(item)

        # Create flames (initially hidden)
        # We create enough for all frames, or just update one set? 
        # Updating one set is easier.
        for _ in range(3): # Max 3 polys per flame frame
            item = self.cv.create_polygon([0,0,0,0,0,0], fill='', outline='', state='hidden')
            self._flame_items.append(item)
        
        # Create jet shapes
        for ckey, _ in JET_SHAPES:
            item = self.cv.create_polygon([0,0,0,0,0,0], fill=PAL[ckey], outline='', state='normal')
            self._jet_items.append(item)

        # Create explosion rings
        for _ in range(3): # Max 3 rings per exp frame
            item = self.cv.create_oval(0,0,0,0, fill='', outline='', state='hidden')
            self._exp_items.append(item)

        # Create bullet items (lines for trails)
        self._bullet_items = []
        for _ in range(CONFIG['max_bullets']):
            item = self.cv.create_line(0,0,0,0, fill='#FFF176', width=2, state='hidden')
            self._bullet_items.append(item)

        # Create impact items (small ovals)
        self._impact_items = []
        for _ in range(CONFIG['max_bullets']):
            item = self.cv.create_oval(0,0,0,0, fill='#FF6D00', outline='', state='hidden')
            self._impact_items.append(item)
            
        # Create missile items
        self._missile_items = []
        for _ in range(CONFIG['missile_count']):
            item = self.cv.create_polygon([0,0,0,0,0,0], fill='#E53935', outline='#000000', state='hidden')
            self._missile_items.append(item)

    # ── Cursor delay buffer ───────────────────────────────────────────────────
    def _poll_cursor(self, now):
        cx, cy = self.root.winfo_pointerxy()
        self._cursor_history.append((now, cx, cy))
        # purge old
        cutoff = now - CONFIG['cursor_delay'] - 0.5
        while self._cursor_history and self._cursor_history[0][0] < cutoff:
            self._cursor_history.pop(0)
        
        # find entry closest to (now - CONFIG['cursor_delay'])
        target_t = now - CONFIG['cursor_delay']
        best = self._cursor_history[0]
        # Optimized search: since history is sorted, we can stop early or use binary search
        # For small buffers, linear is fine, but let's at least stop early.
        for e in self._cursor_history:
            if abs(e[0] - target_t) < abs(best[0] - target_t):
                best = e
            elif e[0] > target_t: # Getting further away
                break
        return (cx, cy), (best[1], best[2])

    # ── Spawn from random screen edge ─────────────────────────────────────────
    def _respawn(self):
        sw, sh = self.sw, self.sh
        sx, sy = self.sx, self.sy
        edge = random.choice(['top','bottom','left','right'])
        if edge == 'top':      self.x, self.y = random.uniform(sx+50, sx+sw-50), sy - 30.0
        elif edge == 'bottom': self.x, self.y = random.uniform(sx+50, sx+sw-50), sy + sh + 30.0
        elif edge == 'left':   self.x, self.y = sx - 30.0, random.uniform(sy+50, sy+sh-50)
        else:                  self.x, self.y = sx + sw + 30.0, random.uniform(sy+50, sy+sh-50)
        self.vx = self.vy = self.speed = 0.0
        self.angle = 0.0
        self.state = 'flying'
        self.fidx  = 0
        self.facc  = 0.0
        self.exp_chance = random.uniform(*CONFIG['explosion_chance'])
        # Reset item states
        for item in self._exp_items: self.cv.itemconfig(item, state='hidden')
        for item in self._jet_items: self.cv.itemconfig(item, state='normal')

    # ── Draw jet at current angle ─────────────────────────────────────────────
    def _draw_jet(self, show_flame=True):
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        # Roll perspective: flatten Y axis based on roll angle
        roll_scale = math.cos(self.roll_angle)

        def proj(lx, ly):
            # Apply roll scale before rotation
            ly_rolled = ly * roll_scale
            rx, ry = rotate_pt(lx, ly_rolled, cos_a, sin_a)
            return CX + rx, CY + ry

        def poly_coords(pts):
            flat = []
            for lx, ly in pts:
                px, py = proj(lx, ly)
                flat += [px, py]
            return flat

        # Update particles (World -> Canvas)
        wx, wy = self.x - CX, self.y - CY
        for i, item in enumerate(self._part_items):
            if i < len(self.particles):
                sx, sy, _, _, life, max_life = self.particles[i]
                px, py = sx - wx, sy - wy
                r = 3.5 * (life / max_life)
                self.cv.coords(item, px-r, py-r, px+r, py+r)
                # Fade color: white -> grey
                ratio = life / max_life
                c_val = int(50 + 205 * ratio)
                color = f'#{c_val:02x}{c_val:02x}{c_val:02x}'
                self.cv.itemconfig(item, fill=color, state='normal')
            else:
                self.cv.itemconfig(item, state='hidden')

        # Update bullets (World -> Canvas)
        for i, item in enumerate(self._bullet_items):
            if i < len(self.bullets):
                sx, sy, svx, svy, tx, ty = self.bullets[i]
                px, py = sx - wx, sy - wy
                # Draw a trail line (current pos back to slightly earlier pos)
                tail_len = 15
                self.cv.coords(item, px, py, px - svx*0.02, py - svy*0.02)
                self.cv.itemconfig(item, state='normal')
            else:
                self.cv.itemconfig(item, state='hidden')

        # Update impacts (World -> Canvas)
        for i, item in enumerate(self._impact_items):
            if i < len(self.impacts):
                sx, sy, life = self.impacts[i]
                px, py = sx - wx, sy - wy
                r = 8 * (1.0 - life/CONFIG['impact_duration'])
                self.cv.coords(item, px-r, py-r, px+r, py+r)
                # Flickering orange/white
                color = random.choice(['#FF6D00', '#FFF176', '#FFFFFF'])
                self.cv.itemconfig(item, fill=color, state='normal')
            else:
                self.cv.itemconfig(item, state='hidden')

        # Update missiles (World -> Canvas)
        for i, item in enumerate(self._missile_items):
            if i < len(self.missiles):
                sx, sy, ang, _, _ = self.missiles[i]
                px, py = sx - wx, sy - wy
                # Missile shape: small triangle
                ma = ang
                pts = [rotate_pt(8, 0, math.cos(ma), math.sin(ma)),
                       rotate_pt(-4, 4, math.cos(ma), math.sin(ma)),
                       rotate_pt(-4, -4, math.cos(ma), math.sin(ma))]
                poly_pts = []
                for lx, ly in pts:
                    poly_pts += [px + lx, py + ly]
                self.cv.coords(item, *poly_pts)
                self.cv.itemconfig(item, state='normal')
            else:
                self.cv.itemconfig(item, state='hidden')

        # Update flames
        flame_shapes = FLAME_SHAPES_ALL[self.fidx] if show_flame else []
        for i, item in enumerate(self._flame_items):
            if i < len(flame_shapes):
                ckey, pts = flame_shapes[i]
                
                # Afterburner effect: scale flames and change color
                if self.is_afterburner:
                    # Scale pts from (-26, 0) origin
                    scaled_pts = []
                    for lx, ly in pts:
                        dx = lx - (-26)
                        dy = ly - 0
                        scaled_pts.append((-26 + dx * 2.0, dy * 1.5))
                    f_coords = poly_coords(scaled_pts)
                    f_fill = '#64B5F6' # Blue afterburner core
                else:
                    f_coords = poly_coords(pts)
                    f_fill = PAL[ckey]
                
                self.cv.coords(item, *f_coords)
                self.cv.itemconfig(item, fill=f_fill, state='normal')
            else:
                self.cv.itemconfig(item, state='hidden')

        # Update jet shapes
        for i, item in enumerate(self._jet_items):
            _, pts = JET_SHAPES[i]
            self.cv.coords(item, *poly_coords(pts))
            self.cv.itemconfig(item, state='normal')

    def _draw_explosion(self):
        if self.exp_frame >= len(EXP_FRAMES):
            for item in self._exp_items: self.cv.itemconfig(item, state='hidden')
            return
        
        # Hide jet and flames
        for item in self._jet_items: self.cv.itemconfig(item, state='hidden')
        for item in self._flame_items: self.cv.itemconfig(item, state='hidden')

        frames = EXP_FRAMES[self.exp_frame]
        for i, item in enumerate(self._exp_items):
            if i < len(frames):
                radius, color, alpha = frames[i]
                r = radius
                self.cv.coords(item, CX-r, CY-r, CX+r, CY+r)
                self.cv.itemconfig(item, fill=color, state='normal')
            else:
                self.cv.itemconfig(item, state='hidden')

    # ── Move window so jet centre = (self.x, self.y) on screen ───────────────
    def _move_window(self):
        wx = int(self.x - CX)
        wy = int(self.y - CY)
        # Allow window to go partially off-screen so jet center can reach the edge
        # We only clamp to ensure it doesn't drift completely into the void, 
        # but wide enough to cover all monitors.
        self.root.geometry(f'{CW}x{CH}+{wx}+{wy}')

    # ── Main tick ─────────────────────────────────────────────────────────────
    def _tick(self):
        now = time.perf_counter()
        dt  = min(now - self.last_t, 0.05)
        self.last_t = now

        # Update particles (WORLD space)
        new_particles = []
        for p in self.particles:
            sx, sy, svx, svy, life, max_life = p
            life -= dt
            if life > 0:
                sx += svx * dt
                sy += svy * dt
                new_particles.append([sx, sy, svx, svy, life, max_life])
        self.particles = new_particles

        # Update bullets (WORLD space)
        new_bullets = []
        for b in self.bullets:
            sx, sy, svx, svy, tx, ty = b
            dist_to_target = math.hypot(tx - sx, ty - sy)
            if dist_to_target < 20: # Impact!
                self.impacts.append([tx, ty, CONFIG['impact_duration']])
            else:
                sx += svx * dt
                sy += svy * dt
                new_bullets.append([sx, sy, svx, svy, tx, ty])
        self.bullets = new_bullets

        # Update impacts
        new_impacts = []
        for imp in self.impacts:
            sx, sy, life = imp
            life -= dt
            if life > 0:
                new_impacts.append([sx, sy, life])
        self.impacts = new_impacts

        # Update missiles (WORLD space with homing)
        new_missiles = []
        real_cx, real_cy = self.root.winfo_pointerxy()
        for m in self.missiles:
            sx, sy, ang, vx, vy = m
            # Homing logic
            target_ang = math.atan2(real_cy - sy, real_cx - sx)
            adiff = target_ang - ang
            while adiff >  math.pi: adiff -= 2*math.pi
            while adiff < -math.pi: adiff += 2*math.pi
            
            ang += adiff * min(CONFIG['missile_turn_spd'] * dt, 0.4)
            vx = math.cos(ang) * CONFIG['missile_speed']
            vy = math.sin(ang) * CONFIG['missile_speed']
            
            sx += vx * dt
            sy += vy * dt
            
            # Smoke trail for missile
            if random.random() < 0.5:
                self.particles.append([sx, sy, -vx*0.2, -vy*0.2, 0.5, 0.5])
            
            # Check impact
            if math.hypot(real_cx - sx, real_cy - sy) < 25:
                # Big explosion impact
                for _ in range(5):
                    self.impacts.append([sx + random.uniform(-10,10), 
                                         sy + random.uniform(-10,10), 
                                         CONFIG['impact_duration'] * 2])
            else:
                new_missiles.append([sx, sy, ang, vx, vy])
        
        self.missiles = new_missiles
        if self.weapon_mode == 'missiles' and not self.missiles:
            self.weapon_mode = 'bullets'
            self.burst_count = 0

        # ── DEAD ─────────────────────────────────────────────────────────────
        if self.state == 'dead':
            self.root.geometry(f'{CW}x{CH}+-300+-300')
            if now >= self.respawn_t:
                self._respawn()
            self.root.after(CONFIG['fps_interval'], self._tick)
            return

        # ── EXPLODING ────────────────────────────────────────────────────────
        if self.state == 'exploding':
            self._draw_explosion()
            self._move_window()
            self.exp_acc += dt * 12.0
            if self.exp_acc >= 1.0:
                self.exp_acc -= 1.0
                self.exp_frame += 1
                if self.exp_frame >= len(EXP_FRAMES):
                    self.state    = 'dead'
                    self.respawn_t = now + random.uniform(0.3, 1.0)
            self.root.after(CONFIG['fps_interval'], self._tick)
            return

        # ── Poll cursor ───────────────────────────────────────────────────────
        (real_cx, real_cy), (del_cx, del_cy) = self._poll_cursor(now)

        # Distances
        dx_real = real_cx - self.x
        dy_real = real_cy - self.y
        dist_real = math.hypot(dx_real, dy_real)

        dx_del = del_cx - self.x
        dy_del = del_cy - self.y
        dist_del = math.hypot(dx_del, dy_del)

        # Shooting logic
        if self.state in ('flying', 'circling') and dist_real < CONFIG['shoot_dist']:
            if self.weapon_mode == 'bullets':
                if now - self.last_shot_t > CONFIG['shoot_rate']:
                    self.last_shot_t = now
                    # Fire from nose
                    cos_a = math.cos(self.angle)
                    sin_a = math.sin(self.angle)
                    nx, ny = rotate_pt(22, 0, cos_a, sin_a)
                    bx, by = self.x + nx, self.y + ny
                    
                    # Bullet velocity toward real cursor
                    bang = math.atan2(real_cy - by, real_cx - bx)
                    bspeed = CONFIG['bullet_speed']
                    self.bullets.append([bx, by, math.cos(bang)*bspeed, math.sin(bang)*bspeed, real_cx, real_cy])
                    if len(self.bullets) > CONFIG['max_bullets']:
                        self.bullets.pop(0)
                        
                    self.burst_count += 1
                    if self.burst_count >= CONFIG['bullets_per_burst']:
                        self.weapon_mode = 'missiles'
                        # Fire 2 missiles from wings
                        for side in [-1, 1]:
                            # Wing tip world pos
                            wx, wy = rotate_pt(-10, side*18, cos_a, sin_a)
                            self.missiles.append([self.x + wx, self.y + wy, self.angle, 
                                                 math.cos(self.angle)*100, math.sin(self.angle)*100])
            # (Missiles fire automatically once added to self.missiles)

        # ── CIRCLING ─────────────────────────────────────────────────────────
        if self.state == 'circling':
            if dist_real > CONFIG['circle_radius'] * 2.8:
                self.state = 'flying'
            else:
                # Orbit target point
                self.circle_ang += CONFIG['circle_speed'] * dt
                tx = real_cx + math.cos(self.circle_ang) * CONFIG['circle_radius']
                ty = real_cy + math.sin(self.circle_ang) * CONFIG['circle_radius']

                dx = tx - self.x;  dy = ty - self.y
                target_angle = math.atan2(dy, dx)
                adiff = target_angle - self.angle
                while adiff >  math.pi: adiff -= 2*math.pi
                while adiff < -math.pi: adiff += 2*math.pi
                dist_orb = math.hypot(dx, dy)
                turn_spd = 6.0 + (dist_orb / 150) * 4
                self.angle += adiff * max(0, min(turn_spd * dt, 0.45))

                target_speed = CONFIG['max_speed'] * 0.6
                if self.speed < target_speed:
                    self.speed = min(self.speed + 300*dt, target_speed)
                else:
                    self.speed = max(self.speed - 400*dt, target_speed)

                t_lerp = 1.0 - (CONFIG['smoothing'] ** dt)
                tvx = math.cos(self.angle) * self.speed
                tvy = math.sin(self.angle) * self.speed
                self.vx += (tvx - self.vx) * t_lerp
                self.vy += (tvy - self.vy) * t_lerp
                self.x += self.vx * dt
                self.y += self.vy * dt

                # Flame anim
                self.facc += dt * 10
                if self.facc >= 1.0:
                    self.facc -= 1.0
                    self.fidx = (self.fidx + 1) % 4
                
                # Emit particles (calculate world pos at tail)
                if random.random() < 0.4:
                    tx, ty = rotate_pt(-26, 0, math.cos(self.angle), math.sin(self.angle))
                    self.particles.append([self.x + tx, self.y + ty, 
                                          random.uniform(-15, 15), 
                                          random.uniform(-15, 15), 
                                          random.uniform(0.6, 1.2), 1.2])
                    if len(self.particles) > MAX_PARTICLES: self.particles.pop(0)

                self._draw_jet(show_flame=True)
                self._move_window()
                self.root.after(CONFIG['fps_interval'], self._tick)
                return

        # ── FLYING — exact HTML physics ───────────────────────────────────────
        # Target angle toward delayed cursor (same as HTML's mouse.x/y but delayed)
        target_angle = math.atan2(dy_del, dx_del)

        adiff = target_angle - self.angle
        while adiff >  math.pi: adiff -= 2*math.pi
        while adiff < -math.pi: adiff += 2*math.pi

        turn_spd = 6.0 + (dist_del / 150.0) * 4.0
        self.angle += adiff * max(0.0, min(turn_spd * dt, 0.45))

        # Maneuver Detection
        # 1. Afterburner
        self.is_afterburner = (dist_del > CONFIG['afterburner_threshold'])
        
        # 2. Barrel Roll
        if abs(adiff) > CONFIG['roll_threshold'] and self.roll_angle == 0:
            self.roll_angle = 0.001 # Start roll
        
        if self.roll_angle > 0:
            self.roll_angle += CONFIG['roll_speed'] * dt
            if self.roll_angle >= 2 * math.pi:
                self.roll_angle = 0.0

        # Speed (from HTML)
        if dist_del > 15:
            target_speed = CONFIG['max_speed']
            if self.is_afterburner:
                target_speed *= 2.0
            accel = 600 if dist_del > 100 else 300
        else:
            target_speed = CONFIG['max_speed'] * (dist_del / 15.0)
            accel = 400

        if self.speed < target_speed:
            self.speed = min(self.speed + accel * dt, target_speed)
        else:
            self.speed = max(self.speed - 400 * dt, target_speed)
        
        limit_mult = 2.5 if self.is_afterburner else 1.3
        self.speed = max(0, min(self.speed, CONFIG['max_speed'] * limit_mult))

        # Velocity lerp — HTML: lerp(vx, targetVx, 1 - pow(smoothing, dt))
        t_lerp = 1.0 - (CONFIG['smoothing'] ** dt)
        tvx = math.cos(self.angle) * self.speed
        tvy = math.sin(self.angle) * self.speed
        self.vx += (tvx - self.vx) * t_lerp
        self.vy += (tvy - self.vy) * t_lerp

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Catch check (real cursor)
        if dist_real < CONFIG['catch_dist']:
            if random.random() < self.exp_chance:
                self.state     = 'exploding'
                self.exp_frame = 0
                self.exp_acc   = 0.0
            else:
                self.state      = 'circling'
                self.circle_ang = math.atan2(self.y - real_cy, self.x - real_cx)
        else:
            # Flame anim — speed proportional
            speed_ratio = self.speed / CONFIG['max_speed']
            fps = max(4.0, min(22.0, speed_ratio * 22.0))
            self.facc += dt * fps
            if self.facc >= 1.0:
                self.facc -= 1.0
                self.fidx = (self.fidx + 1) % 4
            
            # Emit particles when flying
            if self.speed > 30 and random.random() < (self.speed / CONFIG['max_speed'] + 0.2):
                tx, ty = rotate_pt(-26, 0, math.cos(self.angle), math.sin(self.angle))
                # Smoke velocity: slightly opposite to jet direction
                svx = -self.vx * 0.1 + random.uniform(-10, 10)
                svy = -self.vy * 0.1 + random.uniform(-10, 10)
                self.particles.append([self.x + tx, self.y + ty, 
                                      svx, svy, 
                                      random.uniform(0.8, 1.5), 1.5])
                if len(self.particles) > MAX_PARTICLES: self.particles.pop(0)

        self._draw_jet(show_flame=(self.speed > 20))
        self._move_window()
        self.root.after(CONFIG['fps_interval'], self._tick)


if __name__ == '__main__':
    print("Fighter Jet v7  |  ESC or middle-click to quit")
    JetFollower()
