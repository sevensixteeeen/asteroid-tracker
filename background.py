"""An animated space background for the Streamlit page: stars, asteroids, meteors.

It's all CSS, so it needs no extra libraries and the browser does the animating.
"""

import streamlit as st

# Same color as backgroundColor in .streamlit/config.toml.
SPACE = "#070a14"

CSS = """
<style>
/* Let the background show through Streamlit's own page and header colors. */
.stApp, [data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: rgba(13, 18, 32, 0.85);
    backdrop-filter: blur(6px);
}
/* The background lives inside .stMain. Giving .stMain its own layer and the
   background z-index -1 puts the background under everything else in it. */
.stMain { position: relative; z-index: 0; }
/* The element holding the background takes no space on the page. */
[data-testid="stElementContainer"]:has(.space-bg) { margin-bottom: -1rem; }

.space-bg {
    position: fixed;
    inset: 0;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
    background:
        radial-gradient(ellipse at 15% 0%, rgba(57, 135, 229, 0.14), transparent 55%),
        radial-gradient(ellipse at 90% 100%, rgba(98, 80, 214, 0.12), transparent 50%),
        SPACE;
}

/* --- Stars: tiled dots that drift slowly downward, in three depths --- */
.stars {
    position: absolute;
    inset: -400px 0 0 0;  /* one tile taller than the screen, so the loop is seamless */
    background-size: 400px 400px;
    animation: drift 160s linear infinite;
}
.stars.near {
    background-image:
        radial-gradient(1.5px 1.5px at 40px 60px, #fff, transparent),
        radial-gradient(1.5px 1.5px at 310px 140px, #dbe7ff, transparent),
        radial-gradient(2px 2px at 180px 330px, #fff, transparent),
        radial-gradient(1.5px 1.5px at 360px 370px, #ffeccc, transparent);
    animation-duration: 90s;
    opacity: 0.9;
}
.stars.mid {
    background-image:
        radial-gradient(1px 1px at 90px 200px, #fff, transparent),
        radial-gradient(1px 1px at 250px 40px, #fff, transparent),
        radial-gradient(1px 1px at 130px 380px, #cfdcff, transparent),
        radial-gradient(1px 1px at 380px 250px, #fff, transparent),
        radial-gradient(1px 1px at 20px 310px, #fff, transparent);
    animation-duration: 160s;
    opacity: 0.7;
}
.stars.far {
    background-image:
        radial-gradient(1px 1px at 60px 120px, #fff, transparent),
        radial-gradient(1px 1px at 200px 260px, #fff, transparent),
        radial-gradient(1px 1px at 340px 30px, #fff, transparent),
        radial-gradient(1px 1px at 270px 350px, #fff, transparent),
        radial-gradient(1px 1px at 150px 90px, #fff, transparent),
        radial-gradient(1px 1px at 10px 220px, #fff, transparent);
    animation: drift 300s linear infinite, twinkle 6s ease-in-out infinite alternate;
    opacity: 0.45;
}
@keyframes drift { to { transform: translateY(400px); } }
@keyframes twinkle { from { opacity: 0.25; } to { opacity: 0.55; } }

/* --- Asteroids: lumpy rocks that tumble slowly across the screen --- */
/* .rock-path moves across the screen; the .rock inside it spins.
   font-size sets each asteroid's size, because the rock is sized in em. */
.rock-path {
    position: absolute;
    left: 0;
    animation: fly-right 80s linear infinite;
}
.rock {
    width: 1.4em;
    height: 1.1em;
    border-radius: 45% 55% 50% 40% / 55% 45% 55% 45%;
    background: radial-gradient(circle at 35% 30%, #9c978c, #57534b 55%, #2a2825 100%);
    box-shadow:
        inset -0.2em -0.15em 0.3em rgba(0, 0, 0, 0.6),
        inset 0.1em 0.08em 0.15em rgba(255, 255, 255, 0.1);
    animation: spin 30s linear infinite;
    position: relative;
}
/* Two craters on each rock. */
.rock::before, .rock::after {
    content: "";
    position: absolute;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.3);
    box-shadow: inset 0.03em 0.03em 0.05em rgba(0, 0, 0, 0.5);
}
.rock::before { width: 0.3em; height: 0.25em; top: 25%; left: 45%; }
.rock::after { width: 0.2em; height: 0.18em; top: 58%; left: 22%; }

.rock-path:nth-child(4) { top: 8%;  font-size: 22px; animation-duration: 95s;  animation-delay: -20s; }
.rock-path:nth-child(5) { top: 55%; font-size: 12px; animation-duration: 70s;  animation-delay: -55s; opacity: 0.7; }
.rock-path:nth-child(6) { top: 30%; font-size: 34px; animation-duration: 140s; animation-delay: -90s; animation-name: fly-left; }
.rock-path:nth-child(7) { top: 75%; font-size: 16px; animation-duration: 110s; animation-delay: -30s; animation-name: fly-left; opacity: 0.8; }
.rock-path:nth-child(8) { top: 18%; font-size: 9px;  animation-duration: 60s;  animation-delay: -5s;  opacity: 0.6; }
.rock-path:nth-child(5) .rock { animation-duration: 18s; }
.rock-path:nth-child(6) .rock { animation-duration: 55s; animation-direction: reverse; }
.rock-path:nth-child(8) .rock { animation-duration: 12s; }

@keyframes fly-right {
    from { transform: translate(-60px, 0); }
    to   { transform: translate(calc(100vw + 60px), 22vh); }
}
@keyframes fly-left {
    from { transform: translate(calc(100vw + 60px), 0); }
    to   { transform: translate(-60px, 18vh); }
}
@keyframes spin { to { transform: rotate(360deg); } }

/* --- Shooting stars: a quick streak every so often --- */
.meteor {
    position: absolute;
    width: 140px;
    height: 1.5px;
    border-radius: 1px;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.95), rgba(160, 200, 255, 0.4) 30%, transparent);
    opacity: 0;
    animation: streak 11s ease-out infinite;
}
.meteor:nth-child(9)  { top: 10%; left: 75%; }
.meteor:nth-child(10) { top: 35%; left: 95%; animation-duration: 17s; animation-delay: 6s; }
@keyframes streak {
    /* The streak is tilted so its bright head leads the way, down and to the left. */
    0%   { opacity: 0; transform: translate(0, 0) rotate(-30deg); }
    1%   { opacity: 1; }
    7%   { opacity: 0; transform: translate(-420px, 240px) rotate(-30deg); }
    100% { opacity: 0; transform: translate(-420px, 240px) rotate(-30deg); }
}

/* People who've asked their system for less motion get a still starfield. */
@media (prefers-reduced-motion: reduce) {
    .stars, .rock-path, .rock, .meteor { animation: none; }
    .rock-path, .meteor { display: none; }
}
</style>
""".replace("SPACE", SPACE)

# Children 1-3 are star layers, 4-8 asteroids, 9-10 meteors. The CSS above picks
# each one out by its position, so keep this order if you add more.
HTML = (
    '<div class="space-bg">'
    '<div class="stars far"></div><div class="stars mid"></div><div class="stars near"></div>'
    + '<div class="rock-path"><div class="rock"></div></div>' * 5
    + '<div class="meteor"></div>' * 2
    + "</div>"
)


def add_space_background() -> None:
    """Draw the animated background behind everything else on the page."""
    st.html(CSS + HTML)
