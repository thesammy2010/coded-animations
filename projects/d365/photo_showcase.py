"""
Photo Showcase Template

Displays 2-3 photos with slow Ken Burns-style animations.
Layout adapts based on photo orientations.
"""

import json
import os
import random

from manim import *

DEFAULT_IMAGE_PATHS = [
    "/tmp/photos_converted/IMG_6738.jpg",
    "/tmp/photos_converted/IMG_0006.jpg",
    "/tmp/photos_converted/IMG_0011.jpg",
]


class PhotoShowcase(Scene):
    """
    Showcase 2-3 photos with slow Ken Burns-style animations.
    """

    def construct(self):
        self.camera.background_color = BLACK

        env_paths = os.environ.get("SHOWCASE_IMAGE_PATHS")
        paths = json.loads(env_paths) if env_paths else DEFAULT_IMAGE_PATHS
        images_data = []

        # Load images and detect orientation
        for path in paths:
            img = ImageMobject(path)
            is_portrait = img.height > img.width
            images_data.append({"img": img, "portrait": is_portrait})

        n = len(images_data)

        # Count portraits vs landscapes
        portrait_count = sum(1 for d in images_data if d["portrait"])

        # Layout - dynamic, staggered positions with slight tilts
        if n == 3:
            if portrait_count == 3:
                # 3 portraits: staggered heights, slight rotations
                positions = [
                    {"pos": [-4.2, -0.4, 0], "scale": 5.0, "rot": -4},
                    {"pos": [0, 0.5, 0], "scale": 5.5, "rot": 2},
                    {"pos": [4.2, -0.3, 0], "scale": 5.0, "rot": 5},
                ]
            else:
                # Mixed orientations
                positions = [
                    {"pos": [-4, 0.4, 0], "scale": 4.5, "rot": -3},
                    {"pos": [0.5, -0.3, 0], "scale": 5.0, "rot": 2},
                    {"pos": [4.2, 0.2, 0], "scale": 4.5, "rot": -4},
                ]
        elif n == 2:
            positions = [
                {"pos": [-3, 0.3, 0], "scale": 5.5, "rot": -3},
                {"pos": [3, -0.3, 0], "scale": 5.5, "rot": 4},
            ]
        else:
            positions = [{"pos": [0, 0, 0], "scale": 6.0, "rot": 0}]

        # Setup images
        for i, data in enumerate(images_data):
            img = data["img"]
            layout = positions[i]

            if data["portrait"]:
                img.height = layout["scale"]
            else:
                img.width = layout["scale"]

            img.rotate(layout["rot"] * DEGREES)
            img.move_to(layout["pos"])
            img.scale(0.85)  # Start slightly smaller
            self.add(img)

        # Gentle scale in
        self.play(
            *[d["img"].animate.scale(1.18) for d in images_data],
            run_time=1.2,
            rate_func=smooth,
        )

        # Ken Burns: noticeable zoom, drift, and rotation
        animations = []
        for data in images_data:
            img = data["img"]
            zoom = random.uniform(1.08, 1.15)
            drift_x = random.uniform(-0.5, 0.5)
            drift_y = random.uniform(-0.3, 0.3)
            rot = random.uniform(-4, 4) * DEGREES

            animations.append(img.animate.scale(zoom).shift([drift_x, drift_y, 0]).rotate(rot))

        self.play(*animations, run_time=6.0, rate_func=linear)

        # Gentle scale out
        self.play(
            *[d["img"].animate.scale(1.15) for d in images_data],
            run_time=1.2,
            rate_func=smooth,
        )


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="Render the photo showcase animation.")
    parser.add_argument(
        "images",
        nargs="*",
        default=DEFAULT_IMAGE_PATHS,
        help="2-3 image paths to showcase (default: built-in sample paths)",
    )
    args = parser.parse_args()

    env = os.environ.copy()
    env["SHOWCASE_IMAGE_PATHS"] = json.dumps(args.images)
    subprocess.run(["manim", "-pql", __file__, "PhotoShowcase"], env=env)
