"""Streamlit demo: wagon-wheel effect (temporal aliasing).

Run:  streamlit run wagon_wheel_app.py
"""
import time

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Wagon-wheel effect", layout="wide")
st.title("Wagon-wheel effect – temporal aliasing")
st.caption(
    "A camera samples the wheel only `fps` times per second. With identical spokes, "
    "only the rotation per frame modulo the spoke spacing can be observed."
)

# ---------------------------------------------------------------- controls
with st.sidebar:
    st.header("Parameters")
    n_spokes = st.slider("Number of spokes", 2, 24, 8)
    fps = st.slider("Camera frame rate [frames/s]", 2, 30, 10)
    f_true = st.slider("True rotation speed [rev/s]", 0.0, 10.0, 1.0, 0.05)
    mark = st.checkbox("Mark one spoke (breaks the symmetry)", value=False)
    clockwise = st.radio("True rotation direction", ["Clockwise (car driving right)", "Counter-clockwise"]
                         ).startswith("Clockwise")
    playing = st.toggle("Play animation", value=True)
    speed = st.select_slider("Playback speed", [0.25, 0.5, 1.0], value=0.5,
                             help="Slows the animation down for viewing; physics are unchanged.")

sgn = -1.0 if clockwise else 1.0           # screen direction of the TRUE rotation
sym = 360.0 / n_spokes                       # wheel looks identical after this angle
step = 360.0 * f_true / fps                  # true rotation per frame [deg]
apparent = (step + sym / 2) % sym - sym / 2  # perceived step, wrapped to (-sym/2, sym/2]
f_app = apparent * fps / 360.0               # perceived speed [rev/s]
f_nyq = fps / (2 * n_spokes)                 # Nyquist limit for this spoke pattern


# ---------------------------------------------------------------- drawing
def wheel_svg(angle_deg: float, marked: bool, size: int = 320) -> str:
    c, r = size / 2, size / 2 - 14
    parts = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
             f'xmlns="http://www.w3.org/2000/svg">',
             f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#888" stroke-width="6"/>']
    for k in range(n_spokes):
        a = np.deg2rad(sgn * angle_deg + k * sym)
        colour = "#d62728" if (marked and k == 0) else "#888"
        parts.append(f'<line x1="{c}" y1="{c}" x2="{c + r * np.cos(a):.1f}" '
                     f'y2="{c - r * np.sin(a):.1f}" stroke="{colour}" stroke-width="5" '
                     f'stroke-linecap="round"/>')
    parts.append(f'<circle cx="{c}" cy="{c}" r="7" fill="#888"/></svg>')
    return "".join(parts)


def alias_plot():
    fmax = 10.0
    f = np.linspace(0, fmax, 1000)
    st_ = 360.0 * f / fps
    app = ((st_ + sym / 2) % sym - sym / 2) * fps / 360.0
    app = np.where(np.abs(np.diff(app, prepend=app[0])) > 0.5 * sym * fps / 360, np.nan, app)
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.plot(f, app, lw=1.8, label="perceived")
    ax.plot(f, f, "--", lw=1, color="gray", label="true (no aliasing)")
    ax.plot([f_true], [f_app], "o", color="#d62728", ms=8)
    ax.axvline(f_nyq, color="k", lw=0.8, ls=":")
    ax.text(f_nyq, ax.get_ylim()[0], " Nyquist", fontsize=8, va="bottom")
    ax.set_xlabel("true speed [rev/s]")
    ax.set_ylabel("perceived speed [rev/s]")
    ax.set_title("Aliasing curve")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- layout
m1, m2, m3, m4 = st.columns(4)
m1.metric("True rotation / frame", f"{step:.1f}°")
m2.metric("Spoke spacing", f"{sym:.1f}°")
m3.metric("Perceived rotation / frame", f"{apparent:+.1f}°")
m4.metric("Perceived speed", f"{f_app:+.2f} rev/s")

if f_true <= f_nyq:
    st.success(f"f_true ≤ Nyquist limit ({f_nyq:.2f} rev/s): motion is perceived correctly.")
elif abs(apparent) < 1e-6:
    st.warning("Rotation per frame is an exact multiple of the spoke spacing: the wheel appears to **stand still**.")
elif apparent < 0:
    st.error("Aliasing: the wheel appears to rotate **backwards** (opposite to its true direction).")
else:
    st.warning("Aliasing: the wheel appears to rotate **forwards, but too slowly**.")

left, mid, right = st.columns([1, 1, 1.2])
left.subheader("Camera view (sampled)")
cam = left.empty()
mid.subheader("Reality (very high frame rate)")
real = mid.empty()
with right:
    st.pyplot(alias_plot())

# ---------------------------------------------------------------- animation
# Camera: shows the true angle only at t = i / fps.
# Reality: smooth rotation, shown at ~30 display frames/s and slowed by `speed`.
n = 0
t0 = time.time()
cam.markdown(wheel_svg(0, mark), unsafe_allow_html=True)
real.markdown(wheel_svg(0, mark), unsafe_allow_html=True)

if playing:
    while True:
        t = (time.time() - t0) * speed                  # simulated time [s]
        i = int(t * fps)                                # index of latest camera frame
        cam.markdown(wheel_svg(i * step, mark), unsafe_allow_html=True)
        real.markdown(wheel_svg(360.0 * f_true * t, mark), unsafe_allow_html=True)
        time.sleep(1 / 30)
