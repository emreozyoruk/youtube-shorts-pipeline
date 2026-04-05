"""Thumbnail generation — OpenAI DALL-E (16:9) + Pillow text overlay."""

import base64
import json
import os
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from .log import log
from .retry import with_retry

THUMB_WIDTH = 1280
THUMB_HEIGHT = 720


def _get_openai_key() -> str:
    val = os.environ.get("OPENAI_API_KEY")
    if val:
        return val
    cfg_path = Path.home() / ".verticals" / "config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        return cfg.get("openai_api_key", cfg.get("OPENAI_API_KEY", ""))
    return ""


@with_retry(max_retries=3, base_delay=2.0)
def _generate_thumb_image(prompt: str, output_path: Path, api_key: str):
    """Generate a 16:9 thumbnail via OpenAI DALL-E 3."""
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        json={
            "model": "dall-e-3",
            "prompt": f"YouTube thumbnail, 16:9 landscape, bold and eye-catching: {prompt}",
            "n": 1,
            "size": "1792x1024",
            "quality": "standard",
            "response_format": "b64_json",
        },
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=120,
    )
    if r.status_code != 200:
        try:
            detail = r.json().get("error", {}).get("message", r.text[:200])
        except Exception:
            detail = r.text[:200]
        raise RuntimeError(f"OpenAI DALL-E API {r.status_code}: {detail}")
    img_b64 = r.json()["data"][0]["b64_json"]
    output_path.write_bytes(base64.b64decode(img_b64))


def _overlay_title(image_path: Path, title: str, output_path: Path):
    """Overlay bold title text with drop shadow on the thumbnail."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    font_size = 64
    font = None
    for font_name in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    max_width = THUMB_WIDTH - 80
    lines = _wrap_text(draw, title, font, max_width)
    text_block = "\n".join(lines)

    bbox = draw.multiline_textbbox((0, 0), text_block, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (THUMB_WIDTH - text_w) // 2
    y = THUMB_HEIGHT - text_h - 60

    shadow_offset = 3
    draw.multiline_text(
        (x + shadow_offset, y + shadow_offset),
        text_block, fill=(0, 0, 0), font=font, align="center",
    )
    draw.multiline_text(
        (x, y), text_block, fill=(255, 255, 255), font=font, align="center",
    )

    img.save(output_path)


def _wrap_text(draw: ImageDraw.Draw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_thumbnail(draft: dict, out_dir: Path) -> Path:
    """Generate a YouTube thumbnail with OpenAI DALL-E + text overlay."""
    api_key = _get_openai_key()
    prompt = draft.get("thumbnail_prompt", "Cinematic YouTube thumbnail")
    title = draft.get("youtube_title", draft.get("news", ""))
    job_id = draft.get("job_id", "unknown")

    raw_path = out_dir / f"thumb_raw_{job_id}.png"
    final_path = out_dir / f"thumb_{job_id}.png"

    log("Generating thumbnail via OpenAI DALL-E...")
    _generate_thumb_image(prompt, raw_path, api_key)

    log("Adding title overlay...")
    _overlay_title(raw_path, title, final_path)

    log(f"Thumbnail saved: {final_path.name}")
    return final_path
