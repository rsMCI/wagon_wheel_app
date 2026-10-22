"""Wagon-wheel effect (temporal aliasing) – minimal example.

A wheel with N identical spokes looks the same after a rotation of 360/N degrees.
A camera only sees one picture every 1/fps seconds, so only the rotation per frame
modulo 360/N matters. If the wheel turns (almost) a whole multiple of 360/N between
two frames, it appears to stand still or even turn backwards.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

N_SPOKES = 8                    # identical spokes -> symmetry angle 45 deg
FPS = 10                        # camera frame rate [frames/s]
SYM = 360.0 / N_SPOKES          # angle after which the wheel looks identical

# true rotation per camera frame in degrees (what the wheel really does)
cases = [
    ("slow:  10°/frame",  10.0),
    ("fast:  45°/frame",  45.0),   # = exactly one spoke spacing -> looks still
    ("faster: 40°/frame", 40.0),   # = 45° - 5° -> looks like 5° BACKWARDS
]


def apparent_step(step_deg):
    """Rotation per frame as perceived: wrap into (-SYM/2, SYM/2]."""
    return (step_deg + SYM / 2) % SYM - SYM / 2


def draw_wheel(ax, angle_deg, title):
    ax.clear()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, lw=4))
    for k in range(N_SPOKES):
        a = np.deg2rad(angle_deg + k * SYM)
        ax.plot([0, np.cos(a)], [0, np.sin(a)], lw=3, color="k")
    ax.set_title(title, fontsize=10)


fig, axes = plt.subplots(1, len(cases), figsize=(9, 3.4))
frames = 60


def update(i):
    for ax, (name, step) in zip(axes, cases):
        angle = i * step                      # true angle at sample time i/FPS
        seen = apparent_step(step)
        draw_wheel(ax, angle, f"{name}\nappears: {seen:+.0f}°/frame")
    fig.suptitle(f"Wagon-wheel effect – {N_SPOKES} spokes, {FPS} frames/s", y=0.02)


anim = FuncAnimation(fig, update, frames=frames, interval=1000 / FPS)
anim.save("wagon_wheel.gif", writer=PillowWriter(fps=FPS))
print("saved wagon_wheel.gif")

for name, step in cases:
    print(f"{name:20s} true {step:5.1f}°/frame -> apparent {apparent_step(step):+5.1f}°/frame")
