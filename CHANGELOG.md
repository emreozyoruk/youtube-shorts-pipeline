# Changelog

## [3.1.0] — 2026-04-05

### Added
- **Desktop GUI** — CustomTkinter app with real-time log streaming, niche/language/provider selectors, YouTube privacy control
- **Turkish language support** — Edge TTS `tr-TR-AhmetNeural` voice, Turkish script generation via LLM instruction
- **Auto-detect niche** — GPT-4o-mini classifies topic into the best matching niche automatically
- **OpenAI DALL-E 3 images** — B-roll and thumbnail generation via DALL-E 3 API
- **Burned-in subtitles** — moviepy + PIL based subtitle rendering, no libass/ffmpeg filter dependency
- **YouTube privacy control** — Public/Private/Unlisted selector in GUI and CLI
- **9 language support** — English, Turkish, Hindi, Spanish, Portuguese, German, French, Japanese, Korean

### Changed
- Image generation now supports OpenAI DALL-E 3 as primary provider
- Thumbnail generation uses OpenAI DALL-E 3 instead of Gemini
- Niche voice config no longer overrides language-specific voice selection
- Upload module accepts privacy parameter

## [3.0.0] — 2026-04-02

### Core Pipeline
- **Niche Intelligence** — 15 built-in YAML profiles that shape every pipeline stage
- **Multi-provider LLM** — Claude, Gemini, GPT, Ollama support
- **Multi-provider TTS** — Edge TTS (free default), ElevenLabs, Kokoro, macOS say
- **Multi-provider images** — DALL-E 3, Gemini Imagen, Pexels stock footage
- **Research gate** — DuckDuckGo search + web scraping for fact-checked scripts
- **Ken Burns animation** — Zoom/pan effects on b-roll frames
- **Word-level captions** — Whisper timestamps with ASS/SRT output
- **Background music** — Mood-matched with automatic voice ducking
- **YouTube upload** — OAuth2, metadata, captions, thumbnails
- **Topic engine** — Reddit, RSS, Google Trends discovery
- **Resume capability** — Stage tracking for interrupted pipelines
