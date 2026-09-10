# -*- coding: utf-8 -*-
import math, random, struct, wave, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "game" / "images"
AUD = ROOT / "game" / "audio"
W, H = 1280, 720


def crc(chunk):
    return struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


def write_png(path, pixels):
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    chunks = [b"\x89PNG\r\n\x1a\n"]
    for tag, data in [(b"IHDR", ihdr), (b"IDAT", zlib.compress(raw, 9)), (b"IEND", b"")]:
        chunks.append(struct.pack(">I", len(data)) + tag + data + crc(tag + data))
    path.write_bytes(b"".join(chunks))


def rgb(r, g, b):
    return (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))


def field(kind):
    rnd = random.Random(kind)
    rows = []
    for y in range(H):
        row = []
        for x in range(W):
            nx, ny = x / W, y / H
            grain = rnd.randint(-18, 18)
            if kind == "basement":
                r, g, b = 28 + 40 * (1 - ny) + 30 * math.exp(-((nx - 0.35) ** 2 + (ny - 0.2) ** 2) * 8), 18 + 12 * (1 - ny), 10
            elif kind == "factory":
                r, g, b = 22 + 18 * abs(math.sin(nx * 18)), 12 + 6 * ny, 8
                if int(x / 36) % 7 == 0:
                    r, g, b = r * 0.5, g * 0.5, b * 0.5
            elif kind == "grass":
                r, g, b = 12, 22 + 16 * ny, 12
            elif kind == "forest":
                r, g, b = 8, 16 + 20 * ny * (0.4 + 0.6 * abs(math.sin(nx * 9))), 10
            else:
                r, g, b = 4, 4, 4
            row.extend(rgb(r + grain, g + grain * 0.7, b + grain * 0.4))
        rows.append(row)
    return rows


def tone_wav(path, seconds, fn):
    rate = 44100
    n = int(rate * seconds)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            t = i / rate
            fade = min(1.0, t * 4, (seconds - t) * 4)
            v = int(max(-1, min(1, fn(t) * fade)) * 12000)
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


def main(audio_only=False):
    IMG.mkdir(parents=True, exist_ok=True)
    AUD.mkdir(parents=True, exist_ok=True)
    if not audio_only:
        write_png(IMG / "bg_basement.png", field("basement"))
        write_png(IMG / "bg_factory.png", field("factory"))
        write_png(IMG / "bg_grass.png", field("grass"))
        write_png(IMG / "bg_forest.png", field("forest"))
        write_png(IMG / "bg_black.png", field("black"))

    tone_wav(AUD / "hum_lamp.wav", 16, lambda t: 0.35 * math.sin(2 * math.pi * 55 * t) + 0.08 * math.sin(2 * math.pi * 110 * t))
    tone_wav(AUD / "basement_beep.wav", 0.45, lambda t: 0.4 * math.sin(2 * math.pi * 900 * t) * math.exp(-t * 8))
    tone_wav(AUD / "factory_wind.wav", 16, lambda t: 0.25 * math.sin(2 * math.pi * 38 * t) + 0.2 * math.sin(2 * math.pi * 41.2 * t) + 0.05 * math.sin(2 * math.pi * 220 * t * (1 + 0.02 * math.sin(t))))
    tone_wav(AUD / "forest_moss.wav", 18, lambda t: 0.18 * math.sin(2 * math.pi * 48 * t) + 0.12 * math.sin(2 * math.pi * 52.7 * t) + 0.04 * math.sin(2 * math.pi * 180 * t))
    tone_wav(AUD / "tape_click.wav", 0.12, lambda t: 0.6 * math.sin(2 * math.pi * 180 * t) * math.exp(-t * 40))
    print("assets ok")


if __name__ == "__main__":
    import sys
    main(audio_only="--audio" in sys.argv)
