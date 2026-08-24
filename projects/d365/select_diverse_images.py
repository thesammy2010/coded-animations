"""
Diverse Image Selection Algorithm

This script selects visually diverse images from a directory using perceptual hashing
and color histogram analysis to avoid picking similar-looking photos.

Algorithm:
1. Scan all images in the source directory
2. For each image, compute:
   - Average Hash (aHash): Resizes image to 8x8, converts to grayscale,
     computes mean, creates 64-bit hash based on pixels above/below mean
   - Color Histogram: 16-bin histogram for each RGB channel (48 values total)
3. Start with a random seed image
4. Iteratively select the next image that is MOST different from all already selected:
   - Compute minimum Hamming distance (for aHash) to any selected image
   - Images with higher minimum distance are more "unique"
5. Skip images that are too similar (below threshold)
6. Continue until we have desired count or run out of diverse images

This approach ensures we get a varied collage rather than clusters of similar shots.
"""

import argparse
import random
import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def compute_average_hash(img: Image.Image, hash_size: int = 8) -> int:
    """
    Compute average hash (aHash) for an image.
    - Resize to hash_size x hash_size
    - Convert to grayscale
    - Compute mean pixel value
    - Create hash: 1 if pixel > mean, else 0
    """
    img = img.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())
    mean = sum(pixels) / len(pixels)
    return sum(1 << i for i, p in enumerate(pixels) if p > mean)


def compute_color_histogram(img: Image.Image, bins: int = 16) -> list[float]:
    """
    Compute normalized color histogram.
    - Resize for speed
    - Get histogram for R, G, B channels
    - Normalize to 0-1 range
    """
    img = img.convert("RGB").resize((64, 64), Image.Resampling.LANCZOS)
    hist = img.histogram()
    # histogram() returns 256 bins per channel for RGB = 768 values
    # We'll downsample to 'bins' per channel
    r_hist = hist[0:256]
    g_hist = hist[256:512]
    b_hist = hist[512:768]

    def downsample(h, target_bins):
        step = 256 // target_bins
        return [sum(h[i : i + step]) for i in range(0, 256, step)]

    combined = downsample(r_hist, bins) + downsample(g_hist, bins) + downsample(b_hist, bins)
    total = sum(combined) or 1
    return [v / total for v in combined]


def hamming_distance(hash1: int, hash2: int) -> int:
    """Count differing bits between two hashes."""
    return bin(hash1 ^ hash2).count("1")


def histogram_distance(hist1: list[float], hist2: list[float]) -> float:
    """Compute L1 distance between histograms (0 to 2 range)."""
    return sum(abs(a - b) for a, b in zip(hist1, hist2, strict=True))


def load_image_data(path: Path) -> dict | None:
    """Load image and compute hashes. Returns None if image can't be loaded."""
    try:
        with Image.open(path) as img:
            # Skip very small images
            if img.width < 100 or img.height < 100:
                return None
            return {
                "path": path,
                "ahash": compute_average_hash(img),
                "color_hist": compute_color_histogram(img),
            }
    except Exception as e:
        print(f"  Skipping {path.name}: {e}", file=sys.stderr)
        return None


def select_diverse_images(
    image_data: list[dict],
    count: int,
    min_hash_distance: int = 5,  # out of 64 bits (lowered to get more images)
    min_hist_distance: float = 0.2,  # out of 2.0 (lowered to get more images)
) -> list[Path]:
    """
    Select diverse images using greedy farthest-point sampling.

    For each iteration, pick the image that maximizes minimum distance
    to all already-selected images.
    """
    if not image_data:
        return []

    selected = []
    selected_data = []

    # Start with random seed
    seed_idx = random.randint(0, len(image_data) - 1)
    selected.append(image_data[seed_idx]["path"])
    selected_data.append(image_data[seed_idx])
    remaining = [d for i, d in enumerate(image_data) if i != seed_idx]

    print(f"  Seed image: {selected[0].name}", file=sys.stderr)

    while len(selected) < count and remaining:
        best_candidate = None
        best_min_distance = -1
        best_idx = -1

        for idx, candidate in enumerate(remaining):
            # Find minimum distance to any selected image
            min_dist = float("inf")
            for sel in selected_data:
                h_dist = hamming_distance(candidate["ahash"], sel["ahash"])
                c_dist = histogram_distance(candidate["color_hist"], sel["color_hist"])
                # Combine distances (normalize hamming to 0-1 range, hist is 0-2)
                combined = (h_dist / 64) + (c_dist / 2)
                min_dist = min(min_dist, combined)

            # Check if this candidate is sufficiently different
            h_dist_to_nearest = min(
                hamming_distance(candidate["ahash"], s["ahash"]) for s in selected_data
            )
            c_dist_to_nearest = min(
                histogram_distance(candidate["color_hist"], s["color_hist"]) for s in selected_data
            )

            if h_dist_to_nearest < min_hash_distance or c_dist_to_nearest < min_hist_distance:
                continue  # Too similar, skip

            if min_dist > best_min_distance:
                best_min_distance = min_dist
                best_candidate = candidate
                best_idx = idx

        if best_candidate is None:
            print(
                f"  Stopping early: no more sufficiently diverse images (got {len(selected)})",
                file=sys.stderr,
            )
            break

        selected.append(best_candidate["path"])
        selected_data.append(best_candidate)
        remaining.pop(best_idx)

        if len(selected) % 20 == 0:
            print(f"  Selected {len(selected)} images...", file=sys.stderr)

    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Select a visually diverse set of images from a directory."
    )
    parser.add_argument("source_dir", type=Path, help="Directory containing source images")
    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        default=Path("/tmp/selected_photos.txt"),
        help="File to write the selected image paths to (default: %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=150,
        help="Number of diverse images to select (default: %(default)s)",
    )
    args = parser.parse_args()

    source_dir = args.source_dir
    output_file = args.output_file
    target_count = args.count

    print("Scanning for images...", file=sys.stderr)
    image_files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        image_files.extend(source_dir.glob(ext))

    # Filter out thumbnails
    image_files = [f for f in image_files if "thumbnail" not in f.name.lower()]
    print(f"Found {len(image_files)} images", file=sys.stderr)

    print("Computing image hashes (this may take a moment)...", file=sys.stderr)
    image_data = []
    for i, path in enumerate(image_files):
        if i % 100 == 0 and i > 0:
            print(f"  Processed {i}/{len(image_files)}...", file=sys.stderr)
        data = load_image_data(path)
        if data:
            image_data.append(data)

    print(f"Successfully loaded {len(image_data)} images", file=sys.stderr)

    print(f"Selecting {target_count} diverse images...", file=sys.stderr)
    selected = select_diverse_images(image_data, target_count)

    print(f"\nSelected {len(selected)} diverse images", file=sys.stderr)

    # Write to output file
    with open(output_file, "w") as f:
        for path in selected:
            f.write(f"{path}\n")

    print(f"Saved to {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
