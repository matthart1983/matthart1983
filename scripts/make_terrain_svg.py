"""Generate assets/terrain.svg for the GitHub profile README.

A 2D, animated-SVG take on the netwatchlabs.com hero: netwatch's mirrored
throughput graph as a braille-dot terrain, one ridge per process. GitHub
renders README images without scripts, so everything is precomputed and
driven by CSS keyframes:

- an oblique (parallel) projection, so scrolling one sample is a constant
  screen offset and each ridge can step with `steps()` like the TUI;
- the data loops every LOOP samples; each ridge holds two copies so the
  seam is invisible;
- callouts are their own elements with their own opacity keyframes;
- prefers-reduced-motion freezes on the first frame, which already shows
  a callout.

Data is synthetic. Usage: python3 make_terrain_svg.py OUT.svg
"""
import math
import random
import sys

# palette: the site's cloud theme
BG, BORDER = "#0a0e10", "#1d2629"
RX, TX, HOT = "#5cd989", "#5fdcff", "#c4f2d4"
OFF, PLANE = "#2a3848", "#26323a"
TEXT, MUTED, SOFT = "#e6edf0", "#9fb2b8", "#7e949b"
PANEL = "#0d1215"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

TICK = 0.125
LOOP = 320          # samples per loop (40 s)
SVIS = 120          # samples visible per ridge
L = 11              # dot rows each side of the glass
VMAX = 100
DX = 5.4            # px per sample
SLOPE = 0.14        # time axis drops to the right
DY, GY, Y0 = 3.6, 2.4, 3.0
R_LIT, R_OFF = 1.75, 0.8
ROW = (24, -31)     # screen offset per ridge, front to back
CELL = 4 * DY + GY  # braille cell height

rnd = random.Random(7)


def y_of(k):
    return Y0 + k * DY + (k // 4) * GY


def level(v):
    if v < 0.004:
        return 0.0
    return max(0.6, L * math.log10(1 + v) / math.log10(1 + VMAX))


def lit(v):
    """Number of lit dots for a rate."""
    return int(math.floor(level(v) + 0.5))


# --- synthetic traffic, front ridge first -------------------------------
BURSTS = {
    # name: (center sample, up?, lo, hi, conns, peer)
    "cargo": (90, False, 70, 90, 8, "static.crates.io:443"),
    "syncthing": (190, True, 11, 16, 1, "192.168.1.20:22000"),
    "dockerd": (270, False, 80, 96, 3, "registry-1.docker.io:443"),
}
BLEN = 30


def series(name):
    rx, tx = [0.0] * LOOP, [0.0] * LOOP
    b = 0.0
    for n in range(LOOP):
        if name == "firefox":
            if rnd.random() < 0.045:
                b = 14 + rnd.random() * 46
            b *= 0.8
            rx[n] = 0.2 + rnd.random() * 0.3 + b
            tx[n] = 0.04 + rx[n] * 0.035
        elif name == "mpv":
            on = n % 32 < 7
            rx[n], tx[n] = (24 + rnd.random() * 10, 0.12) if on else (0.05, 0.02)
        elif name == "zoom":
            rx[n], tx[n] = 1.8 + rnd.random(), 1.2 + rnd.random() * 0.9
        elif name == "syncthing":
            rx[n], tx[n] = (0.2, 0.6 + rnd.random() * 1.2) if n % 96 < 30 else (0.04, 0.06)
        elif name == "ssh":
            k = 0.12 if rnd.random() < 0.25 else 0.02
            rx[n], tx[n] = k, k * 0.8
        elif name == "cargo":
            rx[n], tx[n] = (0.3, 0.05) if rnd.random() < 0.05 else (0.0, 0.0)
        elif name == "dockerd":
            rx[n], tx[n] = 0.0, 0.0
    peak = 0.0
    if name in BURSTS:
        c, up, lo, hi, _, _ = BURSTS[name]
        n0 = c - BLEN // 2
        for j in range(BLEN):
            k = min(1, j / 3, (BLEN - j) / 3)
            v = k * (lo + rnd.random() * (hi - lo))
            n = (n0 + j) % LOOP
            if up:
                tx[n] = max(tx[n], v)
            else:
                rx[n] = max(rx[n], v)
                tx[n] = max(tx[n], 0.5 * k)
            peak = max(peak, v)
    return rx, tx, peak


PROCS = ["firefox", "mpv", "cargo", "zoom", "syncthing", "dockerd", "ssh"]
P = len(PROCS)
DATA = {p: series(p) for p in PROCS}

# --- geometry -------------------------------------------------------------
WWIN = (SVIS - 0.5) * DX
H = y_of(L - 1) + R_LIT + 1


def pt(i, y):
    """Ridge-local screen point for sample i at height y (up is negative)."""
    return i * DX, i * DX * SLOPE + y


def row_off(r):
    return ROW[0] * r, ROW[1] * r


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v) >= 0.05 else "0"


def dots_path(points):
    """Zero-length round-capped segments: one dot each, relative moves."""
    out, cx, cy = [], 0.0, 0.0
    for x, y in points:
        out.append(f"m{f(x - cx)} {f(y - cy)}h0")
        cx, cy = x, y
    return "M0 0" + "".join(out)


# Bounds: front ridge window starts at the origin.
min_x = -DX
max_x = WWIN + ROW[0] * (P - 1) + 150      # room for labels
min_y = ROW[1] * (P - 1) - H - 40          # room for a callout above the back
max_y = WWIN * SLOPE + H + 6
PAD_X, PAD_TOP, PAD_BOTTOM = 48, 40, 50
OX, OY = PAD_X - min_x, PAD_TOP - min_y
VW = round(max_x - min_x + 2 * PAD_X)
VH = round(max_y - min_y + PAD_TOP + PAD_BOTTOM)

dur = LOOP * TICK
shift = (LOOP * DX, LOOP * DX * SLOPE)


def pct(s):
    return f"{100 * s / LOOP:.3f}%"


svg = []
add = svg.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    f'viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" '
    f'aria-label="netwatch throughput by process, drawn as a terrain of braille dots. Sample data.">')
add(f"""<style>
.s{{animation:scroll {dur:g}s steps({LOOP}) infinite}}
@keyframes scroll{{to{{transform:translate({-shift[0]:.1f}px,{-shift[1]:.1f}px)}}}}
.b{{animation:boot .7s cubic-bezier(.2,.7,.2,1) both}}
@keyframes boot{{from{{opacity:0;transform:translateY(-10px)}}}}
.lg{{animation:fade 1s .9s both}}
@keyframes fade{{from{{opacity:0}}}}
text{{font-family:{MONO}}}
@media (prefers-reduced-motion:reduce){{.s,.b,.lg,.co{{animation:none!important}}}}
</style>""")
add("<defs>")
add(f'<pattern id="lat" patternUnits="userSpaceOnUse" x="{-DX / 2:.2f}" y="0" width="{DX}" height="{CELL:.2f}" '
    f'patternTransform="matrix(1 {SLOPE} 0 1 0 0)">'
    + "".join(f'<circle cx="{DX / 2:.2f}" cy="{Y0 + k * DY:.2f}" r="{R_OFF}" fill="{OFF}"/>' for k in range(4))
    + "</pattern>")
gx2, gy2 = pt(SVIS - 1, 0)
add(f'<linearGradient id="age" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{gx2:.1f}" y2="{gy2:.1f}">'
    '<stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".45" stop-color="#fff" stop-opacity=".6"/>'
    '<stop offset="1" stop-color="#fff"/></linearGradient>')
a1, a2 = pt(-0.5, -H), pt(SVIS - 0.5, -H)
b2, b1 = pt(SVIS - 0.5, H), pt(-0.5, H)
win = f"{a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {b1[0]:.1f},{b1[1]:.1f}"
add(f'<mask id="win" maskUnits="userSpaceOnUse" x="{-DX * 2}" y="{-H - 10:.1f}" width="{WWIN + DX * 4:.1f}" '
    f'height="{WWIN * SLOPE + 2 * H + 20:.1f}"><polygon points="{win}" fill="url(#age)"/></mask>')
# The glow runs on a fixed window, not on the (very wide) scrolling layer.
add(f'<filter id="glow" filterUnits="userSpaceOnUse" x="{-DX * 2}" y="{-H - 10:.1f}" width="{WWIN + DX * 4:.1f}" height="{WWIN * SLOPE + 2 * H + 20:.1f}">'
    '<feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
add('<radialGradient id="haze" cx=".62" cy=".55" r=".6"><stop offset="0" stop-color="#5cd989" stop-opacity=".07"/>'
    '<stop offset="1" stop-color="#5cd989" stop-opacity="0"/></radialGradient>')
add("</defs>")

add(f'<rect x=".5" y=".5" width="{VW - 1}" height="{VH - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>')
add(f'<rect x=".5" y=".5" width="{VW - 1}" height="{VH - 1}" rx="12" fill="url(#haze)"/>')

# glass plane under every ridge
g = []
for (i, r) in ((-1.5, -0.6), (SVIS + 0.5, -0.6), (SVIS + 0.5, P - 0.4), (-1.5, P - 0.4)):
    x, y = pt(i, 0)
    g.append(f"{OX + x + ROW[0] * r:.1f},{OY + y + ROW[1] * r:.1f}")
add(f'<polygon class="lg" points="{" ".join(g)}" fill="{PLANE}" fill-opacity=".38"/>')

callouts = []
for r in reversed(range(P)):  # back to front
    name = PROCS[r]
    rx, tx, peak = DATA[name]
    ox, oy = row_off(r)
    gid = f"d{r}"
    up_rx, up_tx, hot = [], [], []
    for n in range(LOOP):
        for k in range(lit(rx[n])):
            (hot if k == lit(rx[n]) - 1 else up_rx).append(pt(n, -y_of(k)))
        for k in range(lit(tx[n])):
            (hot if k == lit(tx[n]) - 1 else up_tx).append(pt(n, y_of(k)))
    add(f'<g transform="translate({OX + ox:.1f} {OY + oy:.1f})">')
    add(f'<g class="b" style="animation-delay:{(P - 1 - r) * 0.09:.2f}s">')
    # lattice, baseline, then the scrolling dots
    add(f'<polygon points="{win}" fill="url(#lat)" mask="url(#win)" opacity=".9"/>')
    e0, e1 = pt(0, 0), pt(SVIS - 1, 0)
    add(f'<line x1="{e0[0]:.1f}" y1="{e0[1]:.1f}" x2="{e1[0]:.1f}" y2="{e1[1]:.1f}" stroke="{RX}" stroke-opacity=".16"/>')
    add(f'<g filter="url(#glow)"><g mask="url(#win)"><g class="s">')
    add(f'<g id="{gid}" stroke-linecap="round" stroke-width="{2 * R_LIT}" fill="none">')
    if up_rx:
        add(f'<path stroke="{RX}" d="{dots_path(up_rx)}"/>')
    if up_tx:
        add(f'<path stroke="{TX}" d="{dots_path(up_tx)}"/>')
    if hot:
        add(f'<path stroke="{HOT}" stroke-opacity=".9" d="{dots_path(hot)}"/>')
    add("</g>")
    add(f'<use href="#{gid}" xlink:href="#{gid}" x="{shift[0]:.1f}" y="{shift[1]:.1f}"/>')
    add("</g></g></g>")
    lx, ly = pt(SVIS + 1, 0)
    add(f'<text x="{lx:.1f}" y="{ly + 4.5:.1f}" font-size="13" fill="{SOFT}">{name}</text>')
    add("</g></g>")

    if name in BURSTS:
        c, up, _, _, conns, peer = BURSTS[name]
        lvl = lit(peak)
        for copy in (0, 1):
            ci = c + copy * LOOP
            # visible while the burst's middle is in the right half of the window
            s_on, s_off = ci - SVIS + 8, ci - SVIS * 0.5
            lo, hi = max(0, s_on), min(LOOP, s_off)
            if lo >= hi:
                continue
            px, py = pt(ci, (y_of(lvl - 1) + 6) if up else -(y_of(lvl - 1) + 6))
            arrow = "↑" if up else "↓"
            col = TX if up else RX
            label = [(name, TEXT, "600"), (f" {arrow}{peak:.0f} Mb/s", col, "400"),
                     (f" · {conns} conn{'s' if conns > 1 else ''} →", SOFT, "400"), (f" {peer}", TEXT, "400")]
            chars = sum(len(t) for t, _, _ in label)
            bw, bh = chars * 7.8 + 22, 26
            by = py - 24 - bh if not up else py + 24
            ly1, ly2 = (py - 24, py) if not up else (py, py + 24)
            fade = 1.5
            frames = [(0, 0), (lo, 0), (min(hi, lo + fade), 1), (max(lo, hi - fade), 1), (hi, 0), (LOOP, 0)]
            if lo == 0:
                frames = [(0, 1), (max(0, hi - fade), 1), (hi, 0), (LOOP, 0)]
            if hi == LOOP:
                frames = [(0, 0), (lo, 0), (min(LOOP, lo + fade), 1), (LOOP, 1)]
            kf = f"co{r}{copy}"
            stops = "".join(f"{pct(s)}{{opacity:{o}}}" for s, o in frames)
            start = 1 if frames[0][1] else 0
            tspans = "".join(f'<tspan fill="{cl}" font-weight="{w}">{t}</tspan>' for t, cl, w in label)
            callouts.append(
                f'<style>@keyframes {kf}{{{stops}}}</style>'
                f'<g transform="translate({OX + ox:.1f} {OY + oy:.1f})"><g class="s">'
                f'<g class="co" opacity="{start}" style="animation:{kf} {dur:g}s linear infinite">'
                f'<line x1="{px:.1f}" y1="{ly1:.1f}" x2="{px:.1f}" y2="{ly2:.1f}" stroke="{col}"/>'
                f'<rect x="{px - bw / 2:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh}" rx="6" fill="{PANEL}" '
                f'fill-opacity=".94" stroke="{RX}" stroke-opacity=".34"/>'
                f'<text x="{px:.1f}" y="{by + 17.5:.1f}" font-size="13" text-anchor="middle" xml:space="preserve">{tspans}</text>'
                "</g></g></g>")

svg.extend(callouts)

# legend and caption
ly = VH - 26
add(f'<g class="lg" font-size="13">'
    f'<circle cx="{PAD_X}" cy="{ly - 4.5}" r="3.5" fill="{RX}"/><text x="{PAD_X + 10}" y="{ly}" fill="{MUTED}">download</text>'
    f'<circle cx="{PAD_X + 104}" cy="{ly - 4.5}" r="3.5" fill="{TX}"/><text x="{PAD_X + 114}" y="{ly}" fill="{MUTED}">upload</text>'
    f'<text x="{VW - PAD_X}" y="{ly}" fill="{SOFT}" text-anchor="end">sample data · 1 sample / 125 ms</text>'
    f'<text x="{PAD_X}" y="34" fill="{SOFT}" letter-spacing="1.5">NETWATCH · THROUGHPUT BY PROCESS</text>'
    "</g>")
add("</svg>")

out = sys.argv[1]
with open(out, "w") as fh:
    fh.write("\n".join(svg) + "\n")
print(out, VW, VH)
