# Полевой журнал Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Собрать играбельный ритуал на Ren'Py «Полевой журнал»: три кассеты, прибор на экране, три финала.

**Architecture:** Берём рабочий каркас `the_question` (screens/gui/options + папка `game/gui`), выкидываем демо-сюжет и переводы, красим GUI под магнитофон, кладём свои фоны и петли, пишем `script.rpy` с переменными `voice_kept`, `followed_noise`, `ending`. Проверка — `tools/check_story.py` и `renpy.exe … lint`.

**Tech Stack:** Ren'Py 8.5.3 (`C:\Users\User\renpy-8.5.3-sdk\renpy.exe`), Python 3 stdlib для ассетов и проверки сценария.

**Spec:** `docs/superpowers/specs/2026-09-08-polevoy-zhurnal-design.md`

## Global Constraints

- Корень: `C:\Users\User\Documents\polevoy-zhurnal`
- SDK: `C:\Users\User\renpy-8.5.3-sdk`, разрешение 1280×720
- Имя: `config.name = _("Полевой журнал")`, `build.name = "PolevoyZhurnal"`
- Язык интерфейса и текста: русский
- Не цитировать песни, не класть музыку Сидорова, не показывать гибель / петлю / способы ухода
- Нет спрайтов персонажей, нет namebox, нет инвентаря
- Переменные: `voice_kept` (bool), `followed_noise` (bool), `ending` (`"cassette"` / `"wind"` / `"moss"`)
- Аудиофайлы только свои: `game/audio/hum_basement.wav`, `factory_wind.wav`, `forest_moss.wav`, `tape_click.wav`
- Коммиты в этом репозитории не делать, пока пользователь явно не попросит (шаги Commit пропускать)

---

## File map

- `project.json` — чтобы лаунчер видел игру
- `game/options.rpy` — имя, save dir, без голоса
- `game/gui.rpy` — янтарь/ржавчина, DejaVuSans, letter-spacing
- `game/screens.rpy` — say без рамки-картинки, choice как кнопки записи, HUD магнитофона, русское меню, `quick_menu = False`
- `game/script.rpy` — вся история
- `game/images/bg_basement.png`, `bg_factory.png`, `bg_grass.png`, `bg_forest.png`, `bg_black.png`
- `game/audio/*.wav` — петли и щелчок
- `tools/check_story.py` — проверка меток, выборов, финалов, запретных слов
- `tools/make_assets.py` — PNG 1280×720 с зерном и WAV-петли (только stdlib)

Не копировать из `the_question`: `game/script.rpy`, `game/tl/**`, `game/images/**`, `illurock.opus`, `testcases.rpy`.

---

### Task 1: Каркас проекта и падающая проверка сценария

**Files:**
- Create: `project.json`
- Create: `.gitignore`
- Create: `tools/check_story.py`
- Copy: `C:\Users\User\renpy-8.5.3-sdk\the_question\game\screens.rpy` → `game/screens.rpy`
- Copy: `C:\Users\User\renpy-8.5.3-sdk\the_question\game\gui.rpy` → `game/gui.rpy`
- Copy: `C:\Users\User\renpy-8.5.3-sdk\the_question\game\options.rpy` → `game/options.rpy`
- Copy: `C:\Users\User\renpy-8.5.3-sdk\the_question\game\gui\` → `game/gui\` (вся папка)
- Create: `game/script.rpy` (заглушка, чтобы Ren'Py не падал)

**Interfaces:**
- Consumes: SDK `the_question`
- Produces: `game/script.rpy` обязан позже содержать метки `start`, `cassette1`, `cassette2`, `cassette3`, `ending_cassette`, `ending_wind`, `ending_moss`; `tools/check_story.py` читает `game/script.rpy` как текст

- [ ] **Step 1: Скопировать каркас**

В PowerShell из `C:\Users\User\Documents\polevoy-zhurnal`:

```powershell
$src = "C:\Users\User\renpy-8.5.3-sdk\the_question\game"
New-Item -ItemType Directory -Force -Path game, tools, game/images, game/audio | Out-Null
Copy-Item "$src\screens.rpy" game\screens.rpy
Copy-Item "$src\gui.rpy" game\gui.rpy
Copy-Item "$src\options.rpy" game\options.rpy
Copy-Item "$src\gui" game\gui -Recurse -Force
```

`project.json`:

```json
{
  "display_name": "Полевой журнал",
  "renamed_all": true,
  "force_recompile": true,
  "packages": ["pc"]
}
```

`.gitignore`:

```
/game/saves
/game/cache
/game/**/*.rpyc
/game/**/*.rpymc
/errors.txt
/log.txt
/traceback.txt
.superpowers/
```

Заглушка `game/script.rpy`:

```renpy
label start:
    "заглушка"
    return
```

- [ ] **Step 2: Написать `tools/check_story.py`**

```python
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
```

- [ ] **Step 3: Прогнать проверку — должна упасть**

Run: `python tools/check_story.py`

Expected: `FAIL` и список `missing: label cassette1` (и остальные метки). Если `OK` — заглушка слишком полная, верни её к `label start` / `"заглушка"`.

---

### Task 2: Имя, палитра, русское меню, без quick menu

**Files:**
- Modify: `game/options.rpy`
- Modify: `game/gui.rpy` (цвета в начале файла)
- Modify: `game/screens.rpy` (navigation, main_menu, quick_menu default)

**Interfaces:**
- Consumes: скопированные options/gui/screens
- Produces: `config.name = _("Полевой журнал")`; пункты главного меню «Начать», «Продолжить», «Выход»; `default quick_menu = False`

- [ ] **Step 1: `game/options.rpy` — заменить имя и служебное**

Найти и заменить:

```renpy
define config.name = _("Полевой журнал")
define gui.show_name = True
define config.version = "1.0"
define gui.about = _p("""Полевой журнал. Ночная сессия.""")
define build.name = "PolevoyZhurnal"
define config.has_sound = True
define config.has_music = True
define config.has_voice = False
define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.window = "auto"
default preferences.text_cps = 28
define config.save_directory = "PolevoyZhurnal-1"
```

Оставить `config.window_icon` и блок `build.classify` как есть.

- [ ] **Step 2: `game/gui.rpy` — палитра A**

В блоке цветов заменить:

```renpy
define gui.accent_color = "#9a3b2a"
define gui.idle_color = "#8a8a70"
define gui.idle_small_color = "#a09a78"
define gui.hover_color = "#c4b48a"
define gui.selected_color = "#c9c4b0"
define gui.insensitive_color = "#55555580"
define gui.muted_color = "#2a1810"
define gui.hover_muted_color = "#3a2418"
define gui.text_color = "#c9c4b0"
define gui.interface_text_color = "#c9c4b0"
define gui.text_font = "DejaVuSans.ttf"
define gui.name_text_font = "DejaVuSans.ttf"
define gui.interface_text_font = "DejaVuSans.ttf"
define gui.main_menu_background = Solid("#0c0c0a")
define gui.game_menu_background = Solid("#0c0c0a")
```

`gui.init(1280, 720)` не трогать.

- [ ] **Step 3: Главное меню и навигация**

В `screen navigation()` для `if main_menu:` оставить только три кнопки:

```renpy
        if main_menu:

            textbutton _("Начать") action Start()

            textbutton _("Продолжить") action ShowMenu("load")

            textbutton _("Выход") action Quit(confirm=False)
```

Ветку `else:` (History/Save и т.д.) не удалять — меню паузы должно жить.

В `screen main_menu()` убрать показ версии. Блок имени:

```renpy
    if gui.show_name:

        vbox:
            text "[config.name!t]":
                style "main_menu_title"
```

Найти `default quick_menu = True` и поставить:

```renpy
default quick_menu = False
```

- [ ] **Step 4: Lint каркаса**

Run: `& "C:\Users\User\renpy-8.5.3-sdk\renpy.exe" "C:\Users\User\Documents\polevoy-zhurnal" lint`

Expected: завершение без ошибок скрипта (предупреждения про отсутствующие bg допустимы до Task 4). Если падает на `Solid` в `gui.rpy` — задать `define gui.main_menu_background = "#0c0c0a"` строкой, а в `screen main_menu` писать `add Solid("#0c0c0a")`.

---

### Task 3: Экран-прибор (HUD, say, choice)

**Files:**
- Modify: `game/screens.rpy` (экраны `say`, `choice`, новый `tape_hud`, стили window)

**Interfaces:**
- Consumes: ничего из script кроме store-переменных ниже
- Produces store (объявить в `screens.rpy` рядом с HUD):
  - `default cassette_label = "КАССЕТА I · ПОДВАЛ"`
  - `default rec_on = True`
  - `default rec_mode = "run"`  # `"run"` | `"freeze"` | `"zero"`
  - `default tape_frames = 0`
  - `init python: def tape_clock():` → `str` формата `MM:SS:FF`
- Produces: `screen tape_hud()`; `label start` позже делает `show screen tape_hud`

- [ ] **Step 1: Функция счётчика и HUD**

Вставить **перед** `screen say` в `screens.rpy`:

```renpy
default cassette_label = "КАССЕТА I · ПОДВАЛ"
default rec_on = True
default rec_mode = "run"
default tape_frames = 0

init python:
    def tape_clock():
        if rec_mode == "zero":
            return "00:00:00"
        total = tape_frames
        ff = total % 24
        ss = (total // 24) % 60
        mm = (total // 24) // 60
        return "{:02d}:{:02d}:{:02d}".format(mm, ss, ff)

screen tape_hud():
    zorder 50
    if rec_mode == "run":
        timer 0.042 repeat True action SetVariable("tape_frames", tape_frames + 1)

    text cassette_label:
        size 16
        color "#8a8a70"
        kerning 2
        xpos 18
        ypos 14

    hbox:
        xpos 0.98
        xanchor 1.0
        ypos 14
        spacing 10
        if rec_on:
            text "● REC":
                size 16
                color "#9a3b2a"
                kerning 3
        text tape_clock():
            size 16
            color "#8a8a70"
            kerning 2
```

- [ ] **Step 2: `screen say` без namebox-картинки**

Заменить `screen say` и стиль `window` на:

```renpy
screen say(who, what):
    window:
        id "window"
        background Transform(Solid("#000000"), alpha=0.72)
        yalign 1.0
        ysize 200
        xfill True
        text what id "what":
            color "#c9c4b0"
            size 22
            kerning 1.2
            xpos 40
            ypos 40
            xsize 1200
```

Стиль `window` с `background Image("gui/textbox.png"...` больше не должен перекрывать этот screen: либо удали `background Image(...)` у `style window`, либо не используй этот стиль (как выше — свойства прямо в screen).

- [ ] **Step 3: Кнопки записи**

Заменить `screen choice` и стили choice:

```renpy
screen choice(items):
    style_prefix "choice"
    vbox:
        xalign 0.5
        ypos 270
        yanchor 0.5
        spacing 10
        for i in items:
            textbutton i.caption action i.action

style choice_button:
    xminimum 720
    xmaximum 900
    yminimum 44
    background Solid("#14120ecc")
    hover_background Solid("#2a1810")
    padding (18, 10)
    xalign 0.5

style choice_button_text:
    color "#c9a090"
    hover_color "#c4b48a"
    size 18
    kerning 2
    text_align 0.5
    xalign 0.5
```

- [ ] **Step 4: Lint**

Run: `& "C:\Users\User\renpy-8.5.3-sdk\renpy.exe" "C:\Users\User\Documents\polevoy-zhurnal" lint`

Expected: без traceback. Заглушка `start` ещё не показывает HUD — это нормально.

---

### Task 4: Фоны и петли

**Files:**
- Create: `tools/make_assets.py`
- Create (скриптом): `game/images/bg_basement.png`, `bg_factory.png`, `bg_grass.png`, `bg_forest.png`, `bg_black.png`
- Create: `game/audio/hum_basement.wav`, `factory_wind.wav`, `forest_moss.wav`, `tape_click.wav`

**Interfaces:**
- Consumes: stdlib `struct`, `zlib`, `math`, `wave`, `random`
- Produces filenames ровно как выше; в `script.rpy` потом: `scene bg_basement`, `play music "audio/hum_basement.wav" fadein 1.5`

- [ ] **Step 1: Написать `tools/make_assets.py`**

Полный файл (PNG без Pillow — несжатые scanline + zlib):

```python
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


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    AUD.mkdir(parents=True, exist_ok=True)
    write_png(IMG / "bg_basement.png", field("basement"))
    write_png(IMG / "bg_factory.png", field("factory"))
    write_png(IMG / "bg_grass.png", field("grass"))
    write_png(IMG / "bg_forest.png", field("forest"))
    write_png(IMG / "bg_black.png", field("black"))

    tone_wav(AUD / "hum_basement.wav", 16, lambda t: 0.35 * math.sin(2 * math.pi * 55 * t) + 0.08 * math.sin(2 * math.pi * 110 * t) + (0.12 if int(t * 2) % 9 == 0 else 0) * math.sin(2 * math.pi * 900 * t))
    tone_wav(AUD / "factory_wind.wav", 16, lambda t: 0.25 * math.sin(2 * math.pi * 38 * t) + 0.2 * math.sin(2 * math.pi * 41.2 * t) + 0.05 * math.sin(2 * math.pi * 220 * t * (1 + 0.02 * math.sin(t))))
    tone_wav(AUD / "forest_moss.wav", 18, lambda t: 0.18 * math.sin(2 * math.pi * 48 * t) + 0.12 * math.sin(2 * math.pi * 52.7 * t) + 0.04 * math.sin(2 * math.pi * 180 * t))
    tone_wav(AUD / "tape_click.wav", 0.12, lambda t: 0.6 * math.sin(2 * math.pi * 180 * t) * math.exp(-t * 40))
    print("assets ok")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Сгенерировать**

Run: `python tools/make_assets.py`

Expected: печать `assets ok`; пять PNG в `game/images`, четыре WAV в `game/audio`.

- [ ] **Step 3: Объявить изображения в script (временно в заглушке)**

В конец заглушки `game/script.rpy` (до `label start`) добавить:

```renpy
image bg_basement = "images/bg_basement.png"
image bg_factory = "images/bg_factory.png"
image bg_grass = "images/bg_grass.png"
image bg_forest = "images/bg_forest.png"
image bg_black = "images/bg_black.png"
```

(В Task 5 эти строки остаются в полном сценарии.)

---

### Task 5: Сценарий трёх кассет

**Files:**
- Modify: `game/script.rpy` — заменить целиком

**Interfaces:**
- Consumes: `tape_hud`, `cassette_label`, `rec_on`, `rec_mode`, `tape_frames`, фоны, wav
- Produces: `default voice_kept = True`, `default followed_noise = False`, `default ending = ""`; метки как в `check_story.py`; меню с точными строками из проверки

- [ ] **Step 1: Записать полный `game/script.rpy`**

```renpy
default voice_kept = True
default followed_noise = False
default ending = ""

image bg_basement = "images/bg_basement.png"
image bg_factory = "images/bg_factory.png"
image bg_grass = "images/bg_grass.png"
image bg_forest = "images/bg_forest.png"
image bg_black = "images/bg_black.png"


label start:
    $ cassette_label = "КАССЕТА I · ПОДВАЛ"
    $ rec_on = True
    $ rec_mode = "run"
    $ tape_frames = 0
    show screen tape_hud
    play sound "audio/tape_click.wav"
    scene bg_black
    window show
    "Ночь уже стоит. Ты пришёл не разговаривать — писать."
    "В сумке — магнитофон, запас плёнки, кабель, который всегда чуть короче, чем нужно."
    jump cassette1


label cassette1:
    $ cassette_label = "КАССЕТА I · ПОДВАЛ"
    scene bg_basement
    with Dissolve(1.5)
    play music "audio/hum_basement.wav" fadein 2.0

    "Подвал переоборудован давно. Кто — не написано на стенах."
    "Лампа гудит на одной частоте. Если прислушаться, гул не ровный: внутри него капля."
    "Капля падает в ведро с интервалом, который стыдно считать. Ты всё равно считаешь."
    "В углу гитара. Струны не оборваны — просто никто не пришёл их забрать."
    "Ты ставишь микрофон ближе к лампе, чем к себе. Так честнее."
    "Наушники садятся плотно. Сначала слышно комнату. Потом — комнату, пропущенную через прибор."
    "Собственное дыхание приходит с задержкой. Оно уже не твоё. Оно лежит на плёнке отдельно."
    "Можно ничего не говорить. Тогда на кассете останется только этот гул, эта капля, эта гитара, которая не просит."
    "Можно сказать что-нибудь короткое. Чтобы позже знать, что здесь был человек."

    menu:
        "Записать голос":
            play sound "audio/tape_click.wav"
            $ voice_kept = True
            "Ты говоришь не имя. Имя здесь лишнее."
            "Говоришь: «подвал, ночь, лампа». Голос в наушниках приходит чужим, как сосед за стенкой."
            "Оставляешь это. Дыра ещё не открыта. Человеческий слой держится."
        "Стереть. Оставить гул":
            play sound "audio/tape_click.wav"
            $ voice_kept = False
            "Палец на паузе. Потом — перемотка, короткий участок, тишина вместо рта."
            "Гул лампы становится главным. Капля занимает место слова."
            "Дыра уже есть. Она не зарастёт, даже если дальше будет лес."

    "Ты закрываешь крышку не до конца. Плёнка ещё идёт."
    "Пора выходить. Завод за проходной лучше пишет ночью: меньше людей, больше сквозняка."
    jump cassette2


label cassette2:
    $ cassette_label = "КАССЕТА II · ЗАВОД"
    scene bg_factory
    with Dissolve(1.5)
    stop music fadeout 1.5
    play music "audio/factory_wind.wav" fadein 2.0

    "Цех дырявый. Ветер ходит по нему, как человек, который забыл, что его нет."
    "Ты не бьёшь по баку. Бак отвечает сам — петля удара, будто кто-то оставил ритм в железе."
    "Микрофон направлен в пустоту между колоннами. Там цивилизация ещё слышна, но уже как оболочка."

    if voice_kept:
        "В наушниках иногда всплывает тот кусок: «подвал, ночь, лампа». Смешно и не смешно. Человек среди железа."
    else:
        "Голоса на плёнке нет. Только гул, который переехал сюда вместе с тобой и стал сквозняком."

    "Можно остаться и писать смерть вещей: как остывает труба, как ржавчина имеет свою частоту."
    "Можно пойти за шумом — туда, где за проходной уже не бетон, а трава, которая не спрашивает разрешения."

    menu:
        "Идти за шумом, в траву":
            play sound "audio/tape_click.wav"
            $ followed_noise = True
            scene bg_grass
            with Dissolve(1.2)
            "Проходная не закрыта. Калитка стучит в том же размере, что и бак, только тише."
            "Трава здесь жёсткая, как проволока. Она пишет сама: шаги, которые ты не хотел считать своими."
            "Завод остаётся за спиной уже как порог. Ты его прошёл. Вещи ещё слышны, но не главные."
        "Остаться. Писать смерть вещей":
            play sound "audio/tape_click.wav"
            $ followed_noise = False
            "Ты не идёшь. Ставишь вторую кассету на железо."
            "Удар по баку повторяется без тебя. Сквозняк учит микрофон пустоте."
            "Если потом будет лес, он придёт сразу после этого — без переходной травы."

    "Дальше — полоса, где фонарей нет. Там уже не завод. Там деревья стоят слишком внимательно."
    jump cassette3


label cassette3:
    $ cassette_label = "КАССЕТА III · ЛЕС"
    scene bg_forest
    with Dissolve(2.0)
    stop music fadeout 2.0
    play music "audio/forest_moss.wav" fadein 2.5

    "Папоротник шумит так, будто это не листья, а чей-то вдох."
    "Мох закрывает то, что когда-то было тропой. Вода где-то рядом: не ручей, а присутствие."
    "Деревья не двигаются. Это хуже, чем если бы двигались."
    "Микрофон начинает писать частоту, которой не было в ушах. Ты это слышишь уже только через прибор."

    if voice_kept:
        "И один раз — только один — в наушниках возвращается твой голос из подвала. Уже неузнаваемый. Как будто его сказал лес."
    else:
        "На месте голоса — дыра. Плёнка пишет только то, что не человек. Это честнее, чем ты думал."

    if followed_noise:
        "Завод вспоминается как уже пройденный порог. Трава началась раньше леса. Лес это знает."
    else:
        "Лес пришёл сразу после железа. В мхе ещё слышны вещи: бак, сквозняк, пустая оболочка."

    "Плёнка почти кончилась. Остался жест — не мысль, а рука."

    menu:
        "Забрать кассету":
            play sound "audio/tape_click.wav"
            $ ending = "cassette"
            jump ending_cassette
        "Стереть всё":
            play sound "audio/tape_click.wav"
            $ ending = "wind"
            jump ending_wind
        "Оставить магнитофон в мху":
            play sound "audio/tape_click.wav"
            $ ending = "moss"
            jump ending_moss


label ending_cassette:
    $ cassette_label = "КАССЕТА"
    $ rec_on = False
    $ rec_mode = "freeze"
    stop music fadeout 3.0
    "Ты вынимаешь кассету. Крышка щёлкает сухо, по-домашнему, хотя дома ещё нет."
    "REC гаснет. Счётчик замирает на последней цифре, как на вдохе, который не отдали."
    if voice_kept:
        "Дома это будет почти человек. Чужой голос в наушниках, который когда-то был твоим."
        "Можно будет сказать: я там был. И в этом будет доля правды, которой хватит ненадолго."
    else:
        "Дома это будет просто шум. Можно сказать другим, что там был лес. Не услышат."
        "Шум не доказывает ничего. Он только занимает место."
    "Ты кладёшь кассету в карман. Она тёплая от прибора. Прибор уже пустой."
    "Ночь не кончается. Просто ты больше не пишешь."
    pause 1.5
    return


label ending_wind:
    $ cassette_label = "СКВОЗНЯК"
    $ rec_on = False
    $ rec_mode = "zero"
    $ tape_frames = 0
    scene bg_black
    with Dissolve(1.2)
    stop music fadeout 2.0
    "Стираешь. Не яростно — хозяйственно. Как моют кружку."
    "Плёнка становится пустой. Вещи говорили без людей. Теперь не говорят и вещи."
    "Счётчик обнуляется. Красной точки нет."
    if voice_kept:
        "Тот кусок — «подвал, ночь, лампа» — тоже уходит. Человеческий слой был. Его нет."
    else:
        "Стирать почти нечего. Дыра уже была. Ты только подтвердил её формой."
    if followed_noise:
        "Трава останется только в памяти, не на кассете. Память не считается записью."
    else:
        "Смерть вещей тоже стёрта. Остался сквозняк в голове, который микрофон уже не берёт."
    "Идёшь обратно без добычи. Это тоже сессия."
    pause 1.5
    return


label ending_moss:
    $ cassette_label = "МОХ"
    $ rec_on = True
    $ rec_mode = "run"
    "Ставишь магнитофон на мох. Не роняешь — ставишь, как оставляют миску для того, кто придёт позже."
    "Кабель лежит змеёй. Крышка открыта. REC не гаснет."
    "Счётчик идёт уже без тебя в кадре."
    if voice_kept:
        "Где-то на плёнке ещё есть человек. Лес допишет поверх. Получится не дуэт, а замещение."
    else:
        "Голоса не было. Значит, лес не будет никого перекрикивать. Только допишет."
    if followed_noise:
        "Трава уже начала эту работу за проходной. Мох — продолжение, не начало."
    else:
        "Железо останется в первых минутах. Потом мох закроет и его."
    "Ты уходишь без прибора. За спиной продолжает писаться то, чего ты больше не услышишь."
    "Это не прощание. Это просто конец твоей части сессии."
    pause 2.0
    return
```

- [ ] **Step 2: Проверка сценария должна пройти**

Run: `python tools/check_story.py`

Expected: `OK`

- [ ] **Step 3: Lint**

Run: `& "C:\Users\User\renpy-8.5.3-sdk\renpy.exe" "C:\Users\User\Documents\polevoy-zhurnal" lint`

Expected: 0 errors. Если ругается на image names — проверь пути `images/bg_basement.png` относительно `game/`.

---

### Task 6: Прогон финалов и HUD

**Files:**
- Test: прогон через SDK; при необходимости правка `game/script.rpy` / `game/screens.rpy`

**Interfaces:**
- Consumes: всё из задач 1–5
- Produces: игра, которую можно запустить из лаунчера или  
  `& "C:\Users\User\renpy-8.5.3-sdk\renpy.exe" "C:\Users\User\Documents\polevoy-zhurnal"`

- [ ] **Step 1: Запустить игру**

Run: `& "C:\Users\User\renpy-8.5.3-sdk\renpy.exe" "C:\Users\User\Documents\polevoy-zhurnal"`

Expected: чёрно-янтарное меню «Полевой журнал», пункты Начать / Продолжить / Выход.

- [ ] **Step 2: Ручной чеклист (спека)**

1. Начать → подвал, HUD: `КАССЕТА I · ПОДВАЛ`, красный REC, счётчик идёт.
2. Финал «Кассета»: подпись `КАССЕТА`, REC гаснет, счётчик замирает.
3. Финал «Сквозняк»: подпись `СКВОЗНЯК`, чёрный кадр, счётчик `00:00:00`.
4. Финал «Мох»: подпись `МОХ`, REC горит, счётчик идёт.
5. Комбинация голос+трава меняет фразы в лесу и в финале; гул+железо — другие фразы.
6. Нет чужих цитат, нет сцен гибели.
7. Выход из меню не падает.

- [ ] **Step 3: Если HUD не overlay** — в `label start` должно быть `show screen tape_hud` до первого `scene`; не вызывать `hide screen tape_hud` в финалах.

---

## Self-review (coverage)

| Спека | Задача |
|---|---|
| Три кассеты, recordist | Task 5 |
| voice_kept / followed_noise только красят | Task 5 if-блоки |
| Три финала и правила REC | Task 5 + Task 3 |
| Прибор HUD, без namebox | Task 3 |
| Палитра янтарь/ржавчина/мох | Task 2 + Task 4 |
| Свои петли, не Сидоров | Task 4 |
| Русское меню | Task 2 |
| Lint + три финала | Task 6 |
| Запрет гибели и цитат | Task 1 forbidden + Task 5 текст |
