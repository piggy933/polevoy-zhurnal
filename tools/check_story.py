# -*- coding: utf-8 -*-
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "game" / "script.rpy"

REQUIRED_LABELS = [
    "label start",
    "label cassette1",
    "label cassette2",
    "label cassette3",
    "label ending_cassette",
    "label ending_wind",
    "label ending_moss",
]
REQUIRED_SNIPPETS = [
    "default voice_kept",
    "default followed_noise",
    "default ending",
    "Записать голос",
    "Стереть. Оставить гул",
    "Идти за шумом, в траву",
    "Остаться. Писать смерть вещей",
    "Забрать кассету",
    "Стереть всё",
    "Оставить магнитофон в мху",
    'ending = "cassette"',
    'ending = "wind"',
    'ending = "moss"',
    "if voice_kept",
    "if followed_noise",
]
FORBIDDEN = ["повесил", "петл", "самоуби", "суицид"]


def main():
    text = SCRIPT.read_text(encoding="utf-8")
    errors = []
    for item in REQUIRED_LABELS + REQUIRED_SNIPPETS:
        if item not in text:
            errors.append("missing: " + item)
    low = text.lower()
    for word in FORBIDDEN:
        if word in low:
            errors.append("forbidden: " + word)
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
