"""PIKNOTT SAPPHIRE data: types, moves, species, stats, catching and damage maths. All names/designs are original."""
import random, math

TYPES = ["Plain", "Spark", "Leaf", "Aqua", "Ember", "Stone", "Frost", "Shade", "Sky"]
TYPE_COL = {"Plain": (0.80, 0.78, 0.72), "Spark": (1.00, 0.85, 0.15), "Leaf": (0.40, 0.80, 0.30), "Aqua": (0.25, 0.60, 1.00),
            "Ember": (1.00, 0.42, 0.18), "Stone": (0.62, 0.52, 0.40), "Frost": (0.65, 0.92, 1.00), "Shade": (0.48, 0.32, 0.70),
            "Sky": (0.55, 0.80, 0.98)}
# attacker -> {defender: multiplier}
CHART = {
    "Spark": {"Aqua": 2, "Sky": 2, "Leaf": 0.5, "Stone": 0.5, "Spark": 0.5},
    "Leaf": {"Aqua": 2, "Stone": 2, "Ember": 0.5, "Sky": 0.5, "Leaf": 0.5},
    "Aqua": {"Ember": 2, "Stone": 2, "Leaf": 0.5, "Aqua": 0.5},
    "Ember": {"Leaf": 2, "Frost": 2, "Aqua": 0.5, "Stone": 0.5, "Ember": 0.5},
    "Stone": {"Ember": 2, "Sky": 2, "Frost": 2, "Leaf": 0.5},
    "Frost": {"Leaf": 2, "Sky": 2, "Ember": 0.5, "Aqua": 0.5, "Frost": 0.5},
    "Shade": {"Shade": 2, "Plain": 0.5, "Spark": 2},
    "Sky": {"Leaf": 2, "Spark": 0.5, "Stone": 0.5},
    "Plain": {"Stone": 0.5, "Shade": 0.5},
}


def effectiveness(mtype, def_types):
    m = 1.0
    for t in def_types:
        m *= CHART.get(mtype, {}).get(t, 1.0)
    return m


# name: (type, power, accuracy, pp, kind)   kind: "hit" | "heal" | "boost"
MOVES = {
    "Tackle Hop": ("Plain", 40, 100, 30, "hit"), "Quick Swipe": ("Plain", 45, 100, 25, "hit"),
    "Body Slam": ("Plain", 75, 90, 12, "hit"), "Rest Glow": ("Plain", 0, 100, 8, "heal"), "Focus Up": ("Plain", 0, 100, 10, "boost"),
    "Static Nip": ("Spark", 40, 100, 25, "hit"), "Volt Dash": ("Spark", 60, 95, 18, "hit"), "Thunder Burst": ("Spark", 90, 85, 8, "hit"),
    "Leaf Flick": ("Leaf", 40, 100, 25, "hit"), "Vine Lash": ("Leaf", 60, 95, 18, "hit"), "Bloom Cannon": ("Leaf", 90, 85, 8, "hit"),
    "Splash Jet": ("Aqua", 40, 100, 25, "hit"), "Tide Slam": ("Aqua", 65, 95, 15, "hit"), "Torrent": ("Aqua", 90, 85, 8, "hit"),
    "Ember Spit": ("Ember", 40, 100, 25, "hit"), "Flame Rush": ("Ember", 65, 95, 15, "hit"), "Magma Roar": ("Ember", 95, 85, 8, "hit"),
    "Pebble Toss": ("Stone", 40, 100, 25, "hit"), "Rock Crush": ("Stone", 70, 90, 15, "hit"), "Landslide": ("Stone", 95, 80, 8, "hit"),
    "Frost Breath": ("Frost", 40, 100, 25, "hit"), "Ice Shard": ("Frost", 60, 100, 18, "hit"), "Blizzard Veil": ("Frost", 90, 85, 8, "hit"),
    "Shadow Peck": ("Shade", 40, 100, 25, "hit"), "Night Veil": ("Shade", 65, 95, 15, "hit"), "Void Pulse": ("Shade", 90, 85, 8, "hit"),
    "Gust Wing": ("Sky", 40, 100, 25, "hit"), "Air Slice": ("Sky", 65, 95, 15, "hit"), "Star Dive": ("Sky", 95, 85, 8, "hit"),
}

# Starters the player chooses at Azure Camp (one of 1, 2, 3).
STARTERS = [
    dict(sid=1, blurb="A spark-fast mountain hare. Quick on the ridges."),
    dict(sid=2, blurb="A sturdy pine-seed cub. Calm, tough and rooted."),
    dict(sid=3, blurb="A stream frog from the glacier runoff. Steady and wet."),
]

# id, name, types, base stats (hp, atk, def, spd), moves, catch rate, base xp, zones, size, aggressive, dex text, model recipe
SPECIES = [
    dict(id=1, name="Glintail", types=["Spark"], base=(44, 54, 38, 74), moves=["Quick Swipe", "Static Nip", "Volt Dash", "Thunder Burst"],
         rate=0.45, xp=60, zones=["Crystal Vale"], size=0.75, aggro=False, model="rabbit", col=(0.35, 0.72, 1.0), col2=(1.0, 0.92, 0.35),
         text="A mountain hare whose tufted tail stores a cold blue spark. It stamps once before it dashes."),
    dict(id=2, name="Pinekit", types=["Leaf"], base=(52, 44, 58, 40), moves=["Tackle Hop", "Leaf Flick", "Vine Lash", "Rest Glow"],
         rate=0.6, xp=50, zones=["Crystal Vale", "Nightpine"], size=0.65, aggro=False, model="blob", col=(0.22, 0.42, 0.28), col2=(0.55, 0.38, 0.18),
         text="A round pine-seed cub. The needles on its back flatten when it is content, and bristle when it is not."),
    dict(id=3, name="Brooklet", types=["Aqua"], base=(56, 44, 52, 42), moves=["Tackle Hop", "Splash Jet", "Tide Slam", "Rest Glow"],
         rate=0.6, xp=50, zones=["Glacier Mere", "Crystal Vale"], size=0.65, aggro=False, model="frog", col=(0.18, 0.48, 0.82), col2=(0.70, 0.92, 1.0),
         text="A jelly-soft frog that rides meltwater down the slopes. Its belly is the colour of a clear pool."),
    dict(id=4, name="Emberift", types=["Ember"], base=(46, 62, 40, 64), moves=["Quick Swipe", "Ember Spit", "Flame Rush", "Focus Up"],
         rate=0.45, xp=62, zones=["Cragspine"], size=0.75, aggro=True, model="fox", col=(0.72, 0.22, 0.28), col2=(1.0, 0.62, 0.25),
         text="A short-tempered ridge fox with a cleft of embers down its back. It charges anyone who blocks the path."),
    dict(id=5, name="Cragbit", types=["Stone"], base=(52, 56, 74, 24), moves=["Tackle Hop", "Pebble Toss", "Rock Crush", "Focus Up"],
         rate=0.55, xp=55, zones=["Cragspine", "Sapphire Caves"], size=0.7, aggro=False, model="beetle", col=(0.40, 0.44, 0.55), col2=(0.25, 0.45, 0.85),
         text="A beetle whose shell is veined with raw sapphire. Still, it looks like just another stone until it walks."),
    dict(id=6, name="Duskmaw", types=["Shade"], base=(46, 52, 44, 68), moves=["Quick Swipe", "Shadow Peck", "Night Veil", "Gust Wing"],
         rate=0.45, xp=60, zones=["Nightpine", "Sapphire Caves"], size=0.75, aggro=False, model="moth", col=(0.16, 0.14, 0.38), col2=(0.45, 0.70, 1.0),
         text="A moth of the night pines. The pale eyes on its wings blink when it wants to be left alone."),
    dict(id=7, name="Ridgewind", types=["Sky"], base=(42, 52, 36, 84), moves=["Quick Swipe", "Gust Wing", "Air Slice", "Star Dive"],
         rate=0.45, xp=58, zones=["Cragspine", "Crystal Vale", "Frostcrown"], size=0.6, aggro=False, model="bird", col=(0.40, 0.58, 0.78), col2=(0.92, 0.96, 1.0),
         text="A steel-blue ridge bird that rides the mountain wind. It never lands for long."),
    dict(id=8, name="Cascafin", types=["Aqua"], base=(62, 64, 55, 62), moves=["Body Slam", "Splash Jet", "Tide Slam", "Torrent"],
         rate=0.3, xp=90, zones=["Glacier Mere"], size=1.0, aggro=False, model="fish", col=(0.08, 0.42, 0.62), col2=(0.55, 0.90, 0.95),
         text="A big-finned swimmer of Glacier Mere. It leaps the ice weirs at dusk and soaks everything nearby."),
    dict(id=9, name="Voltclaw", types=["Spark"], base=(44, 58, 40, 78), moves=["Quick Swipe", "Static Nip", "Volt Dash", "Air Slice"],
         rate=0.4, xp=65, zones=["Nightpine", "Crystal Vale"], size=0.7, aggro=True, model="weasel", col=(0.16, 0.18, 0.28), col2=(0.35, 0.75, 1.0),
         text="A dark mountain weasel with electric-blue claws. It zaps first and is gone before you blink."),
    dict(id=10, name="Fernpeak", types=["Leaf", "Stone"], base=(78, 76, 74, 42), moves=["Body Slam", "Vine Lash", "Rock Crush", "Bloom Cannon"],
         rate=0.18, xp=140, zones=["Nightpine"], size=1.45, aggro=True, model="bear", col=(0.32, 0.40, 0.30), col2=(0.18, 0.42, 0.24),
         text="The moss-backed guardian of Nightpine. Ferns and shards of slate grow through its heavy shoulders."),
    dict(id=11, name="Rimehorn", types=["Frost"], base=(58, 58, 56, 72), moves=["Quick Swipe", "Frost Breath", "Ice Shard", "Blizzard Veil"],
         rate=0.3, xp=100, zones=["Frostcrown"], size=1.05, aggro=False, model="goat", col=(0.90, 0.95, 1.0), col2=(0.40, 0.72, 1.0),
         text="A sure-footed goat with ice-crystal horns. It only grazes the snowfields under Frostcrown."),
    dict(id=12, name="Basalith", types=["Ember", "Stone"], base=(82, 86, 82, 34), moves=["Body Slam", "Flame Rush", "Rock Crush", "Magma Roar"],
         rate=0.15, xp=150, zones=["Sapphire Caves"], size=1.5, aggro=True, model="golem", col=(0.18, 0.20, 0.32), col2=(0.25, 0.55, 1.0),
         text="A lumbering cave beast with sapphire-fire veins. Each step rings like a hammer in the basin."),
    dict(id=13, name="Azurath", types=["Sky", "Frost"], base=(92, 96, 88, 90), moves=["Air Slice", "Ice Shard", "Star Dive", "Blizzard Veil"],
         rate=0.05, xp=250, zones=["Azure Summit"], size=1.7, aggro=True, model="dragon", col=(0.12, 0.32, 0.78), col2=(0.85, 0.78, 0.58),
         text="A legendary sapphire dragon of the high peak. Old guides say it sleeps on Azure Summit and wakes only for a worthy climber."),
]
BY_ID = {s["id"]: s for s in SPECIES}
BY_NAME = {s["name"]: s for s in SPECIES}

BALLS = [  # key, display, catch multiplier, colour
    ("pikcel", "Pikcel Ball", 1.0, (0.20, 0.62, 0.98)),
    ("nova", "Nova Pikcel", 1.6, (0.62, 0.30, 0.95)),
    ("astral", "Astral Pikcel", 2.4, (0.95, 0.80, 0.30)),
]
STYLES = {"Normal": (1.0, 1.0), "Strong": (1.45, 1.55), "Agile": (0.65, 0.55)}   # power mult, action-time mult


def xp_for(level):
    return int(0.8 * level ** 3)


class Mon:
    def __init__(self, sid, level, nick=None):
        self.sid = sid; self.level = level; self.xp = xp_for(level)
        self.atk_boost = 0
        self.recalc(); self.hp = self.maxhp
        self.pp = {m: MOVES[m][3] for m in self.sp["moves"]}

    @property
    def sp(self):
        return BY_ID[self.sid]

    @property
    def name(self):
        return self.sp["name"]

    @property
    def types(self):
        return self.sp["types"]

    def recalc(self):
        hp, a, d, s = self.sp["base"]; L = self.level
        old = getattr(self, "maxhp", None)
        self.maxhp = int(2 * hp * L / 100) + L + 10
        self.atk = int(2 * a * L / 100) + 5
        self.dfn = int(2 * d * L / 100) + 5
        self.spd = int(2 * s * L / 100) + 5
        if old is not None:
            self.hp = min(self.maxhp, self.hp + (self.maxhp - old))

    def gain_xp(self, n):
        """Returns list of levels reached."""
        self.xp += n; ups = []
        while self.level < 100 and self.xp >= xp_for(self.level + 1):
            self.level += 1; self.recalc(); ups.append(self.level)
        return ups

    def heal_full(self):
        self.hp = self.maxhp; self.atk_boost = 0
        self.pp = {m: MOVES[m][3] for m in self.sp["moves"]}

    def to_json(self):
        return {"sid": self.sid, "level": self.level, "xp": self.xp, "hp": self.hp, "pp": self.pp}

    @staticmethod
    def from_json(d):
        m = Mon(d["sid"], d["level"]); m.xp = d.get("xp", m.xp); m.hp = min(m.maxhp, d.get("hp", m.maxhp))
        for k, v in d.get("pp", {}).items():
            if k in m.pp:
                m.pp[k] = v
        return m


def damage(att, dfn, move, style="Normal"):
    mtype, power, acc, pp, kind = MOVES[move]
    eff = effectiveness(mtype, dfn.types)
    stab = 1.5 if mtype in att.types else 1.0
    a = att.atk * (1 + 0.5 * att.atk_boost)
    base = ((2 * att.level / 5 + 2) * power * STYLES[style][0] * a / max(1, dfn.dfn)) / 50 + 2
    dmg = max(1, int(base * stab * eff * random.uniform(0.85, 1.0)))
    return dmg, eff


def action_time(mon, style="Normal"):
    """Action-order action cost: faster PIKNOTT and Agile style act sooner, Strong acts later."""
    return 100.0 * 80.0 / (mon.spd + 30.0) * STYLES[style][1]


def catch_chance(mon, ball_mult, stealth=1.0, in_battle=False):
    sp = mon.sp
    hp_f = 1.0 - 0.66 * mon.hp / mon.maxhp
    lvl_f = max(0.5, 1.0 - mon.level / 120.0)
    c = sp["rate"] * ball_mult * hp_f * lvl_f * stealth * (1.1 if in_battle else 1.0) * 1.6
    return max(0.02, min(0.97, c))
