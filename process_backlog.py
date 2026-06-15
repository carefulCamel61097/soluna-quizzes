#!/usr/bin/env python3
"""
process_backlog.py

Walk the backlog of solunaaaa16 reels and, for each one, download the video
then transcribe it before moving on to the next. These are the two fully
automated steps of the pipeline; frame extraction + quiz assembly happen later
(with a human in the loop).

Reads the reel URLs from the "## Backlog" section of VIDEOS.md.

Output layout (videos/ and transcripts/ are git-ignored):
    videos/<shortcode>.mp4
    transcripts/<shortcode>.srt  (+ .json/.txt/.vtt/.tsv)

The script is idempotent: a reel whose transcript already exists is skipped, so
you can stop it (Ctrl-C) and re-run later without redoing finished work.

Usage:
    python process_backlog.py            # process the whole backlog
    python process_backlog.py <url> ...  # process only the given reel URL(s)
"""

import os
import re
import sys
import glob
import time
import random
import shutil
import subprocess

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(HERE, "videos")
TRANSCRIPTS_DIR = os.path.join(HERE, "transcripts")
BACKLOG_FILE = os.path.join(HERE, "VIDEOS.md")

WHISPER_MODEL = "small"      # tiny | base | small | medium | large (bigger = slower, more accurate)
WHISPER_LANG = "en"
MIN_DELAY_SEC = 20           # polite random pause between downloads
MAX_DELAY_SEC = 45

REEL_RE = re.compile(r"https://www\.instagram\.com/reel/([A-Za-z0-9_-]+)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def require_tool(name):
    """Return the path to a CLI tool or exit with a helpful message."""
    path = shutil.which(name)
    if path:
        return path
    print(f"ERROR: '{name}' not found on PATH.", file=sys.stderr)
    if name == "ffmpeg":
        print("  Install with:  winget install ffmpeg", file=sys.stderr)
    elif name == "yt-dlp":
        print("  Install with:  winget install yt-dlp   (or: pip install yt-dlp)", file=sys.stderr)
    elif name == "whisper":
        print("  Install with:  pip install openai-whisper", file=sys.stderr)
    sys.exit(1)


def read_backlog_urls():
    """Extract reel URLs from the '## Backlog' section of VIDEOS.md."""
    if not os.path.exists(BACKLOG_FILE):
        print(f"ERROR: {BACKLOG_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(BACKLOG_FILE, encoding="utf-8") as f:
        text = f.read()
    # Only look after the "## Backlog" heading so the "Done" reel is excluded.
    marker = text.find("## Backlog")
    section = text[marker:] if marker != -1 else text
    urls, seen = [], set()
    for m in REEL_RE.finditer(section):
        sc = m.group(1)
        if sc not in seen:
            seen.add(sc)
            urls.append(f"https://www.instagram.com/reel/{sc}/")
    return urls


def shortcode_of(url):
    m = REEL_RE.search(url)
    return m.group(1) if m else None


def video_path(shortcode):
    matches = glob.glob(os.path.join(VIDEOS_DIR, f"{shortcode}.*"))
    return matches[0] if matches else None


def transcript_exists(shortcode):
    return bool(glob.glob(os.path.join(TRANSCRIPTS_DIR, f"{shortcode}.srt")))


def download(url, shortcode, ytdlp):
    """Download the reel to videos/<shortcode>.mp4. Returns True on success."""
    if video_path(shortcode):
        print(f"  video already present, skipping download")
        return True
    out_tmpl = os.path.join(VIDEOS_DIR, f"{shortcode}.%(ext)s")
    cmd = [ytdlp, "--no-playlist", "--retries", "3", "-o", out_tmpl, url]
    print(f"  downloading -> videos/{shortcode}.mp4")
    result = subprocess.run(cmd)
    if result.returncode != 0 or not video_path(shortcode):
        print(f"  !! download FAILED for {shortcode}", file=sys.stderr)
        return False
    return True


def transcribe(shortcode, whisper):
    """Transcribe videos/<shortcode>.* into transcripts/. Returns True on success."""
    if transcript_exists(shortcode):
        print(f"  transcript already present, skipping")
        return True
    vid = video_path(shortcode)
    if not vid:
        print(f"  !! no video to transcribe for {shortcode}", file=sys.stderr)
        return False
    cmd = [
        whisper, vid,
        "--model", WHISPER_MODEL,
        "--language", WHISPER_LANG,
        "--output_dir", TRANSCRIPTS_DIR,
        "--output_format", "all",
    ]
    print(f"  transcribing (model={WHISPER_MODEL}) ...")
    result = subprocess.run(cmd)
    if result.returncode != 0 or not transcript_exists(shortcode):
        print(f"  !! transcribe FAILED for {shortcode}", file=sys.stderr)
        return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ytdlp = require_tool("yt-dlp")
    whisper = require_tool("whisper")
    require_tool("ffmpeg")  # needed by both yt-dlp (merge) and whisper (audio)

    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

    # URLs from the command line override the backlog file.
    urls = sys.argv[1:] or read_backlog_urls()
    if not urls:
        print("No reel URLs found to process.")
        return

    total = len(urls)
    print(f"Processing {total} reel(s). Videos -> {VIDEOS_DIR}, transcripts -> {TRANSCRIPTS_DIR}\n")

    done, skipped, failed = [], [], []
    for i, url in enumerate(urls, 1):
        sc = shortcode_of(url)
        print(f"[{i}/{total}] {url}")
        if not sc:
            print("  !! could not parse shortcode, skipping", file=sys.stderr)
            failed.append(url)
            continue

        if transcript_exists(sc):
            print("  already finished (transcript exists), skipping\n")
            skipped.append(sc)
            continue

        newly_downloaded = not video_path(sc)
        if not download(url, sc, ytdlp):
            failed.append(sc)
            print()
            continue
        if not transcribe(sc, whisper):
            failed.append(sc)
            print()
            continue

        done.append(sc)
        print("  done\n")

        # Polite pause only after an actual network download, and not after the last item.
        if newly_downloaded and i < total:
            delay = random.randint(MIN_DELAY_SEC, MAX_DELAY_SEC)
            print(f"  (waiting {delay}s before next download)\n")
            time.sleep(delay)

    print("=" * 50)
    print(f"Finished. processed={len(done)}  skipped={len(skipped)}  failed={len(failed)}")
    if failed:
        print("Failed shortcodes:", ", ".join(failed))


if __name__ == "__main__":
    main()
