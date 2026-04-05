#!/usr/bin/env python3
"""Verticals — YouTube Shorts Generator GUI"""

import customtkinter as ctk
import threading
import subprocess
import sys
import json
from pathlib import Path

# Dark mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NICHES = [
    "auto-detect",
    "tech", "gaming", "finance", "fitness", "cooking",
    "travel", "true-crime", "science", "politics", "entertainment",
    "sports", "fashion", "education", "motivation", "comedy", "general",
]

LANGUAGES = [
    ("Türkçe", "tr"), ("English", "en"), ("हिन्दी", "hi"),
    ("Español", "es"), ("Português", "pt"), ("Deutsch", "de"),
    ("Français", "fr"), ("日本語", "ja"), ("한국어", "ko"),
]

PROVIDERS = ["claude", "openai", "gemini"]


def auto_detect_niche(topic: str) -> str:
    """Use a cheap LLM call to detect the best niche for a topic."""
    import os
    cfg_path = Path.home() / ".verticals" / "config.json"
    api_key = ""
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        api_key = cfg.get("openai_api_key", "")

    if not api_key:
        return "general"

    try:
        import requests
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You classify topics into content niches. Respond with ONLY the niche name, nothing else. Available niches: tech, gaming, finance, fitness, cooking, travel, true-crime, science, politics, entertainment, sports, fashion, education, motivation, comedy, general"},
                    {"role": "user", "content": f"Classify this topic: {topic}"}
                ],
                "max_tokens": 10,
                "temperature": 0,
            },
            timeout=15,
        )
        if r.status_code == 200:
            niche = r.json()["choices"][0]["message"]["content"].strip().lower().replace('"', '').replace("'", "")
            valid = ["tech", "gaming", "finance", "fitness", "cooking", "travel", "true-crime", "science", "politics", "entertainment", "sports", "fashion", "education", "motivation", "comedy", "general"]
            if niche in valid:
                return niche
    except Exception:
        pass
    return "general"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Verticals — AI YouTube Shorts Generator")
        self._set_appearance_mode("dark")
        self.geometry("1000x1000")
        self.minsize(800, 700)
        ctk.set_widget_scaling(1.3)
        ctk.set_window_scaling(1.3)

        # ─── Header ───
        header = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="🎬 Verticals",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header, text="AI YouTube Shorts Generator",
            font=ctk.CTkFont(size=13),
            text_color="#acacac"
        ).pack(side="left", padx=5)

        # ─── Scrollable Main Content ───
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=15)

        # Topic
        ctk.CTkLabel(main, text="Topic / News", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.topic_entry = ctk.CTkTextbox(main, height=80, corner_radius=8, font=ctk.CTkFont(size=13))
        self.topic_entry.pack(fill="x", pady=(0, 15))
        self.topic_entry.insert("1.0", "Türkiye'de yapay zeka sektörü hızla büyüyor")

        # Row: Niche + Language
        row1 = ctk.CTkFrame(main, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 15))

        niche_frame = ctk.CTkFrame(row1, fg_color="transparent")
        niche_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(niche_frame, text="Niche", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.niche_var = ctk.StringVar(value="auto-detect")
        self.niche_menu = ctk.CTkOptionMenu(niche_frame, variable=self.niche_var, values=NICHES, width=200)
        self.niche_menu.pack(anchor="w")

        lang_frame = ctk.CTkFrame(row1, fg_color="transparent")
        lang_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(lang_frame, text="Language", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.lang_var = ctk.StringVar(value="Türkçe")
        self.lang_menu = ctk.CTkOptionMenu(lang_frame, variable=self.lang_var, values=[l[0] for l in LANGUAGES], width=200)
        self.lang_menu.pack(anchor="w")

        # Row: LLM Provider + Privacy
        row2 = ctk.CTkFrame(main, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 15))

        llm_frame = ctk.CTkFrame(row2, fg_color="transparent")
        llm_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(llm_frame, text="LLM Provider", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.provider_var = ctk.StringVar(value="claude")
        self.provider_menu = ctk.CTkOptionMenu(llm_frame, variable=self.provider_var, values=PROVIDERS, width=200)
        self.provider_menu.pack(anchor="w")

        privacy_frame = ctk.CTkFrame(row2, fg_color="transparent")
        privacy_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(privacy_frame, text="YouTube Privacy", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.privacy_var = ctk.StringVar(value="private")
        self.privacy_menu = ctk.CTkOptionMenu(privacy_frame, variable=self.privacy_var, values=["public", "private", "unlisted"], width=200)
        self.privacy_menu.pack(anchor="w")

        # Upload checkbox
        self.upload_var = ctk.BooleanVar(value=True)
        self.upload_check = ctk.CTkCheckBox(
            main, text="Upload to YouTube after generation", variable=self.upload_var,
            font=ctk.CTkFont(size=13)
        )
        self.upload_check.pack(anchor="w", pady=(0, 15))

        # ─── Generate Button ───
        self.generate_btn = ctk.CTkButton(
            main, text="🚀 Generate & Publish",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50, corner_radius=10,
            fg_color="#6549d5", hover_color="#4a35a0",
            command=self.start_generation,
        )
        self.generate_btn.pack(fill="x", pady=(0, 15))

        # ─── Progress ───
        self.progress = ctk.CTkProgressBar(main, mode="indeterminate", height=6)
        self.progress.pack(fill="x", pady=(0, 10))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            main, text="Ready", font=ctk.CTkFont(size=12),
            text_color="#acacac"
        )
        self.status_label.pack(anchor="w", pady=(0, 5))

        # ─── Log Output ───
        log_header = ctk.CTkFrame(main, fg_color="transparent")
        log_header.pack(fill="x", pady=(5, 5))
        ctk.CTkLabel(log_header, text="Log", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self.copy_btn = ctk.CTkButton(
            log_header, text="📋 Copy Logs", width=120, height=30,
            font=ctk.CTkFont(size=12), corner_radius=6,
            fg_color="#333344", hover_color="#444466",
            command=self.copy_logs,
        )
        self.copy_btn.pack(side="right")

        self.clear_btn = ctk.CTkButton(
            log_header, text="🗑️ Clear", width=80, height=30,
            font=ctk.CTkFont(size=12), corner_radius=6,
            fg_color="#333344", hover_color="#444466",
            command=self.clear_logs,
        )
        self.clear_btn.pack(side="right", padx=(0, 8))

        self.log_box = ctk.CTkTextbox(main, height=350, corner_radius=8, font=ctk.CTkFont(family="monospace", size=11), wrap="word")
        self.log_box.pack(fill="both", expand=True, pady=(0, 10))
        self.log_box.configure(state="disabled")

        self.running = False

    def copy_logs(self):
        self.log_box.configure(state="normal")
        text = self.log_box.get("1.0", "end").strip()
        self.log_box.configure(state="disabled")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.copy_btn.configure(text="✅ Copied!")
        self.after(2000, lambda: self.copy_btn.configure(text="📋 Copy Logs"))

    def clear_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def get_lang_code(self):
        name = self.lang_var.get()
        for n, code in LANGUAGES:
            if n == name:
                return code
        return "en"

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def set_status(self, text):
        self.status_label.configure(text=text)

    def start_generation(self):
        if self.running:
            return

        topic = self.topic_entry.get("1.0", "end").strip()
        if not topic:
            self.set_status("⚠️ Please enter a topic!")
            return

        self.running = True
        self.generate_btn.configure(state="disabled", text="⏳ Generating...")
        self.progress.start()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        # Ensure config uses openai for images
        cfg_path = Path.home() / ".verticals" / "config.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            cfg["image_provider"] = "openai"
            cfg_path.write_text(json.dumps(cfg, indent=2))

        thread = threading.Thread(target=self.run_pipeline, args=(topic,), daemon=True)
        thread.start()

    def run_pipeline(self, topic):
        niche = self.niche_var.get()
        lang = self.get_lang_code()
        provider = self.provider_var.get()
        upload = self.upload_var.get()
        privacy = self.privacy_var.get()

        # Auto-detect niche if selected
        if niche == "auto-detect":
            self.after(0, self.set_status, "🧠 Auto-detecting niche...")
            self.after(0, self.log, "🧠 Auto-detecting niche from topic...")
            niche = auto_detect_niche(topic)
            self.after(0, self.log, f"   → Detected: {niche}")
            self.after(0, lambda: self.niche_var.set(niche))

        self.after(0, self.set_status, "📝 Researching & writing script...")
        self.after(0, self.log, f"Topic: {topic}")
        self.after(0, self.log, f"Niche: {niche} | Lang: {lang} | LLM: {provider}")
        self.after(0, self.log, f"Privacy: {privacy} | Upload: {upload}")
        self.after(0, self.log, "─" * 50)

        project_dir = Path(__file__).parent
        cmd = [
            sys.executable, "-u", "-m", "verticals", "run",
            "--news", topic,
            "--niche", niche,
            "--lang", lang,
            "--provider", provider,
        ]

        # Set env vars for the subprocess
        env = dict(__import__("os").environ)
        env["VERTICALS_PRIVACY"] = privacy
        env["PYTHONUNBUFFERED"] = "1"

        # If upload is disabled, skip upload step but still produce video
        if not upload:
            env["VERTICALS_SKIP_UPLOAD"] = "1"

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(project_dir),
                bufsize=0,
                env=env,
            )

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                line = line.strip()
                if line:
                    self.after(0, self.log, line)
                    if "Researching" in line:
                        self.after(0, self.set_status, "🔍 Researching topic...")
                    elif "Calling LLM" in line:
                        self.after(0, self.set_status, "📝 Writing script...")
                    elif "Draft saved" in line:
                        self.after(0, self.set_status, "✅ Script ready!")
                    elif "b-roll frame" in line:
                        self.after(0, self.set_status, "🎨 Generating images...")
                    elif "voiceover" in line.lower():
                        self.after(0, self.set_status, "🎙️ Generating voiceover...")
                    elif "Whisper" in line:
                        self.after(0, self.set_status, "📝 Generating captions...")
                    elif "thumbnail" in line.lower():
                        self.after(0, self.set_status, "🖼️ Generating thumbnail...")
                    elif "Assembling" in line:
                        self.after(0, self.set_status, "🎬 Assembling video...")
                    elif "Uploading" in line:
                        self.after(0, self.set_status, "📤 Uploading to YouTube...")
                    elif "youtu.be" in line or "Done!" in line:
                        self.after(0, self.set_status, f"✅ {line}")

            process.wait()

            if process.returncode == 0:
                self.after(0, self.set_status, "✅ Done! Video generated successfully!")
                self.after(0, self.log, "\n🎉 SUCCESS!")
            else:
                self.after(0, self.set_status, f"❌ Error (exit code {process.returncode})")
                self.after(0, self.log, f"\n❌ Process exited with code {process.returncode}")

        except Exception as e:
            self.after(0, self.set_status, f"❌ Error: {str(e)}")
            self.after(0, self.log, f"\n❌ Exception: {str(e)}")

        finally:
            self.running = False
            self.after(0, self.progress.stop)
            self.after(0, self.progress.set, 0)
            self.after(0, lambda: self.generate_btn.configure(state="normal", text="🚀 Generate & Publish"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
