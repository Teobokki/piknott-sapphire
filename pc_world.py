"""The Sapphire region: heightfield terrain, zones, scenery, collision and the minimap image."""
import math, random
import numpy as np
from pc_toon import Mesh, node_from_arrays, outlined, rot_z, rot_x, mm, LIGHT
LIGHT_XY = (LIGHT.x, LIGHT.y)

SIZE = 220.0          # region spans -SIZE..SIZE on x and y
N = 176               # grid cells per side
CELL = 2 * SIZE / N
WATER = 0.0
# Layout is deliberately unlike Celestika (camp south-west, peak north-east, forest east, caves north-west).
CAMP = (-60.0, -145.0)
PEAK = (40.0, 120.0)
LAKE = (90.0, 40.0)
LAKE_R = 35.0
CAVE = (-90.0, 50.0)
CAVE_R = 34.0
SHRINE = (10.0, 70.0)
BOUND_R = 196.0

ZONE_COL = {
    "Crystal Vale": (0.38, 0.66, 0.56), "Nightpine": (0.14, 0.28, 0.32), "Cragspine": (0.42, 0.46, 0.58),
    "Glacier Mere": (0.45, 0.72, 0.92), "Sapphire Caves": (0.10, 0.22, 0.48), "Frostcrown": (0.90, 0.94, 1.0),
    "Azure Summit": (0.50, 0.68, 0.92),
}
ZONE_LABEL_POS = {"Crystal Vale": (-20, -80), "Nightpine": (130, -10), "Cragspine": (-140, -20), "Glacier Mere": (90, 40),
                  "Sapphire Caves": (-90, 50), "Frostcrown": (40, 95), "Azure Summit": (40, 145), "Camp": CAMP}
PATHS = [[CAMP, (-30, -90), (0, -50), (10, 10), SHRINE, (25, 90), PEAK],
         [(-30, -90), (40, -70), (100, -20), (110, 20)],
         [(-30, -90), (-80, -40), (-95, 15), CAVE],
         [(10, 10), (50, 20), LAKE]]


def _fbm(x, y, seed=11, octaves=4, scale=0.02):
    rng = np.random.default_rng(seed)
    h = np.zeros_like(x, dtype=np.float64); amp = 1.0; f = scale
    for _ in range(octaves):
        for _k in range(3):
            a = rng.uniform(0, 2 * math.pi); p1, p2 = rng.uniform(0, 2 * math.pi, 2)
            dx, dy = math.cos(a), math.sin(a)
            h += amp * np.sin((x * dx + y * dy) * f + p1) * np.cos((x * dy - y * dx) * f * 0.7 + p2) / 3
        amp *= 0.5; f *= 2.03
    return h


def raw_height(x, y):
    h = 2.8 + 2.1 * _fbm(x, y, 11)
    # Main peak — tall snow mountain, no crater (unlike Celestika's volcano).
    dp = np.hypot(x - PEAK[0], y - PEAK[1])
    v = np.clip(1 - dp / 110.0, 0, 1)
    h += 82 * v ** 1.55
    # West crag ridge
    rx = np.clip((-x - 70) / 50, 0, 1)
    h += rx * rx * (6 + 11 * np.abs(_fbm(x, y, 19, 3, 0.035)) * 2.0)
    # East nightpine plateau, slightly raised
    fx = np.clip((x - 75) / 50, 0, 1)
    h += fx * 2.8 * (_fbm(x, y, 7, 2, 0.05) + 0.55)
    # Glacier Mere
    dl = np.hypot(x - LAKE[0], y - LAKE[1])
    h = np.where(dl < LAKE_R, h - 8.0 * np.clip(1 - dl / LAKE_R, 0, 1) ** 0.6 - 1.4, h)
    h = np.where(dl < LAKE_R + 6, np.minimum(h, 1.0 + (dl - LAKE_R) * 0.5 + 1.2), h)
    h = np.where(dl < LAKE_R + 6, np.maximum(h, -5.5), h)
    # Sapphire Caves basin (depressed, walkable floor)
    dv = np.hypot(x - CAVE[0], y - CAVE[1])
    bowl = np.clip(1 - dv / CAVE_R, 0, 1)
    h = np.where(dv < CAVE_R, h - 14.0 * bowl ** 0.75 - 1.5, h)
    h = np.where(dv < CAVE_R, np.maximum(h, -3.8), h)
    # A slightly higher rim around the cave so it reads as a hollow
    ring = (dv > CAVE_R - 6) & (dv < CAVE_R + 8)
    h = np.where(ring, h + 3.5 * np.clip(1 - np.abs(dv - CAVE_R) / 7, 0, 1), h)
    # A gap on the south rim so you can walk in
    gap = (y < CAVE[1] - 8) & (np.abs(x - CAVE[0]) < 14) & (dv < CAVE_R + 10)
    h = np.where(gap, h - 4.0, h)
    r = np.hypot(x, y)
    h += np.minimum(np.clip(r - 188, 0, None) ** 1.15 * 1.0, 34.0) * (0.75 + 0.25 * np.sin(np.arctan2(y, x) * 9))
    dc = np.hypot(x - CAMP[0], y - CAMP[1])
    t = np.clip((dc - 10) / 14, 0, 1)
    h = h * t + 2.4 * (1 - t)
    return h


def fb(y):
    """West edge of the vale (crag begins)."""
    return -85 + 12 * np.sin(y * 0.028 + 0.4)


def rb(y):
    """East edge of the vale (nightpine begins)."""
    return 70 + 10 * np.sin(y * 0.031 + 1.6)


def zone_of(x, y, h):
    if math.hypot(x - LAKE[0], y - LAKE[1]) < LAKE_R + 4:
        return "Glacier Mere"
    if math.hypot(x - CAVE[0], y - CAVE[1]) < CAVE_R + 2 and h < 10:
        return "Sapphire Caves"
    dv = math.hypot(x - PEAK[0], y - PEAK[1])
    if dv < 100 and h > 10:
        if dv < 28 and h > 50:
            return "Azure Summit"
        if h > 32:
            return "Frostcrown"
        if h > 16 and dv < 70:
            return "Frostcrown"
    if x < fb(y):
        return "Cragspine"
    if x > rb(y):
        return "Nightpine"
    return "Crystal Vale"


def _seg_dist(px, py, a, b):
    ax, ay = a; bx, by = b
    vx, vy = bx - ax, by - ay
    t = np.clip(((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy), 0, 1)
    return np.hypot(px - (ax + t * vx), py - (ay + t * vy))


def path_dist(px, py):
    d = np.full(np.shape(px), 1e9)
    for pl in PATHS:
        for a, b in zip(pl, pl[1:]):
            d = np.minimum(d, _seg_dist(px, py, a, b))
    return d


def colour_field(x, y, h, slope):
    """Flat cel palette per sample — cooler sapphire palette than Celestika."""
    c = np.zeros(x.shape + (3,))
    dp = np.hypot(x - PEAK[0], y - PEAK[1])
    vale = np.array(ZONE_COL["Crystal Vale"]); pine = np.array(ZONE_COL["Nightpine"])
    crag = np.array(ZONE_COL["Cragspine"]); cave = np.array(ZONE_COL["Sapphire Caves"])
    frost = np.array(ZONE_COL["Frostcrown"]); summit = np.array(ZONE_COL["Azure Summit"])
    c[:] = vale
    F, Rr = fb(y), rb(y)
    c[x < F] = crag
    c[(x < F + 8) & (x >= F)] = (vale + crag) / 2
    c[x > Rr] = pine
    c[(x > Rr - 8) & (x <= Rr)] = (vale + pine) / 2
    cv = np.hypot(x - CAVE[0], y - CAVE[1])
    c[(cv < CAVE_R + 4) & (h < 12)] = cave
    c[(cv < CAVE_R) & (h < 4)] = cave * 0.85 + np.array((0.05, 0.12, 0.35))
    pk = (dp < 100) & (h > 10)
    c[pk & (h > 16)] = (0.45, 0.52, 0.68)
    c[pk & (h > 32)] = frost
    c[pk & (h > 52) & (dp < 30)] = summit
    c[(h > 3) & (slope > 1.1) & ~(pk | (cv < CAVE_R))] = crag * 0.85
    pd = path_dist(x, y)
    c[(pd < 2.6) & (cv >= CAVE_R) & ~((dp < 90) & (h > 32))] = (0.58, 0.55, 0.50)
    nl = np.hypot(x - LAKE[0], y - LAKE[1]) < LAKE_R + 9
    c[nl & (h < 1.4) & (h > -0.5)] = (0.78, 0.86, 0.92)          # icy shore
    c[nl & (h <= -0.5)] = (0.35, 0.52, 0.62)
    dc = np.hypot(x - CAMP[0], y - CAMP[1])
    c[dc < 9] = (0.55, 0.52, 0.48)
    rr_ = np.hypot(x, y)
    c[rr_ > 192] = (0.40, 0.48, 0.66)
    c[(rr_ > 192) & (h > 20)] = (0.90, 0.93, 1.0)
    return c


class Region:
    def __init__(self, seed=2026):
        self.rng = np.random.default_rng(seed)
        xs = np.linspace(-SIZE, SIZE, N + 1)
        self.gx, self.gy = np.meshgrid(xs, xs)
        self.H = raw_height(self.gx, self.gy)
        gy_, gx_ = np.gradient(self.H, CELL)
        self.slope = np.hypot(gx_, gy_)
        nrm = np.dstack([-gx_, -gy_, np.ones_like(self.H)])
        self.VN = nrm / np.linalg.norm(nrm, axis=2, keepdims=True)
        self.trees = []; self.rocks = []; self.grass = []; self.obstacles = []; self.pickups = []

    def height(self, x, y):
        fx = (x + SIZE) / CELL; fy = (y + SIZE) / CELL
        i = int(min(max(fx, 0), N - 1.001)); j = int(min(max(fy, 0), N - 1.001))
        tx, ty = min(max(fx - i, 0), 1), min(max(fy - j, 0), 1)
        H = self.H
        if tx + ty <= 1:
            return float(H[j, i] + (H[j, i + 1] - H[j, i]) * tx + (H[j + 1, i] - H[j, i]) * ty)
        return float(H[j + 1, i + 1] + (H[j + 1, i] - H[j + 1, i + 1]) * (1 - tx) + (H[j, i + 1] - H[j + 1, i + 1]) * (1 - ty))

    def ground(self, x, y):
        return max(self.height(x, y), WATER - 0.6) if self.in_lake(x, y) else self.height(x, y)

    def in_lake(self, x, y):
        return math.hypot(x - LAKE[0], y - LAKE[1]) < LAKE_R + 2 and self.height(x, y) < WATER

    def in_cave(self, x, y):
        return math.hypot(x - CAVE[0], y - CAVE[1]) < CAVE_R + 2 and self.height(x, y) < 10

    def zone(self, x, y):
        return zone_of(x, y, self.height(x, y))

    def in_grass(self, x, y):
        for gx, gy, r in self.grass:
            if (x - gx) ** 2 + (y - gy) ** 2 < r * r:
                return True
        return False

    def push_out(self, x, y, rad=0.45):
        for ox, oy, r in self.obstacles:
            dx, dy = x - ox, y - oy
            d2 = dx * dx + dy * dy; rr = r + rad
            if d2 < rr * rr and d2 > 1e-6:
                d = math.sqrt(d2); x = ox + dx / d * rr; y = oy + dy / d * rr
        rr = math.hypot(x, y)
        if rr > BOUND_R:
            x *= BOUND_R / rr; y *= BOUND_R / rr
        return x, y

    def build(self, parent, progress=None):
        root = parent.attach_new_node("region")
        H, gx, gy = self.H, self.gx, self.gy
        j, i = np.mgrid[0:N, 0:N]
        P = np.dstack([gx, gy, H])
        a = P[j, i]; b = P[j, i + 1]; c = P[j + 1, i]; d = P[j + 1, i + 1]
        na, nb, nc, nd = self.VN[j, i], self.VN[j, i + 1], self.VN[j + 1, i], self.VN[j + 1, i + 1]
        t1 = np.stack([a, b, c], 2).reshape(-1, 3, 3); t2 = np.stack([d, c, b], 2).reshape(-1, 3, 3)
        k1 = np.stack([na, nb, nc], 2).reshape(-1, 3, 3); k2 = np.stack([nd, nc, nb], 2).reshape(-1, 3, 3)
        tris = np.concatenate([t1, t2]); inks = np.concatenate([k1, k2])
        fn = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]); fn /= np.linalg.norm(fn, axis=1, keepdims=True)
        cen = tris.mean(1)
        sl = np.hypot(fn[:, 0], fn[:, 1]) / np.maximum(fn[:, 2], 0.05)
        col = colour_field(cen[:, 0], cen[:, 1], cen[:, 2], sl)
        v = tris.reshape(-1, 3); k = inks.reshape(-1, 3); cc = np.repeat(col, 3, 0)
        terr = node_from_arrays(v.astype(np.float32), k.astype(np.float32), cc, k.astype(np.float32), "terrain")
        t = outlined(terr, root, 0.10, name="terrain"); t.set_shader_input("rim_k", 0.0)
        if progress: progress(0.35)
        # Glacier Mere water (icy sapphire, no glow)
        m = Mesh(); seg = 48
        V = [(LAKE[0], LAKE[1], WATER)]; T = []
        for s in range(seg + 1):
            ang = 2 * math.pi * s / seg; V.append((LAKE[0] + math.cos(ang) * (LAKE_R + 8), LAKE[1] + math.sin(ang) * (LAKE_R + 8), WATER))
        for s in range(seg):
            T.append((0, s + 1, s + 2))
        m.add(V, [(0, 0, 1)] * len(V), (0.18, 0.48, 0.88, 0.9), [(0, 0, 1)] * len(V), T)
        for rr in (10, 20, 28):
            Vr, Tr = [], []
            for s in range(seg + 1):
                ang = 2 * math.pi * s / seg
                for q in (rr, rr + 0.5):
                    Vr.append((LAKE[0] + math.cos(ang) * q, LAKE[1] + math.sin(ang) * q, WATER + 0.03))
            for s in range(seg):
                if s % 3 == 0: continue
                a0 = s * 2; Tr += [(a0, a0 + 2, a0 + 1), (a0 + 1, a0 + 2, a0 + 3)]
            m.add(Vr, [(0, 0, 1)] * len(Vr), (0.70, 0.88, 1.0, 0.9), [(0, 0, 1)] * len(Vr), Tr)
        for r0, r1, colw in ((LAKE_R - 6, LAKE_R + 8, (0.45, 0.78, 1.0, 0.85)), (LAKE_R + 0.5, LAKE_R + 1.6, (1, 1, 1, 0.95))):
            Vr, Tr = [], []
            for q in range(seg + 1):
                ang = 2 * math.pi * q / seg
                for rr_ in (r0, r1):
                    Vr.append((LAKE[0] + math.cos(ang) * rr_, LAKE[1] + math.sin(ang) * rr_, WATER + 0.015))
            for q in range(seg):
                a0 = q * 2; Tr += [(a0, a0 + 2, a0 + 1), (a0 + 1, a0 + 2, a0 + 3)]
            m.add(Vr, [(0, 0, 1)] * len(Vr), colw, [(0, 0, 1)] * len(Vr), Tr)
        w = m.node("water"); w.reparent_to(root); w.set_shader_input("rim_k", 0.0); w.set_shader_input("unlit", 1.0)
        from panda3d.core import TransparencyAttrib
        w.set_transparency(TransparencyAttrib.M_alpha); w.set_bin("transparent", 5); w.set_depth_write(False)
        self.scatter()
        if progress: progress(0.55)
        self.build_scenery(root)
        if progress: progress(0.9)
        return root

    def scatter(self):
        R = random.Random(9)
        def ok(x, y):
            if math.hypot(x, y) > 175: return False
            if math.hypot(x - CAMP[0], y - CAMP[1]) < 16: return False
            if math.hypot(x - LAKE[0], y - LAKE[1]) < LAKE_R + 4: return False
            if math.hypot(x - CAVE[0], y - CAVE[1]) < CAVE_R: return False
            return True
        for _ in range(1400):
            x, y = R.uniform(-180, 180), R.uniform(-180, 180)
            if not ok(x, y):
                continue
            z = self.zone(x, y); h = self.height(x, y)
            if z in ("Crystal Vale", "Nightpine") and h < 28 and len(self.trees) < 220:
                kind = "pine" if (z == "Nightpine" or R.random() < 0.55) else "round"
                s = R.uniform(0.7, 1.35)
                self.trees.append((x, y, s, kind))
                self.obstacles.append((x, y, 0.7 * s))
            p = {"Cragspine": 0.55, "Frostcrown": 0.18, "Sapphire Caves": 0.0, "Crystal Vale": 0.05, "Nightpine": 0.04}.get(z, 0)
            if R.random() < p and len(self.rocks) < 160 and z != "Sapphire Caves":
                s = R.uniform(0.6, 1.8)
                self.rocks.append((x, y, s)); self.obstacles.append((x, y, 0.55 * s))
        # grass in the vale and nightpine, plus two patches by camp
        spots = []
        for _ in range(400):
            x, y = R.uniform(-170, 170), R.uniform(-170, 160)
            z = self.zone(x, y)
            if ok(x, y) and z in ("Crystal Vale", "Nightpine") and len(spots) < 34:
                if all((x - a) ** 2 + (y - b) ** 2 > 400 for a, b, _ in spots):
                    spots.append((x, y, R.uniform(4.5, 7.5)))
        spots[:0] = [(CAMP[0] + 14, CAMP[1] + 17, 6.0), (CAMP[0] - 16, CAMP[1] + 25, 5.0)]
        self.grass = spots
        for _ in range(200):
            x, y = R.uniform(-170, 170), R.uniform(-170, 160)
            if ok(x, y) and len(self.pickups) < 18 and self.height(x, y) < 45:
                self.pickups.append((x, y))

    def build_scenery(self, root):
        R = random.Random(5)
        m = Mesh()
        for (x, y, s, kind) in self.trees:
            z = self.height(x, y) - 0.2
            if kind == "pine":
                m.cone((x, y, z), 1.6 * s, 0.32 * s, (0.24, 0.18, 0.18), seg=10, top_r=0.2 * s)
                dark = R.choice([(0.10, 0.24, 0.28), (0.12, 0.28, 0.30), (0.08, 0.20, 0.26)])
                for q, (hh, rr) in enumerate(((1.2, 2.2), (2.6, 1.7), (3.8, 1.15))):
                    m.cone((x, y, z + hh * s), 2.0 * s, rr * s, dark, seg=14)
            else:
                m.cone((x, y, z), 1.8 * s, 0.3 * s, (0.36, 0.26, 0.18), seg=10, top_r=0.22 * s)
                g = R.choice([(0.28, 0.58, 0.40), (0.24, 0.52, 0.38), (0.32, 0.62, 0.42)])
                m.ellipsoid((x, y, z + 2.8 * s), (1.5 * s, 1.5 * s, 1.3 * s), g, seg=16, rings=10)
                for q in range(3):
                    a = R.uniform(0, 6.28)
                    m.ellipsoid((x + math.cos(a) * 0.9 * s, y + math.sin(a) * 0.9 * s, z + (2.3 + q * 0.4) * s), (0.85 * s, 0.85 * s, 0.75 * s), g, seg=14, rings=9)
        trees = m.node("trees")
        outlined(trees, root, 0.07, name="trees")
        sh = Mesh(); seg = 20
        def disc(x, y, r):
            z = self.height(x, y) + 0.06
            off = (-LIGHT_XY[0] * r * 0.5, -LIGHT_XY[1] * r * 0.5)
            V = [(x + off[0], y + off[1], z)] + [(x + off[0] + math.cos(a / seg * 6.283) * r * 1.25, y + off[1] + math.sin(a / seg * 6.283) * r,
                                                 self.height(x + off[0] + math.cos(a / seg * 6.283) * r * 1.25, y + off[1] + math.sin(a / seg * 6.283) * r) + 0.06) for a in range(seg + 1)]
            sh.add(V, [(0, 0, 1)] * len(V), (0.08, 0.12, 0.28, 0.38), [(0, 0, 1)] * len(V), [(0, i + 1, i + 2) for i in range(seg)])
        for (x, y, s_, kind) in self.trees:
            disc(x, y, (1.6 if kind == "round" else 1.4) * s_)
        for (x, y, s_) in self.rocks:
            disc(x, y, s_ * 0.9)
        shn = sh.node("shadows"); shn.reparent_to(root)
        from panda3d.core import TransparencyAttrib
        shn.set_transparency(TransparencyAttrib.M_alpha); shn.set_depth_write(False); shn.set_bin("transparent", 2)
        shn.set_shader_input("unlit", 1.0)
        m = Mesh(); rr = np.random.default_rng(4)
        for (x, y, s) in self.rocks:
            z = self.height(x, y)
            zn = self.zone(x, y)
            col = (0.80, 0.86, 0.95) if zn == "Frostcrown" else ((0.36, 0.40, 0.52) if zn == "Cragspine" else (0.50, 0.54, 0.62))
            m.rock((x, y, z + 0.2 * s), (s, s * rr.uniform(0.8, 1.2), s * rr.uniform(0.6, 1.0)), col, rr)
        outlined(m.node("rocks"), root, 0.07, name="rocks")
        # sapphire cave crystals
        cm = Mesh(); cr = np.random.default_rng(21)
        for _ in range(46):
            ang = cr.uniform(0, 6.28); d = cr.uniform(6, CAVE_R - 4)
            x, y = CAVE[0] + math.cos(ang) * d, CAVE[1] + math.sin(ang) * d
            z = self.height(x, y)
            s = cr.uniform(0.7, 1.8)
            col = cr.choice([(0.20, 0.42, 0.95), (0.30, 0.55, 1.0), (0.15, 0.32, 0.80)])
            cm.cone((x, y, z), 1.8 * s, 0.35 * s, col, seg=6)
            cm.cone((x, y, z + 1.6 * s), 0.9 * s, 0.18 * s, (0.55, 0.80, 1.0), seg=6)
            self.obstacles.append((x, y, 0.4 * s))
        outlined(cm.node("crystals"), root, 0.05, name="crystals")
        # tall grass — cooler greens
        m = Mesh()
        for (gx, gy, r) in self.grass:
            n = int(r * r * 1.6)
            for _ in range(n):
                a = R.uniform(0, 2 * math.pi); d = r * math.sqrt(R.random())
                x, y = gx + math.cos(a) * d, gy + math.sin(a) * d
                z = self.height(x, y) - 0.05
                col = R.choice([(0.22, 0.55, 0.38), (0.28, 0.62, 0.42), (0.18, 0.48, 0.36)])
                lean = mm(rot_z(R.uniform(0, 6.28)), rot_x(R.uniform(-0.25, 0.25)))
                m.cone((x, y, z), R.uniform(0.75, 1.15), 0.2, col, seg=5, rot=lean)
        gr = outlined(m.node("grass"), root, 0.025, name="grass"); gr.set_shader_input("rim_k", 0.4)
        # camp: sapphire-blue tent, campfire, crates, banner
        m = Mesh()
        cx, cy = CAMP; z = 2.4
        m.cone((cx - 5, cy + 3, z), 3.4, 3.0, (0.16, 0.38, 0.82), seg=4, rot=rot_z(math.pi / 4))
        m.box((cx - 5, cy + 0.9, z + 0.8), (0.5, 0.05, 0.8), (0.10, 0.18, 0.40))
        for a in range(5):
            ang = a * 2 * math.pi / 5
            m.box((cx + math.cos(ang) * 0.9, cy + math.sin(ang) * 0.9, z + 0.15), (0.6, 0.15, 0.15), (0.40, 0.26, 0.16), rot=rot_z(ang + math.pi / 2))
        for a in range(8):
            ang = a * 2 * math.pi / 8
            m.rock((cx + math.cos(ang) * 1.6, cy + math.sin(ang) * 1.6, z), (0.35, 0.35, 0.25), (0.40, 0.44, 0.55), np.random.default_rng(a))
        m.box((cx + 4.5, cy + 3.5, z + 0.5), (0.5, 0.5, 0.5), (0.55, 0.42, 0.28))
        m.box((cx + 5.3, cy + 2.6, z + 0.4), (0.4, 0.4, 0.4), (0.50, 0.38, 0.24))
        m.cone((cx + 6, cy - 3, z), 5, 0.12, (0.35, 0.28, 0.20), seg=5, top_r=0.1)
        m.box((cx + 6.7, cy - 3, z + 4.4), (0.7, 0.04, 0.45), (0.20, 0.48, 0.95))
        # Sapphire Shrine on the climb
        sx, sy = SHRINE; sz = self.height(sx, sy)
        for q in range(3):
            m.box((sx, sy, sz + 0.4 + q * 0.8), (2.2 - q * 0.6, 2.2 - q * 0.6, 0.4), (0.40, 0.48, 0.70))
        m.cone((sx, sy, sz + 2.4), 3.0, 0.3, (0.25, 0.55, 1.0), seg=5)
        self.obstacles.append((sx, sy, 2.4)); self.obstacles.append((cx - 5, cy + 3, 2.4))
        outlined(m.node("camp"), root, 0.05, name="camp")
        self.build_sky(root)
        m = Mesh()
        m.cone((0, 0, 0), 1.3, 0.55, (1.0, 0.55, 0.12), seg=6)
        m.cone((0, 0, 0.05), 0.8, 0.32, (1.0, 0.92, 0.35), seg=6)
        self.fire = outlined(m.node("flame"), root, 0.03, name="fire")
        self.fire.set_pos(cx, cy, z + 0.2)

    def build_sky(self, parent):
        """Cel sky: deeper sapphire-blue bands, a pale sun and outlined clouds (no glow/bloom)."""
        from panda3d.core import TransparencyAttrib
        self.sky = parent.attach_new_node("sky")
        m = Mesh(); seg, rings, R = 32, 16, 900.0
        bands = [(-0.2, (0.55, 0.68, 0.86)), (0.06, (0.38, 0.55, 0.82)), (0.16, (0.28, 0.46, 0.80)), (0.32, (0.20, 0.38, 0.72)),
                 (0.55, (0.14, 0.28, 0.62))]
        def skycol(zn):
            c = bands[0][1]
            for t, cc in bands:
                if zn >= t: c = cc
            return c
        V, N, C, T = [], [], [], []
        for j in range(rings + 1):
            th = math.pi * j / rings
            for i in range(seg + 1):
                ph = 2 * math.pi * i / seg
                u = (math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th))
                V.append((u[0] * R, u[1] * R, u[2] * R)); N.append((-u[0], -u[1], -u[2])); C.append(skycol(u[2]))
        for j in range(rings):
            for i in range(seg):
                a = j * (seg + 1) + i; b = a + seg + 1
                T.append((a, a + 1, b)); T.append((a + 1, b + 1, b))
        m.add(V, N, C, N, T)
        sx, sy, sz = LIGHT.x * 860, LIGHT.y * 860, LIGHT.z * 860
        for rr, cc in ((70, (1.0, 0.98, 0.90)), (42, (1.0, 1.0, 0.98))):
            m.sphere((sx, sy, sz), rr, cc, seg=20, rings=12)
        dome = m.node("dome"); dome.reparent_to(self.sky)
        dome.set_shader_input("unlit", 1.0); dome.set_two_sided(True); dome.set_bin("background", 0); dome.set_depth_write(False)
        dome.set_light_off(); dome.set_fog_off()
        self.sky.set_compass()
        R2 = random.Random(21); cm = Mesh()
        for _ in range(26):
            a = R2.uniform(0, 2 * math.pi); d = R2.uniform(230, 420)
            cx, cy, cz = math.cos(a) * d, math.sin(a) * d, R2.uniform(95, 150)
            for q in range(R2.randint(4, 7)):
                rr = R2.uniform(10, 20)
                cm.ellipsoid((cx + R2.uniform(-22, 22), cy + R2.uniform(-12, 12), cz + R2.uniform(-3, 5)), (rr * 1.4, rr, rr * 0.7),
                             (0.92, 0.95, 1.0), seg=14, rings=8)
        self.clouds = outlined(cm.node("clouds"), parent, 0.9, name="clouds")
        self.clouds.set_shader_input("fog_far", 5000.0); self.clouds.set_shader_input("rim_k", 0.6)

    def map_image(self, res=512):
        xs = np.linspace(-SIZE, SIZE, res)
        X, Y = np.meshgrid(xs, xs)
        Hh = raw_height(X, Y)
        gy_, gx_ = np.gradient(Hh, xs[1] - xs[0])
        sl = np.hypot(gx_, gy_)
        c = colour_field(X, Y, Hh, sl)
        dl = np.hypot(X - LAKE[0], Y - LAKE[1])
        c[(Hh < WATER) & (dl < LAKE_R + 6)] = (0.28, 0.62, 0.95)
        cv = np.hypot(X - CAVE[0], Y - CAVE[1])
        c[(cv < CAVE_R) & (Hh < 8)] = (0.12, 0.28, 0.62)
        band = np.floor(Hh / 10.0)
        edge = (np.abs(np.diff(band, axis=0, prepend=band[:1])) + np.abs(np.diff(band, axis=1, prepend=band[:, :1]))) > 0
        c[edge & (Hh > 4)] *= 0.55
        px = lambda v: int((v + SIZE) / (2 * SIZE) * (res - 1))
        for (x, y, s, k) in self.trees:
            i, j = px(x), px(y)
            c[max(0, j - 1):j + 2, max(0, i - 1):i + 2] = (0.06, 0.16, 0.18) if k == "pine" else (0.16, 0.40, 0.28)
        for (x, y, r) in self.grass:
            rr = int(r / (2 * SIZE) * res) + 1; i, j = px(x), px(y)
            yy, xx = np.ogrid[-rr:rr + 1, -rr:rr + 1]
            sub = c[max(0, j - rr):j + rr + 1, max(0, i - rr):i + rr + 1]
            msk = (xx ** 2 + yy ** 2 <= rr * rr)[:sub.shape[0], :sub.shape[1]]
            sub[msk] = (0.18, 0.48, 0.32)
        i, j = px(CAMP[0]), px(CAMP[1]); c[j - 4:j + 5, i - 4:i + 5] = (0.2, 0.45, 0.95)
        i, j = px(SHRINE[0]), px(SHRINE[1]); c[j - 3:j + 4, i - 3:i + 4] = (0.35, 0.75, 1.0)
        c[np.hypot(X, Y) > BOUND_R + 4] *= 0.45
        img = (np.clip(c, 0, 1) * 255).astype(np.uint8)
        return img
