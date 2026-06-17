# Soluna Quizzes

Turning Instagram quiz videos into playable web quizzes — semi-automatically.

**▶ Play here: https://carefulcamel61097.github.io/soluna-quizzes/**

## Credit

**All the quiz ideas, questions, and visuals originate from
[@solunaaaa16](https://www.instagram.com/solunaaaa16/) on Instagram.** Full credit goes to them.

This project is **not** trying to steal, monetise, or replace their work, and it is **not** a
public republishing of it. It's a small personal tool that reformats their videos into a
self-paced web version so I can share a single link with a tiny circle of **family and friends**
(my dad especially loves these). If you enjoy these quizzes, please go follow and watch the
originals — that's the whole point. If the creator would prefer this not exist, I'll take it down.

## What this is

[@solunaaaa16](https://www.instagram.com/solunaaaa16/) posts videos of a guy working through
quizzes (geography, history, visual puzzles). This project turns those videos into clean,
self-paced web quizzes hosted on GitHub Pages. Each quiz shows a question and a visual, and a
**Show answer** button reveals the answer when you're ready — no typing, no scoring, just
browse and guess at your own pace.

> Adapted for **private family/friends use**, not republishing. The original video footage is
> not committed to this repo — only the still frames needed for each question.

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
