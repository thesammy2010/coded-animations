# Coded Animations

This repo is for me to use code to create animations with [Manim](https://www.manim.community/).

## Setup

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
uv run pre-commit install
```

Render settings (quality, output format, output directory) are configured in `manim.cfg`.

## Project structure

- `example.py` — example scenes (`HelloWorld`, `SimpleCircle`, `CircleToSquare`) used for learning/reference.
- `projects/d365/` — scenes and helper scripts for a specific "365 days" project:
  - `anniversary.py` — title-card scene with animated text.
  - `collage.py` — scatters a set of photos across the frame.
  - `photo_showcase.py` — Ken Burns-style showcase of 2-3 photos.
  - `select_diverse_images.py` — standalone helper that picks a visually diverse subset of images from a directory (via perceptual hashing + color histograms), for feeding into `collage.py`.

## Running scenes

Each scene file can be rendered directly with `manim`, e.g.:

```bash
uv run manim -pqh example.py HelloWorld
```

Or run the file directly, which shells out to `manim` with sensible default flags:

```bash
uv run python example.py
```

### `projects/d365` scripts

These scripts take file paths as CLI arguments instead of hardcoded paths.

**`select_diverse_images.py`** — picks diverse images from a source directory:

```bash
uv run python projects/d365/select_diverse_images.py /path/to/photos \
  --output-file /tmp/selected_photos.txt \
  --count 150
```

**`collage.py`** — renders the photos listed in a file (one path per line, e.g. produced by `select_diverse_images.py`) scattering across the frame:

```bash
uv run python projects/d365/collage.py --photos-file /tmp/selected_photos.txt
```

**`photo_showcase.py`** — renders a Ken Burns-style showcase of 2-3 specific photos:

```bash
uv run python projects/d365/photo_showcase.py /path/to/photo1.jpg /path/to/photo2.jpg /path/to/photo3.jpg
```

**`anniversary.py`** — no file inputs, just run it directly:

```bash
uv run python projects/d365/anniversary.py
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```
