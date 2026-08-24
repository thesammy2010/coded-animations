from manim import *


class HelloWorld(Scene):
    """A simple example scene that displays text."""

    def construct(self):
        text = Text("Hello, TheSammy2010!")
        self.play(Write(text))
        self.wait(1)
        self.play(FadeOut(text))


class SimpleCircle(Scene):
    """A simple circle animation."""

    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        self.play(Create(circle))
        self.play(circle.animate.scale(2))
        self.play(circle.animate.set_color(RED))
        self.play(circle.animate.shift(RIGHT * 2))
        self.play(circle.animate.shift(LEFT * 4))
        self.play(circle.animate.move_to(ORIGIN))
        self.play(FadeOut(circle))


class CircleToSquare(Scene):
    """Example scene showing shape transformation."""

    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)

        self.play(Create(circle))
        self.wait(0.5)
        self.play(Transform(circle, square))
        self.wait(1)


if __name__ == "__main__":
    import subprocess

    subprocess.call("clear", shell=True)
    for scene_class in [HelloWorld, SimpleCircle, CircleToSquare]:
        scene_name = scene_class.__name__
        print(f"Rendering: {scene_name}")
        subprocess.run(["manim", "-pql", __file__, scene_name])
