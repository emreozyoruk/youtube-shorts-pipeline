# Verticals v3 — AI YouTube Shorts Generator

**Fully automated YouTube Shorts pipeline with GUI, multi-language support, and niche intelligence.**

> Topic in. Published Short out. Any niche. Any language. ~$0.11 per video.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey)

## What It Does

One click generates a complete YouTube Short:

1. **Researches** your topic via DuckDuckGo
2. **Writes** a hook-driven script using AI (Claude/GPT/Gemini)
3. **Generates** cinematic b-roll images via DALL-E 3
4. **Records** natural voiceover (300+ voices, 9 languages)
5. **Burns** word-level subtitles directly into the video
6. **Generates** a thumbnail with text overlay
7. **Uploads** to YouTube with title, description, tags & captions

All in ~3 minutes. Fully automated.

## GUI

A native Python desktop GUI for non-technical users:

```bash
python3 gui.py
```

Features:
- Topic input
- Auto-detect niche from topic (GPT-4o-mini)
- Language selector (9 languages including Turkish)
- LLM provider selector (Claude / OpenAI / Gemini)
- YouTube privacy selector (Public / Private / Unlisted)
- Upload toggle
- Real-time log streaming
- Copy logs & clear buttons

## CLI

```bash
python3 -m verticals run --news "Your topic here" --niche tech --lang en --provider claude
```

### Available Options

| Flag | Options | Default |
|------|---------|---------|
| `--news` | Your topic/headline | Required |
| `--niche` | tech, gaming, finance, fitness, cooking, travel, science, etc. | general |
| `--lang` | en, tr, hi, es, pt, de, fr, ja, ko | en |
| `--provider` | claude, openai, gemini, ollama | claude |
| `--voice` | edge, elevenlabs, say | edge |
| `--platform` | shorts, reels, tiktok, all | shorts |
| `--dry-run` | Script only, no video | false |

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/emreozyoruk/youtube-shorts-pipeline.git
cd youtube-shorts-pipeline
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example env file:

```bash
cp .env.example .env
```

Edit `.env` with your API keys. Or run the interactive setup:

```bash
python3 -m verticals
```

First run triggers a setup wizard that saves keys to `~/.verticals/config.json` (file permissions: 0600).

**Where to get API keys:**

| Provider | Get Key | Used For |
|----------|---------|----------|
| Anthropic | [console.anthropic.com](https://console.anthropic.com/) | Script writing (best quality) |
| OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) | Script writing + DALL-E images + thumbnails |
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/apikey) | Script writing + Imagen |

**Edge TTS is free** — no API key needed for voiceover (300+ voices).

### 3. YouTube Upload Setup (Optional)

```bash
python3 scripts/setup_youtube_oauth.py
```

This requires a Google Cloud project with YouTube Data API v3 enabled:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 credentials** (Desktop app)
5. Download `client_secret.json` to `~/.verticals/`
6. Run the setup script — it opens a browser for authorization
7. Token is saved to `~/.verticals/youtube_token.json`

### 4. Run

**GUI:**
```bash
python3 gui.py
```

**CLI:**
```bash
python3 -m verticals run --news "AI is changing everything" --niche tech --lang en
```

## How It Works

```
TOPIC → RESEARCH → SCRIPT → IMAGES → VOICE → CAPTIONS → ASSEMBLE → UPLOAD
         DuckDuckGo  Claude    DALL-E   Edge TTS  Whisper   ffmpeg     YouTube
                     /GPT/     /Gemini  /11Labs            +moviepy
                     Gemini
```

### Niche Intelligence

15 built-in niches shape every stage of the pipeline:

| Niche | Script Tone | Visual Style |
|-------|-------------|--------------|
| Tech | Fast, fact-dense, opinionated | Dark, neon, futuristic |
| Finance | Data-driven, skeptical | Charts, numbers, clean |
| Cooking | Warm, instructional | Food photography, bright |
| True Crime | Suspenseful, dark | Cinematic, moody |
| Science | Curious, explanatory | Diagrams, space, labs |

Each niche controls: script tone, hook patterns, visual vocabulary, music mood, caption style, and thumbnail strategy.

## Cost Per Video

| Tier | Stack | Cost |
|------|-------|------|
| Premium | Claude + DALL-E + ElevenLabs | ~$0.15 |
| Standard | Claude + DALL-E + Edge TTS | ~$0.11 |
| Budget | GPT-4o-mini + DALL-E + Edge TTS | ~$0.06 |
| Free | Ollama + Pexels + Edge TTS | $0.00 |

## Requirements

- Python 3.10+
- ffmpeg
- At least one LLM API key (Anthropic, OpenAI, or Gemini)

### Install ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

## Project Structure

```
youtube-shorts-pipeline/
├── gui.py                  # Desktop GUI (CustomTkinter)
├── verticals/
│   ├── __main__.py         # CLI entry point
│   ├── draft.py            # Script generation with niche intelligence
│   ├── broll.py            # Image generation (DALL-E / Gemini)
│   ├── tts.py              # Text-to-speech (Edge TTS / ElevenLabs)
│   ├── captions.py         # Whisper word-level timestamps
│   ├── assemble.py         # ffmpeg + moviepy video assembly
│   ├── thumbnail.py        # DALL-E thumbnail + text overlay
│   ├── upload.py           # YouTube API upload
│   ├── research.py         # DuckDuckGo fact research
│   ├── niche.py            # Niche profile loader
│   ├── llm.py              # Multi-provider LLM calls
│   └── config.py           # Configuration management
├── niches/                 # 15 YAML niche profiles
├── scripts/
│   └── setup_youtube_oauth.py
├── requirements.txt
└── .env.example
```

## Security

- API keys are stored in `~/.verticals/config.json` with 0600 permissions (owner-only)
- YouTube OAuth tokens are stored in `~/.verticals/youtube_token.json`
- No credentials are committed to the repository
- `.gitignore` excludes all sensitive files

## Supported Languages

| Language | Code | Voice |
|----------|------|-------|
| English | en | en-US-GuyNeural |
| Turkish | tr | tr-TR-AhmetNeural |
| Hindi | hi | hi-IN-MadhurNeural |
| Spanish | es | es-MX-JorgeNeural |
| Portuguese | pt | pt-BR-AntonioNeural |
| German | de | de-DE-ConradNeural |
| French | fr | fr-FR-HenriNeural |
| Japanese | ja | ja-JP-KeitaNeural |
| Korean | ko | ko-KR-InJoonNeural |

## License

MIT — See [LICENSE](LICENSE) for details.

## Author

Built by [Emre Ozyoruk](https://github.com/emreozyoruk) — Software Engineer, Full Stack & AI.
