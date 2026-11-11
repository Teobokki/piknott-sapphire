"""Builds derived assets from assets/cover.jpg (icon + widescreen backdrop), procedural SFX, and looping BGM. Run once before packaging."""
import os, wave, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
cov = Image.open(os.path.join(A, "cover.jpg")).convert("RGB")
w, h = cov.size; s = min(w, h)
sq = cov.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(A, "icon.png"))
sq.save(os.path.join(A, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
# widescreen side-fill for the start screen (the cover itself is drawn unaltered on top of this)
bg = sq.resize((1920, 1920), Image.LANCZOS).crop((0, 420, 1920, 1500)).filter(ImageFilter.GaussianBlur(28))
ImageEnhance.Brightness(bg).enhance(0.55).save(os.path.join(A, "backdrop.jpg"), quality=88)

SR = 22050
def save(name, x):
    x = np.clip(x, -1, 1); d = (x * 30000).astype(np.int16)
    os.makedirs(os.path.join(A, "sfx"), exist_ok=True)
    with wave.open(os.path.join(A, "sfx", name + ".wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes(d.tobytes())
def t(dur): return np.linspace(0, dur, int(SR * dur), endpoint=False)
def env(n, a=0.01, r=0.3):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    return e * np.exp(-np.linspace(0, 1, n) / r)
rng = np.random.default_rng(7)
x = t(0.35); save("throw", rng.standard_normal(len(x)) * env(len(x), 0.05, 0.35) * 0.4 * np.sin(np.pi * x / 0.35))
x = t(0.18); save("wobble", np.sin(2 * np.pi * (300 + 120 * np.sin(40 * x)) * x) * env(len(x), 0.005, 0.25) * 0.6)
x = t(0.9); f = np.where(x < 0.15, 660, np.where(x < 0.3, 880, 1320))
save("catch", (np.sin(2 * np.pi * f * x) * 0.5 + 0.3 * np.sin(4 * np.pi * f * x)) * env(len(x), 0.01, 0.5))
x = t(0.5); save("breakout", (np.sin(2 * np.pi * (500 - 600 * x) * x) * 0.6 + rng.standard_normal(len(x)) * 0.2) * env(len(x), 0.005, 0.25))
x = t(0.25); save("hit", (rng.standard_normal(len(x)) * 0.7 + np.sin(2 * np.pi * 90 * x) * 0.6) * env(len(x), 0.002, 0.12))
x = t(0.4); save("super", (np.sin(2 * np.pi * 220 * x) + np.sin(2 * np.pi * 330 * x)) * 0.35 * env(len(x), 0.002, 0.3) + rng.standard_normal(len(x)) * 0.3 * env(len(x), 0.001, 0.08))
x = t(0.08); save("click", np.sin(2 * np.pi * 1200 * x) * env(len(x), 0.001, 0.2) * 0.4)
x = t(1.0); save("levelup", sum(np.sin(2 * np.pi * fr * x) * (x > d0) for fr, d0 in ((523, 0), (659, 0.15), (784, 0.3), (1046, 0.45))) * 0.2 * env(len(x), 0.01, 0.6))
x = t(0.6); save("heal", np.sin(2 * np.pi * (600 + 600 * x) * x) * 0.4 * env(len(x), 0.05, 0.5))
x = t(0.3); save("alert", np.sin(2 * np.pi * 1000 * x) * (np.sin(2 * np.pi * 14 * x) > 0) * env(len(x), 0.005, 0.4) * 0.4)
print("assets ok")

# Looping BGM in F# minor (sapphire / cool key). Theme ~72 BPM; battle ~100 BPM in the same key.
# No glow: just dry additive tones and a soft pulse, no reverb tails that would read as bloom.
def tone(dur, freq, vol=0.12, r=0.4):
    x = t(dur)
    return np.sin(2 * np.pi * freq * x) * env(len(x), 0.02, r) * vol

def chord(dur, freqs, vol=0.08, r=0.5):
    x = t(dur)
    s = sum(np.sin(2 * np.pi * f * x) * (0.6 if i == 0 else 0.35) for i, f in enumerate(freqs))
    return s * env(len(x), 0.04, r) * vol / max(1, len(freqs) * 0.45)

# F#3, A3, C#4, F#4, A4, C#5
FS = 185.0; A3 = 220.0; CS = 277.2; FS4 = 370.0; A4 = 440.0; CS5 = 554.4; E4 = 329.6; D4 = 293.7
# 16s theme loop, 72 BPM (beat = 0.833s), pad + sparse melody
beat = 60.0 / 72.0
th = np.zeros(int(SR * 16.0))
def put(buf, start, sig):
    i = int(start * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i+n] += sig[:n]
# pads every 4 beats
prog = [(FS, CS, FS4), (A3, E4, A4), (D4, FS4, A4), (CS, E4, CS5)]
for bar, ch in enumerate(prog * 2):
    put(th, bar * beat * 4, chord(beat * 4.4, ch, vol=0.16, r=0.7))
# melody: slow, minor, mid register
mel = [FS4, None, A4, FS4, CS5, A4, None, FS4, E4, FS4, A4, None, CS5, A4, FS4, None]
for i, f in enumerate(mel):
    if f:
        put(th, i * beat, tone(beat * 1.6, f, vol=0.10, r=0.45) + tone(beat * 1.6, f * 2, vol=0.03, r=0.4))
# soft high pulse (not a sparkle bloom — just a tick)
for i in range(16):
    put(th, i * beat * 2 + 0.02, tone(0.12, CS5 * 2, vol=0.025, r=0.08))
save("theme", th * 0.85)

# Battle: same key, ~100 BPM, more pulse, shorter loop (9.6s = 16 beats)
beat_b = 60.0 / 100.0
bt = np.zeros(int(SR * beat_b * 16))
bprog = [(FS, CS, FS4), (FS, A3, CS5), (A3, E4, A4), (CS, FS4, CS5)]
for bar, ch in enumerate(bprog * 2):
    put(bt, bar * beat_b * 2, chord(beat_b * 2.3, ch, vol=0.18, r=0.4))
# driving fifth pulse
for i in range(16):
    kick = tone(0.16, FS, vol=0.12, r=0.08)
    nz = rng.standard_normal(len(kick)) * env(len(kick), 0.001, 0.04) * 0.08
    put(bt, i * beat_b, kick + nz)
    if i % 2 == 0:
        put(bt, i * beat_b + beat_b * 0.5, tone(0.10, CS, vol=0.07, r=0.07))
bmel = [CS5, A4, FS4, A4, E4, FS4, CS5, A4, FS4, CS5, A4, FS4, E4, A4, FS4, CS]
for i, f in enumerate(bmel):
    put(bt, i * beat_b, tone(beat_b * 0.9, f, vol=0.11, r=0.22))
save("battle", bt * 0.8)
print("music ok")
