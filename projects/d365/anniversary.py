from manim import *


class Anniversary(Scene):
    """Happy 1 Year Anniversary scene with green and pink interlaced text."""

    def construct(self):
        self.camera.background_color = BLACK

        green = "#00d4aa"
        pink = "#ff6b9d"

        words = ["Happy", "1 Year", "Anniversary"]
        colors = [green, pink, green]

        text_group = VGroup()
        for word, color in zip(words, colors, strict=True):
            text = Text(word, font="Arial", font_size=72, color=color, weight=BOLD)
            text_group.add(text)

        text_group.arrange(DOWN, buff=0.4)

        for text in text_group:
            text.set_opacity(0)
            self.add(text)

        for text in text_group:
            self.play(
                text.animate.set_opacity(1),
                run_time=1.5,
                rate_func=smooth,
            )
            self.wait(0.3)

        self.wait(1)

        self.play(
            *[text.animate.scale(1.1) for text in text_group],
            rate_func=there_and_back,
            run_time=1.5,
        )

        self.wait(2)


if __name__ == "__main__":
    import subprocess

    subprocess.run(["manim", "-pqh", __file__, "Anniversary"])
