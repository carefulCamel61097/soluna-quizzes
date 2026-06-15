# Soluna Quizzes

Turning Instagram quiz videos into playable web quizzes — semi-automatically.

**▶ Play here: https://carefulcamel61097.github.io/soluna-quizzes/**

## What this is

[solunaaaa16](https://www.instagram.com/solunaaaa16/) on Instagram posts videos of a guy
working through quizzes (geography, trivia, visual puzzles). A lot of them are exactly the
kind of thing my dad enjoys.

This project takes those videos and turns them into clean, self-paced web quizzes hosted on
GitHub Pages, so I can share a single link with him. Each quiz shows a question and a visual,
and a **Show answer** button reveals the answer when he's ready — no typing, no scoring, just
browse and guess at your own pace.

> These quizzes are adapted from another creator's videos and are intended for **private family
> use**, not republishing. The original footage is not committed to this repo.

## The pipeline

Most of the work is automated; a human does a quick review pass where it matters.

1. **Download** the reel with [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) → an `.mp4`.
2. **Transcribe** the audio with [OpenAI Whisper](https://github.com/openai/whisper)
   (runs locally, free). This produces a timestamped transcript (`.srt`/`.json`).
   - The transcript reveals the quiz type, the questions, **and** the spoken answers.
3. **Extract frames** with [`ffmpeg`](https://ffmpeg.org/) at the timestamps where each
   question's visual is on screen.
   - Frames are chosen from the *guessing* phase, **before** the answer is revealed, so the
     answer isn't spoiled. Some videos burn the answer into the image as a caption — those
     frames are either cropped or replaced with an earlier clean frame.
4. **Assemble** each quiz into a small JSON file (question, image, answer) — this is the
   human review/correction step, where uncertain items get checked.
5. **Publish** to GitHub Pages from the [`docs/`](docs/) folder.

```
reel.mp4 ──yt-dlp──► .mp4 ──whisper──► transcript (+timestamps)
                       │                     │
                       └──────ffmpeg─────────┘  ──► frames
                                                     │
                                          review + assemble (JSON)
                                                     │
                                              GitHub Pages (docs/)
```

## Repo layout

```
docs/                          # the published site (GitHub Pages source)
  index.html                   # library landing page — lists all quizzes
  player.html                  # the quiz player
  css/ js/                     # styles and logic
  data/quizzes.json            # manifest of all quizzes
  data/<quiz-id>.json          # one file per quiz (questions + answers)
  img/<quiz-id>/               # that quiz's images
transcript/                    # Whisper output for source videos
quiz-draft.json                # working draft / review notes for a quiz
```

## Adding a new quiz

1. Run the pipeline on a new reel (download → transcribe → extract frames).
2. Drop the chosen images into `docs/img/<new-quiz-id>/`.
3. Create `docs/data/<new-quiz-id>.json` (copy `satellite-cities.json` as a template).
4. Add one entry for it to `docs/data/quizzes.json`.
5. Commit and push — GitHub Pages redeploys automatically.

## The player

- Image + prompt, with a **Show answer** button (or press **Space**).
- Move between questions with the on-screen arrows or the **← / →** arrow keys.
- No text input and no scoring by design — answers often have multiple valid spellings
  (e.g. historical figures), so self-checking keeps it simple and frustration-free.

## Running locally

The player loads data with `fetch()`, so it needs to be served over HTTP (not opened as a
`file://` path):

```
python -m http.server 8000
# then open http://localhost:8000/docs/
```
