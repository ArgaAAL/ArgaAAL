from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1200
HEIGHT = 430
FRAMES_PER_SCENE = 14
FRAME_DURATION_MS = 90

INK = (8, 11, 9)
INK_2 = (15, 20, 17)
PORCELAIN = (230, 233, 226)
PORCELAIN_2 = (205, 211, 203)
GRAPHITE = (53, 59, 55)
MUTED = (126, 137, 130)
LIME = (200, 255, 46)
BLUE = (132, 182, 255)
GREEN = (76, 184, 115)
RED = (235, 100, 91)

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        path,
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


DISPLAY = font("C:/Windows/Fonts/DejaVuSans-Bold.ttf", 42)
CHAPTER = font("C:/Windows/Fonts/DejaVuSans-Bold.ttf", 34)
HEADING = font("C:/Windows/Fonts/DejaVuSans-Bold.ttf", 24)
BODY = font("C:/Windows/Fonts/DejaVuSans.ttf", 17)
MONO = font("C:/Windows/Fonts/CascadiaMono.ttf", 14)
MONO_BOLD = font("C:/Windows/Fonts/DejaVuSansMono-Bold.ttf", 14)
SMALL = font("C:/Windows/Fonts/CascadiaMono.ttf", 12)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def mix(a: float, b: float, value: float) -> float:
    return a + (b - a) * value


def mix_color(a: tuple[int, int, int], b: tuple[int, int, int], value: float) -> tuple[int, int, int]:
    return tuple(int(mix(left, right, value)) for left, right in zip(a, b))


def text_color(light: bool) -> tuple[int, int, int]:
    return INK if light else PORCELAIN


def muted_color(light: bool) -> tuple[int, int, int]:
    return GRAPHITE if light else MUTED


def glow_dot(image: Image.Image, x: float, y: float, radius: int = 5, color: tuple[int, int, int] = LIME) -> None:
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow, "RGBA")
    draw.ellipse((x - radius * 4, y - radius * 4, x + radius * 4, y + radius * 4), fill=(*color, 95))
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 2.2))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 255))


def contour_field(draw: ImageDraw.ImageDraw, light: bool, offset: float = 0.0) -> None:
    color = (*GRAPHITE, 45) if light else (*PORCELAIN_2, 24)
    for index in range(6):
        points = []
        for x in range(-40, WIDTH + 41, 30):
            y = 72 + index * 66 + math.sin((x / 115.0) + index * 0.9 + offset) * (20 + index * 4)
            points.append((x, y))
        draw.line(points, fill=color, width=1)


def base(scene: int, light: bool, progress: float) -> Image.Image:
    background = PORCELAIN if light else INK
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*background, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    contour_field(draw, light, scene * 0.7 + progress * 0.25)

    accent_x = int(mix(-180, WIDTH + 80, progress))
    accent = PORCELAIN_2 if light else (26, 34, 29)
    draw.polygon(
        [(accent_x - 260, 0), (accent_x + 10, 0), (accent_x + 310, HEIGHT), (accent_x + 40, HEIGHT)],
        fill=(*accent, 48 if light else 60),
    )

    fg = text_color(light)
    muted = muted_color(light)
    draw.text((38, 25), "ARGA ADOLF LUMUNON", font=MONO_BOLD, fill=fg)
    draw.text((1162, 25), "ONE SIGNAL / MANY LAYERS", font=MONO, fill=muted, anchor="ra")
    draw.line((38, 54, 1162, 54), fill=(*muted, 70), width=1)
    draw.text((1162, 394), f"0{scene + 1} / 08", font=SMALL, fill=muted, anchor="ra")
    return image


def scene_title(draw: ImageDraw.ImageDraw, light: bool, index: str, project: str, title: str, status: str) -> None:
    fg = text_color(light)
    muted = muted_color(light)
    draw.text((42, 88), index, font=MONO_BOLD, fill=LIME if not light else GREEN)
    draw.text((42, 113), project.upper(), font=MONO, fill=muted)
    lines = title.split("\n")
    for line_index, line in enumerate(lines):
        draw.text((42, 151 + line_index * 49), line, font=DISPLAY, fill=fg)
    draw.text((42, 346), status, font=SMALL, fill=muted)


def draw_intent(progress: float) -> Image.Image:
    image = base(0, False, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, False, "01", "Nara / Nova", "A request is\nnot an action.", "INTENT > REVIEW > SIGNED ACTION")

    x0, y0 = 560, 105
    typed = "send 0.02 BTC"[: max(1, int(13 * ease(progress * 1.8)))]
    draw.rounded_rectangle((x0, y0, 1085, y0 + 72), radius=28, fill=(235, 239, 232, 240))
    draw.text((x0 + 26, y0 + 24), typed, font=BODY, fill=INK)
    draw.ellipse((x0 + 473, y0 + 22, x0 + 505, y0 + 54), fill=LIME)
    draw.text((x0 + 489, y0 + 38), ">", font=MONO_BOLD, fill=INK, anchor="mm")

    gate_t = ease(clamp((progress - 0.22) / 0.5))
    review_x = int(mix(1125, 690, gate_t))
    review_alpha = int(255 * gate_t)
    draw.line((610, 222, 1050, 222), fill=(*MUTED, 95), width=2)
    draw.line((610, 222, 610 + 440 * gate_t, 222), fill=(*LIME, 220), width=3)
    draw.rounded_rectangle((review_x, 250, review_x + 365, 338), radius=8, fill=(17, 24, 20, review_alpha), outline=(*MUTED, review_alpha), width=1)
    draw.text((review_x + 18, 266), "REVIEW BEFORE SIGNING", font=SMALL, fill=(*BLUE, review_alpha))
    draw.text((review_x + 18, 291), "BTC  0.0200     fee  0.0001", font=MONO, fill=(*PORCELAIN, review_alpha))
    draw.text((review_x + 18, 316), "human confirmation required", font=SMALL, fill=(*MUTED, review_alpha))
    glow_dot(image, 610 + 440 * gate_t, 222)
    return image


def draw_risk(progress: float) -> Image.Image:
    image = base(1, False, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, False, "02", "Fradium", "Risk lives in\nthe path.", "GRAPH > MODEL > EXPLANATION")

    nodes = [(590, 210), (705, 118), (725, 292), (850, 190), (952, 104), (1008, 268), (1100, 188)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 6), (5, 6), (1, 4), (2, 5)]
    for left, right in edges:
        draw.line((*nodes[left], *nodes[right]), fill=(*MUTED, 80), width=2)

    path = [0, 1, 3, 5, 6]
    visible_segments = progress * (len(path) - 1)
    for index in range(len(path) - 1):
        amount = clamp(visible_segments - index)
        if amount <= 0:
            continue
        start = nodes[path[index]]
        end = nodes[path[index + 1]]
        target = (mix(start[0], end[0], amount), mix(start[1], end[1], amount))
        draw.line((*start, *target), fill=(*LIME, 230), width=4)

    for index, (x, y) in enumerate(nodes):
        radius = 11 if index in path else 7
        fill = LIME if index <= visible_segments + 0.2 and index in path else GRAPHITE
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=PORCELAIN_2, width=1)

    active_index = min(len(path) - 1, int(visible_segments + 0.5))
    glow_dot(image, *nodes[path[active_index]])
    score = int(18 + 64 * ease(clamp((progress - 0.38) / 0.62)))
    draw.arc((1018, 286, 1138, 406), 205, 205 + score * 2.7, fill=RED, width=7)
    draw.text((1078, 347), f"{score:02d}", font=HEADING, fill=PORCELAIN, anchor="mm")
    draw.text((1078, 374), "PATH RISK", font=SMALL, fill=MUTED, anchor="mm")
    return image


def draw_runtime(progress: float) -> Image.Image:
    image = base(2, True, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, True, "03", "Fradium AI", "The model must\nsurvive runtime.", "TRAINING SHAPE != DEPLOYMENT SHAPE")

    compress = ease(clamp(progress * 1.45))
    source_x = 560
    layer_widths = [260, 215, 170, 125]
    for index, width in enumerate(layer_widths):
        y = 118 + index * 46
        current_width = mix(width, 92, compress)
        x = mix(source_x, 744, compress)
        draw.rounded_rectangle((x, y, x + current_width, y + 24), radius=12, fill=(*GRAPHITE, 165 - index * 18))
        draw.text((x + 10, y + 5), ["GNN", "XGBOOST", "FEATURES", "WEIGHTS"][index], font=SMALL, fill=PORCELAIN)

    capsule_x = mix(830, 902, ease(clamp((progress - 0.42) / 0.58)))
    draw.rounded_rectangle((capsule_x, 190, capsule_x + 112, 250), radius=30, fill=INK)
    draw.text((capsule_x + 56, 220), "ONNX", font=MONO_BOLD, fill=LIME, anchor="mm")
    boundary_x = 1030
    draw.line((boundary_x, 90, boundary_x, 348), fill=(*INK, 130), width=2)
    draw.text((boundary_x + 12, 92), "WASM BOUNDARY", font=SMALL, fill=GRAPHITE)

    cross = ease(clamp((progress - 0.62) / 0.38))
    signal_x = mix(capsule_x + 110, 1110, cross)
    draw.line((capsule_x + 110, 220, signal_x, 220), fill=(*GREEN, 220), width=4)
    for ring in range(3):
        radius = 22 + ring * 19
        draw.arc((1088 - radius, 220 - radius, 1088 + radius, 220 + radius), 210, 505, fill=(*GREEN, 125 - ring * 30), width=3)
    draw.text((1088, 310), "STABLE MODEL STATE", font=SMALL, fill=GRAPHITE, anchor="mm")
    glow_dot(image, signal_x, 220, color=GREEN)
    return image


def draw_flow(progress: float) -> Image.Image:
    image = base(3, False, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, False, "04", "PayGate / Marketizen", "Pressure changes\narchitecture.", "PAYMENT RAILS / GATEWAY / QUEUE / STATE")

    rail_y = 238
    stops = [(570, "REQUEST"), (700, "PAY"), (825, "GATE"), (950, "QUEUE"), (1085, "STATE")]
    draw.line((stops[0][0], rail_y, stops[-1][0], rail_y), fill=(*MUTED, 100), width=3)
    for index, (x, label) in enumerate(stops):
        active = progress * (len(stops) - 1) >= index - 0.1
        radius = 22 if index in (1, 2, 3) else 14
        draw.ellipse((x - radius, rail_y - radius, x + radius, rail_y + radius), fill=LIME if active else GRAPHITE, outline=PORCELAIN_2, width=2)
        draw.text((x, rail_y + 47), label, font=SMALL, fill=PORCELAIN, anchor="mm")

    segment = progress * (len(stops) - 1)
    left_index = min(len(stops) - 2, int(segment))
    amount = segment - left_index
    signal_x = mix(stops[left_index][0], stops[left_index + 1][0], amount)
    glow_dot(image, signal_x, rail_y)

    draw.text((700, 154), "402", font=HEADING, fill=BLUE, anchor="mm")
    draw.text((825, 154), "API", font=HEADING, fill=PORCELAIN, anchor="mm")
    draw.text((950, 154), "ASYNC", font=HEADING, fill=PORCELAIN, anchor="mm")
    draw.line((1040, 118, 1136, 118), fill=(*GREEN, 160), width=5)
    draw.line((1040, 136, 1115, 136), fill=(*BLUE, 160), width=5)
    draw.line((1040, 154, 1090, 154), fill=(*LIME, 160), width=5)
    draw.text((1088, 177), "HEALTHY UNDER LOAD", font=SMALL, fill=MUTED, anchor="mm")
    return image


def draw_evidence(progress: float) -> Image.Image:
    image = base(4, True, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, True, "05", "SpecHeal", "Green is not\nproof.", "FAILURE > EVIDENCE > VALIDATION > RERUN")

    x0 = 560
    draw.text((x0, 104), "locator('[data-test=checkout]')", font=MONO, fill=GRAPHITE)
    draw.line((x0, 132, x0 + 530, 132), fill=(*RED, 190), width=3)
    draw.text((x0 + 530, 104), "FAIL", font=MONO_BOLD, fill=RED, anchor="ra")

    stages = [(585, 215, "DOM"), (750, 285, "SCREEN"), (915, 205, "VALIDATE"), (1080, 285, "RERUN")]
    for index in range(len(stages) - 1):
        x1, y1, _ = stages[index]
        x2, y2, _ = stages[index + 1]
        draw.line((x1, y1, x2, y2), fill=(*GRAPHITE, 95), width=2)
    reached = progress * (len(stages) - 1)
    for index, (x, y, label) in enumerate(stages):
        active = reached >= index - 0.08
        fill = GREEN if active else PORCELAIN_2
        draw.rounded_rectangle((x - 54, y - 30, x + 54, y + 30), radius=5, fill=fill, outline=GRAPHITE, width=1)
        draw.text((x, y), label, font=SMALL, fill=INK, anchor="mm")

    left_index = min(len(stages) - 2, int(reached))
    amount = reached - left_index
    x1, y1, _ = stages[left_index]
    x2, y2, _ = stages[left_index + 1]
    glow_dot(image, mix(x1, x2, amount), mix(y1, y2, amount), color=GREEN)
    proof = ease(clamp((progress - 0.68) / 0.32))
    draw.rounded_rectangle((1007, 88, 1144, 152), radius=4, outline=(*GREEN, int(255 * proof)), width=3)
    draw.text((1075, 120), "PASS / PROVEN", font=SMALL, fill=(*GREEN, int(255 * proof)), anchor="mm")
    return image


def draw_input(progress: float) -> Image.Image:
    image = base(5, False, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, False, "06", "A1931 Bridge", "Unsupported does\nnot mean unusable.", "BLE HID > RELAY > NATIVE INPUT")

    pad = (570, 126, 850, 338)
    draw.rounded_rectangle(pad, radius=18, fill=(15, 21, 18), outline=(*PORCELAIN_2, 100), width=2)
    finger_y = mix(260, 178, ease(progress))
    finger_x = mix(655, 720, ease(progress))
    for offset in (-28, 28):
        draw.ellipse((finger_x + offset - 10, finger_y - 10, finger_x + offset + 10, finger_y + 10), fill=LIME)
        draw.line((finger_x + offset, finger_y + 13, finger_x + offset + 34, finger_y + 48), fill=(*LIME, 100), width=2)

    split_x, split_y = 925, 232
    draw.line((850, split_y, split_x, split_y), fill=(*LIME, 210), width=3)
    draw.line((split_x, split_y, 1060, 162), fill=(*BLUE, 210), width=3)
    draw.line((split_x, split_y, 1060, 302), fill=(*GREEN, 210), width=3)
    draw.text((1080, 154), "ANDROID", font=MONO_BOLD, fill=BLUE)
    draw.text((1080, 176), "native multitouch", font=SMALL, fill=MUTED)
    draw.text((1080, 294), "WIN ARM64", font=MONO_BOLD, fill=GREEN)
    draw.text((1080, 316), "precision touchpad", font=SMALL, fill=MUTED)
    glow_dot(image, mix(850, split_x, progress), split_y)
    return image


def draw_camera(progress: float) -> Image.Image:
    image = base(6, False, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, False, "07", "Nabu Camera / WIP", "An unresolved edge\nstays unresolved.", "WINDOWS ON ARM / QUALCOMM CAMERA STACK")

    lens_x, lens_y = 610, 210
    for radius, color in ((92, GRAPHITE), (68, BLUE), (40, INK_2), (14, LIME)):
        draw.ellipse((lens_x - radius, lens_y - radius, lens_x + radius, lens_y + radius), outline=color, width=5)

    stages = [(760, "SENSOR"), (855, "ISP"), (950, "IPE"), (1060, "BUFFER ?")]
    draw.line((lens_x + 92, lens_y, 1095, lens_y), fill=(*MUTED, 110), width=3)
    for index, (x, label) in enumerate(stages):
        reached = progress * len(stages) >= index + 0.2
        draw.ellipse((x - 12, lens_y - 12, x + 12, lens_y + 12), fill=GREEN if reached else GRAPHITE)
        draw.text((x, lens_y + 34), label, font=SMALL, fill=PORCELAIN, anchor="mm")

    stop_x = mix(lens_x + 92, 1060, ease(progress))
    glow_dot(image, stop_x, lens_y, color=GREEN)
    draw.rectangle((1030, 102, 1150, 182), fill=(41, 86, 55), outline=GREEN, width=2)
    for y in range(108, 179, 7):
        draw.line((1034, y, 1146, y), fill=(*LIME, 25), width=1)
    draw.text((1090, 142), "GREEN FRAME", font=SMALL, fill=PORCELAIN, anchor="mm")
    draw.line((1060, 176, 1060, 330), fill=(*RED, 210), width=3)
    draw.text((1076, 314), "MAPPING / OWNERSHIP", font=SMALL, fill=RED)
    draw.text((1076, 334), "OPEN PROBLEM", font=MONO_BOLD, fill=PORCELAIN)
    return image


def draw_belief(progress: float) -> Image.Image:
    image = base(7, True, progress)
    draw = ImageDraw.Draw(image, "RGBA")
    scene_title(draw, True, "08", "Self-consistency research / WIP", "A hypothesis earns\nits weight.", "PROPOSE > COMPRESS > COUNTERFACTUAL > REVISE")

    center = (900, 224)
    labels = ["H1", "H2", "H3", "H4", "H5"]
    radii = [155, 135, 175, 125, 165]
    for index, label in enumerate(labels):
        angle = index * (math.tau / len(labels)) + progress * 1.2
        collapse = ease(clamp((progress - 0.42) / 0.58))
        radius = mix(radii[index], 38 if index == 2 else 75, collapse)
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius * 0.66
        color = GREEN if index == 2 else mix_color(BLUE, GRAPHITE, collapse)
        draw.line((*center, x, y), fill=(*GRAPHITE, 70), width=1)
        draw.ellipse((x - 24, y - 24, x + 24, y + 24), fill=color, outline=INK, width=1)
        draw.text((x, y), label, font=SMALL, fill=INK if index == 2 else PORCELAIN, anchor="mm")

    draw.ellipse((center[0] - 55, center[1] - 55, center[0] + 55, center[1] + 55), outline=GRAPHITE, width=2)
    draw.text(center, "TEST", font=MONO_BOLD, fill=INK, anchor="mm")
    final_alpha = int(255 * ease(clamp((progress - 0.62) / 0.38)))
    draw.rounded_rectangle((1000, 335, 1152, 382), radius=23, fill=(*GREEN, final_alpha))
    draw.text((1076, 358), "PROVISIONAL", font=SMALL, fill=(*INK, final_alpha), anchor="mm")
    glow_dot(image, center[0] + 38, center[1], color=GREEN)
    return image


SCENES = [draw_intent, draw_risk, draw_runtime, draw_flow, draw_evidence, draw_input, draw_camera, draw_belief]


def render_animation() -> Path:
    frames: list[Image.Image] = []
    for scene_index, renderer in enumerate(SCENES):
        next_renderer = SCENES[(scene_index + 1) % len(SCENES)]
        for local_frame in range(FRAMES_PER_SCENE):
            progress = local_frame / (FRAMES_PER_SCENE - 1)
            frame = renderer(progress)
            if progress > 0.78:
                transition = ease((progress - 0.78) / 0.22)
                incoming = next_renderer(transition * 0.12)
                frame = Image.blend(frame, incoming, transition)
            frames.append(frame.convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT))

    output = MEDIA / "system-loop.gif"
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return output


def chapter_base(light: bool, number: str, title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    background = PORCELAIN if light else INK
    image = Image.new("RGBA", (1200, 300), (*background, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    color = text_color(light)
    muted = muted_color(light)
    for index in range(5):
        y = 40 + index * 60
        draw.arc((-120 + index * 100, y - 170, 950 + index * 80, y + 420), 195, 340, fill=(*muted, 34), width=1)
    draw.text((36, 28), number, font=MONO_BOLD, fill=LIME if not light else GREEN)
    draw.text((36, 56), title, font=CHAPTER, fill=color)
    draw.text((38, 105), subtitle, font=SMALL, fill=muted)
    return image, draw


def render_chapter_intent() -> Path:
    image, draw = chapter_base(False, "01", "INTENT BECOMES ACTION", "NARA / NOVA / FRADIUM")
    points = [(420, 220), (585, 150), (760, 220), (930, 145), (1110, 220)]
    for index in range(len(points) - 1):
        draw.line((*points[index], *points[index + 1]), fill=(*MUTED, 120), width=2)
    labels = ["PROMPT", "REVIEW", "RISK", "SIGN", "RECEIPT"]
    for index, ((x, y), label) in enumerate(zip(points, labels)):
        radius = 28 if index in (1, 2, 3) else 18
        fill = LIME if index in (1, 3) else (28, 36, 31)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=PORCELAIN_2, width=2)
        draw.text((x, y + 49), label, font=SMALL, fill=PORCELAIN, anchor="mm")
    draw.line((*points[0], *points[-1]), fill=(*LIME, 48), width=8)
    glow_dot(image, *points[2])
    output = MEDIA / "chapter-intent.webp"
    image.convert("RGB").save(output, "WEBP", quality=88, method=6)
    return output


def render_chapter_pressure() -> Path:
    image, draw = chapter_base(True, "02", "SYSTEMS UNDER PRESSURE", "MARKETIZEN / PAYGATE / SPECHEAL")
    rail_y = 210
    stops = [(400, "LOAD"), (545, "GATEWAY"), (695, "QUEUE"), (845, "STATE"), (1010, "PROOF"), (1140, "PASS")]
    draw.line((stops[0][0], rail_y, stops[-1][0], rail_y), fill=(*GRAPHITE, 125), width=3)
    for index, (x, label) in enumerate(stops):
        fill = GREEN if index in (1, 4, 5) else PORCELAIN_2
        radius = 24 if index in (1, 4) else 14
        draw.ellipse((x - radius, rail_y - radius, x + radius, rail_y + radius), fill=fill, outline=INK, width=1)
        draw.text((x, 252), label, font=SMALL, fill=INK, anchor="mm")
    draw.text((545, 160), "ROUTE", font=MONO_BOLD, fill=GRAPHITE, anchor="mm")
    draw.text((1010, 160), "RERUN", font=MONO_BOLD, fill=GRAPHITE, anchor="mm")
    glow_dot(image, 1010, rail_y, color=GREEN)
    output = MEDIA / "chapter-pressure.webp"
    image.convert("RGB").save(output, "WEBP", quality=88, method=6)
    return output


def render_chapter_edges() -> Path:
    image, draw = chapter_base(False, "03", "UNSUPPORTED EDGES", "A1931 / NABU CAMERA / SELF-CONSISTENCY")
    draw.rounded_rectangle((400, 145, 620, 265), radius=14, outline=(*PORCELAIN_2, 130), width=2)
    draw.ellipse((475, 184, 495, 204), fill=LIME)
    draw.ellipse((525, 184, 545, 204), fill=LIME)
    draw.text((510, 280), "NATIVE INPUT", font=SMALL, fill=MUTED, anchor="mm")

    lens = (790, 205)
    for radius, color in ((65, GRAPHITE), (45, BLUE), (20, GREEN)):
        draw.ellipse((lens[0] - radius, lens[1] - radius, lens[0] + radius, lens[1] + radius), outline=color, width=4)
    draw.line((855, 205, 960, 205), fill=(*RED, 190), width=3)
    draw.line((960, 150, 960, 258), fill=(*RED, 220), width=3)
    draw.text((910, 280), "CAMERA / WIP", font=SMALL, fill=MUTED, anchor="mm")

    center = (1080, 205)
    for index in range(5):
        angle = index * math.tau / 5
        x = center[0] + math.cos(angle) * 72
        y = center[1] + math.sin(angle) * 50
        draw.line((*center, x, y), fill=(*MUTED, 75), width=1)
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=GREEN if index == 2 else GRAPHITE)
    draw.text((1080, 280), "PROVISIONAL BELIEF", font=SMALL, fill=MUTED, anchor="mm")
    output = MEDIA / "chapter-edges.webp"
    image.convert("RGB").save(output, "WEBP", quality=88, method=6)
    return output


def render_contact_sheet() -> Path:
    sheet = Image.new("RGB", (600, 4 * 215), INK)
    for index, renderer in enumerate(SCENES):
        frame = renderer(0.72).convert("RGB").resize((600, 215), Image.Resampling.LANCZOS)
        sheet.paste(frame, (0, index * 107 if index < 4 else (index - 4) * 107 + 430))
    # A readable two-column proof sheet for local review only.
    sheet = Image.new("RGB", (1200, 860), INK)
    for index, renderer in enumerate(SCENES):
        frame = renderer(0.72).convert("RGB").resize((600, 215), Image.Resampling.LANCZOS)
        sheet.paste(frame, ((index % 2) * 600, (index // 2) * 215))
    output = MEDIA / "system-loop-contact-sheet.jpg"
    sheet.save(output, quality=90)
    return output


def render() -> list[Path]:
    MEDIA.mkdir(parents=True, exist_ok=True)
    return [
        render_animation(),
        render_chapter_intent(),
        render_chapter_pressure(),
        render_chapter_edges(),
    ]


if __name__ == "__main__":
    for result in render():
        print(f"Rendered {result.name} ({result.stat().st_size / 1024:.1f} KiB)")
