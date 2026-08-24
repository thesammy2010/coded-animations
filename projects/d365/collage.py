import os
import random
from pathlib import Path

from manim import *

DEFAULT_PHOTOS_FILE = "/tmp/selected_photos.txt"


class PhotoCollage(Scene):
    """Photo collage - images appear randomly and scatter across the frame."""

    def construct(self):
        self.camera.background_color = BLACK

        photos_file = Path(os.environ.get("PHOTOS_FILE", DEFAULT_PHOTOS_FILE))
        image_paths = [
            line.strip() for line in photos_file.read_text().splitlines() if line.strip()
        ]

        random.shuffle(image_paths)

        # Target size with max 10% variation
        base_size = 1.6  # Larger images to fill more space
        size_variation = 0.1

        frame_width = config.frame_width
        frame_height = config.frame_height

        images = []
        target_positions = []
        target_sizes = []

        for path in image_paths:
            try:
                img = ImageMobject(path)

                # Random size within 10% of base
                size_multiplier = random.uniform(1 - size_variation, 1 + size_variation)
                target_size = base_size * size_multiplier
                target_sizes.append(target_size)

                # Scale image to target size (maintaining aspect ratio)
                if img.width > img.height:
                    img.width = target_size
                else:
                    img.height = target_size

                # Random position anywhere on screen (allowing overlap)
                # Reduced padding to let images go closer to edges
                padding = 0.2
                x = random.uniform(-frame_width / 2 + padding, frame_width / 2 - padding)
                y = random.uniform(-frame_height / 2 + padding, frame_height / 2 - padding)
                target_positions.append(np.array([x, y, 0]))

                # Start off-screen at random edge
                edge = random.choice(["top", "bottom", "left", "right"])
                if edge == "top":
                    start_pos = [random.uniform(-8, 8), 6, 0]
                elif edge == "bottom":
                    start_pos = [random.uniform(-8, 8), -6, 0]
                elif edge == "left":
                    start_pos = [-10, random.uniform(-5, 5), 0]
                else:
                    start_pos = [10, random.uniform(-5, 5), 0]

                img.move_to(start_pos)
                img.set_opacity(0)
                images.append(img)

            except Exception as e:
                print(f"Skipping {path}: {e}")
                continue

        # Add all images to scene
        for img in images:
            self.add(img)

        # Animate images appearing randomly over ~8 seconds
        # Group into waves but randomize within each wave
        total_duration = 8.0

        # Create staggered animations with random delays
        animations_with_delays = []
        for img, pos in zip(images, target_positions, strict=True):
            # Random delay between 0 and total_duration - 1 (leave 1 sec for animation)
            delay = random.uniform(0, total_duration - 1.5)
            animations_with_delays.append((delay, img, pos))

        # Sort by delay
        animations_with_delays.sort(key=lambda x: x[0])

        # Play animations in small overlapping batches
        batch = []
        batch_delays = []

        for delay, img, pos in animations_with_delays:
            batch.append((img, pos))
            batch_delays.append(delay)

            # When batch is full or delay gap is large, play the batch
            if batch and (len(batch) >= 8 or delay - batch_delays[0] > 0.5):
                anims = [img.animate.move_to(pos).set_opacity(1) for img, pos in batch]
                self.play(
                    *anims,
                    run_time=random.uniform(0.4, 0.8),
                    rate_func=smooth,
                )
                batch = []
                batch_delays = []

        # Play remaining
        if batch:
            anims = [img.animate.move_to(pos).set_opacity(1) for img, pos in batch]
            self.play(*anims, run_time=0.6, rate_func=smooth)

        self.wait(2)


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="Render the photo collage animation.")
    parser.add_argument(
        "--photos-file",
        default=DEFAULT_PHOTOS_FILE,
        help="Text file with one image path per line (default: %(default)s)",
    )
    args = parser.parse_args()

    env = os.environ.copy()
    env["PHOTOS_FILE"] = args.photos_file
    subprocess.run(["manim", "-pqh", __file__, "PhotoCollage"], env=env)
