from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1200
HEIGHT = 340
FRAMES_PER_CASE = 20
FRAME_DURATION_MS = 85

BACKGROUND = (5, 8, 8)
PANEL = (11, 16, 15)
PANEL_EDGE = (42, 52, 49)
TEXT = (237, 240, 232)
MUTED = (132, 143, 137)
LIME = (199, 255, 43)
BLUE = (103, 174, 255)

CASES = [
    {
        "id": "01 / FRADIUM",
        "constraint": ("MODEL MUST RUN", "ON-CHAIN"),
        "decision": ("RUST / ONNX / WASM", "STABLE MODEL STATE"),
        "evidence": ("WCHL 2025", "TRACK WINNER"),
    },
    {
        "id": "02 / MARKETIZEN",
        "constraint": ("1,000 VIRTUAL", "USERS"),
        "decision": ("GO / QUEUES / CACHE", "MODULAR MONOLITH"),
        "evidence": ("40,640 CHECKS", "PASSED"),
    },
    {
        "id": "03 / SPECHEAL",
        "constraint": ("A UI TEST FAILED", "BUT WHY?"),
        "decision": ("DOM / SCREENSHOT", "VALIDATE / RERUN"),
        "evidence": ("NO BLIND", "SELF-HEAL"),
    },
    {
        "id": "04 / A1931 BRIDGE",
        "constraint": ("UNSAFE BLE HID", "ON TWO SYSTEMS"),
        "decision": ("ANDROID RELAY", "WINDOWS UMDF"),
        "evidence": ("NATIVE", "TOUCHPAD"),
    },
]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        name,
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


DISPLAY = font("C:/Windows/Fonts/DejaVuSans-Bold.ttf", 34)
HEADING = font("C:/Windows/Fonts/DejaVuSans-Bold.ttf", 23)
MONO = font("C:/Windows/Fonts/CascadiaMono.ttf", 14)
MONO_BOLD = font("C:/Windows/Fonts/DejaVuSansMono-Bold.ttf", 14)
SMALL = font("C:/Windows/Fonts/CascadiaMono.ttf", 12)


def opacity_layer(alpha: int) -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, alpha))


def draw_base(frame_number: int, active_case: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image, "RGBA")

    for x in range(0, WIDTH, 40):
        draw.line((x, 0, x, HEIGHT), fill=(32, 43, 39, 42), width=1)
    for y in range(0, HEIGHT, 40):
        draw.line((0, y, WIDTH, y), fill=(32, 43, 39, 42), width=1)

    scan_y = (frame_number * 5) % HEIGHT
    draw.rectangle((0, scan_y, WIDTH, scan_y + 1), fill=(199, 255, 43, 22))

    draw.text((40, 27), "ARGA ADOLF LUMUNON", font=DISPLAY, fill=TEXT)
    draw.text(
        (1160, 35),
        "SOFTWARE ENGINEER / THE STACK FOLLOWS THE REQUIREMENT",
        font=MONO,
        fill=MUTED,
        anchor="ra",
    )
    draw.line((40, 78, 1160, 78), fill=(70, 82, 77, 150), width=1)

    labels = ((40, "CONSTRAINT"), (380, "DECISION SURFACE"), (810, "EVIDENCE"))
    for x, label in labels:
        draw.text((x, 101), label, font=MONO_BOLD, fill=LIME)

    panels = ((40, 126, 340, 250), (380, 126, 770, 250), (810, 126, 1160, 250))
    for panel in panels:
        draw.rounded_rectangle(panel, radius=7, fill=PANEL, outline=PANEL_EDGE, width=1)

    for index in range(len(CASES)):
        x = 40 + index * 23
        color = LIME if index == active_case else (57, 67, 63)
        draw.ellipse((x, 291, x + 7, 298), fill=color)

    draw.text((40, 310), "REAL CONSTRAINTS / PUBLIC BOUNDARIES / REPRODUCIBLE EVIDENCE", font=SMALL, fill=MUTED)
    draw.text((1160, 310), "LOOP / 04 SYSTEMS", font=SMALL, fill=BLUE, anchor="ra")
    return image


def draw_case(image: Image.Image, case: dict[str, object], alpha: int, progress: float) -> None:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    draw.text((40, 267), case["id"], font=MONO_BOLD, fill=(*BLUE, 255))

    columns = [
        (58, case["constraint"]),
        (398, case["decision"]),
        (828, case["evidence"]),
    ]
    for x, lines in columns:
        first, second = lines
        draw.text((x, 155), first, font=HEADING, fill=(*TEXT, 255))
        draw.text((x, 193), second, font=HEADING, fill=(*TEXT, 255))

    connectors = ((340, 188, 380, 188), (770, 188, 810, 188))
    for line in connectors:
        draw.line(line, fill=(*MUTED, 145), width=2)

    route_start = 340
    route_end = 810
    pulse_x = route_start + (route_end - route_start) * progress
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.ellipse((pulse_x - 10, 178, pulse_x + 10, 198), fill=(*LIME, 170))
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    layer = Image.alpha_composite(layer, glow)
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.ellipse((pulse_x - 3, 185, pulse_x + 3, 191), fill=(*LIME, 255))

    alpha_mask = Image.new("L", (WIDTH, HEIGHT), alpha)
    faded = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    faded.paste(layer, (0, 0), alpha_mask)
    image.paste(faded, (0, 0), faded)


def render() -> Path:
    frames: list[Image.Image] = []
    frame_number = 0

    for case_index, case in enumerate(CASES):
        for local_frame in range(FRAMES_PER_CASE):
            t = local_frame / (FRAMES_PER_CASE - 1)
            fade_in = min(1.0, t / 0.2)
            fade_out = min(1.0, (1.0 - t) / 0.2)
            alpha = int(255 * min(fade_in, fade_out))
            progress = min(1.0, max(0.0, (t - 0.12) / 0.76))

            frame = draw_base(frame_number, case_index)
            draw_case(frame, case, alpha, progress)
            palette_frame = frame.quantize(colors=48, method=Image.Quantize.MEDIANCUT)
            frames.append(palette_frame)
            frame_number += 1

    output = Path(__file__).resolve().parents[1] / "media" / "system-loop.gif"
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


if __name__ == "__main__":
    result = render()
    print(f"Rendered {result} ({result.stat().st_size / 1024:.1f} KiB)")
