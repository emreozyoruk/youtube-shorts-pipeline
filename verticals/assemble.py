"""ffmpeg video assembly — frames + voiceover + music + captions."""

from pathlib import Path

from .broll import animate_frame
from .config import MEDIA_DIR, run_cmd
from .log import log


def _parse_srt(srt_path: str) -> list[dict]:
    """Parse SRT file into list of {start, end, text}."""
    import re
    subs = []
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    blocks = re.split(r"\n\n+", content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        time_match = re.match(r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})", lines[1])
        if not time_match:
            continue
        def to_sec(t):
            t = t.replace(",", ".")
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        subs.append({
            "start": to_sec(time_match.group(1)),
            "end": to_sec(time_match.group(2)),
            "text": " ".join(lines[2:]).strip(),
        })
    return subs


def _burn_srt_subtitles(video_path: str, srt_path: str, output_path: str):
    """Burn SRT subtitles into video using moviepy + PIL."""
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip

    video = VideoFileClip(video_path)
    subs = _parse_srt(srt_path)

    text_clips = []
    for sub in subs:
        txt = TextClip(
            text=sub["text"],
            font_size=38,
            color="white",
            font="Arial-Bold",
            stroke_color="black",
            stroke_width=2,
            size=(video.w - 80, None),
            method="caption",
            text_align="center",
        )
        txt = txt.with_start(sub["start"]).with_end(sub["end"])
        txt = txt.with_position(("center", video.h - 150))
        text_clips.append(txt)

    final = CompositeVideoClip([video] + text_clips)
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=video.fps,
        logger=None,
    )
    video.close()


def get_audio_duration(path: Path) -> float:
    """Get duration of an audio file in seconds."""
    r = run_cmd(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture=True,
    )
    return float(r.stdout.strip())


def assemble_video(
    frames: list[Path],
    voiceover: Path,
    out_dir: Path,
    job_id: str,
    lang: str = "en",
    ass_path: str | None = None,
    music_path: str | None = None,
    duck_filter: str | None = None,
) -> Path:
    """Assemble final video from frames, voiceover, captions, and music."""
    log("Assembling video...")
    duration = get_audio_duration(voiceover)
    per_frame = duration / len(frames)
    effects = ["zoom_in", "pan_right", "zoom_out"]

    # Animate each frame with Ken Burns effect
    animated = []
    for i, frame in enumerate(frames):
        anim = out_dir / f"anim_{i}.mp4"
        animate_frame(frame, anim, per_frame + 0.1, effects[i % len(effects)])
        animated.append(anim)

    # Concat animated segments (escape single quotes for ffmpeg concat demuxer)
    concat_file = out_dir / "concat.txt"
    def _esc(p):
        return str(p).replace("'", "'\\''" )
    concat_file.write_text("\n".join(f"file '{_esc(p)}'" for p in animated))

    merged_video = out_dir / "merged_video.mp4"
    run_cmd([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(merged_video), "-y", "-loglevel", "quiet",
    ])

    # Build the final ffmpeg command with optional captions + music
    out_path = MEDIA_DIR / f"verticals_{job_id}_{lang}.mp4"

    # Find SRT file
    srt_path = None
    if ass_path:
        srt_candidate = str(ass_path).replace(".ass", ".srt")
        if Path(srt_candidate).exists():
            srt_path = srt_candidate

    # First: merge video + audio
    temp_out = out_dir / "temp_merged_av.mp4"
    if music_path and Path(music_path).exists():
        music_filter = f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{duration}"
        if duck_filter:
            music_filter += f",{duck_filter}"
        music_filter += "[music]"
        audio_filter = f"{music_filter};[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"

        cmd = [
            "ffmpeg", "-i", str(merged_video), "-i", str(voiceover),
            "-stream_loop", "-1", "-i", str(music_path),
            "-filter_complex", audio_filter,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest",
            str(temp_out), "-y", "-loglevel", "quiet",
        ]
    else:
        cmd = [
            "ffmpeg", "-i", str(merged_video), "-i", str(voiceover),
            "-c:v", "copy", "-c:a", "aac", "-shortest",
            str(temp_out), "-y", "-loglevel", "quiet",
        ]
    run_cmd(cmd)

    # Then: burn subtitles using Python (moviepy + PIL)
    if srt_path and Path(srt_path).exists():
        log("Burning subtitles into video...")
        try:
            _burn_srt_subtitles(str(temp_out), srt_path, str(out_path))
            temp_out.unlink(missing_ok=True)
        except Exception as e:
            log(f"Subtitle burn failed ({e}) — using video without burned subs")
            import shutil
            shutil.move(str(temp_out), str(out_path))
    else:
        import shutil
        shutil.move(str(temp_out), str(out_path))

    run_cmd(cmd)
    log(f"Video assembled: {out_path}")
    return out_path
