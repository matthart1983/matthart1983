"""Generate assets/terrain-{dark,light}.svg for the GitHub profile README.

A short decorative strip based on the netwatchlabs.com hero: a mirrored
throughput graph as a braille-dot terrain, a few ridges deep, with the
NetWatch Labs wordmark on the left. It is decoration, not a screenshot,
so it carries no process names, rates or callouts; the real demo GIF
below it in the README is the evidence. GitHub
renders README images without scripts, so everything is precomputed and
driven by CSS keyframes:

- each ridge is drawn flat, then scaled and shifted to fake perspective
  (back ridges smaller, converging to the right);
- within a ridge, scrolling one sample is a constant offset, so the dots
  step with `steps()` like the TUI redraws;
- the data loops every LOOP samples and each ridge holds two copies, so the
  seam is invisible;
- narrow images (phones) drop the tagline; prefers-reduced-motion holds
  the first frame.

Two files come out, one per GitHub theme, using GitHub's own colours:
the code-block ground, its text colours, and greens (download) and blues
(upload) shaded by height the way the contribution graph shades
activity. The README picks one with <picture> and prefers-color-scheme.

Data is synthetic. Usage: python3 make_terrain_svg.py OUTDIR
"""
import math
import random
import sys

# GitHub (Primer) colours. Greens and blues run low to high intensity.
THEMES = {
    "dark": dict(
        bg="#151b23", panel="#0d1117", border="#3d444d", off="#262c36", plane="#212830", plane_op=".7",
        text="#f0f6fc", muted="#9198a1",
        rx=["#238636", "#2ea043", "#3fb950", "#56d364"],
        tx=["#1f6feb", "#388bfd", "#58a6ff", "#79c0ff"],
        glow=True,
    ),
    "light": dict(
        bg="#f6f8fa", panel="#ffffff", border="#d1d9e0", off="#d1d9e0", plane="#e6eaef", plane_op=".8",
        text="#1f2328", muted="#59636e",
        rx=["#4ac26b", "#2da44e", "#1a7f37", "#116329"],
        tx=["#54aeff", "#218bff", "#0969da", "#0550ae"],
        glow=False,
    ),
}
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

TICK = 0.125
LOOP = 320          # samples per loop (40 s)
SVIS = 124          # samples visible per ridge
L = 8               # dot rows each side of the glass
VMAX = 100
DX = 5.6            # px per sample at the front
SLOPE = 0.03        # the time axis drops to the right
DY, GY, Y0 = 4.0, 2.6, 3.4
R_LIT, R_OFF = 2.0, 0.85
CELL = 4 * DY + GY  # braille cell height
DEPTH = 21          # px between ridges at the front
KSTEP = 0.06        # scale lost per ridge going back

rnd = random.Random(7)


def y_of(k):
    return Y0 + k * DY + (k // 4) * GY


def lit(v):
    """Lit dots for a rate: a power scale, so bursts tower and idle is empty."""
    if v < 0.15:
        return 0
    return min(L, int(L * (min(v, VMAX) / VMAX) ** 0.45 + 0.5))


# --- synthetic traffic, front ridge first -------------------------------
BURSTS = {
    # series: (centre sample, upload?, lo, hi)
    "cargo": (82, False, 70, 90),
    "syncthing": (205, True, 11, 16),
    "dockerd": (285, False, 80, 96),
}
BLEN = 30
# Series shapes, front ridge first. The names only pick a traffic shape; none is drawn.
PROCS = ["firefox", "mpv", "cargo", "syncthing", "dockerd"]
P = len(PROCS)


def series(name):
    rx, tx = [0.0] * LOOP, [0.0] * LOOP
    b = 0.0
    for n in range(LOOP):
        if name == "firefox":
            if rnd.random() < 0.05:
                b = 10 + rnd.random() * 40
            b *= 0.78
            rx[n] = 0.1 + rnd.random() * 0.2 + b
            tx[n] = 0.03 + rx[n] * 0.04
        elif name == "mpv":
            rx[n], tx[n] = (22 + rnd.random() * 10, 0.2) if n % 32 < 7 else (0.05, 0.02)
        elif name == "zoom":
            rx[n], tx[n] = 1.6 + rnd.random() * 1.4, 1.1 + rnd.random() * 1.0
        elif name == "syncthing":
            rx[n], tx[n] = (0.2, 0.5 + rnd.random() * 1.0) if n % 96 < 30 else (0.04, 0.06)
        elif name == "ssh":
            k = 0.3 if rnd.random() < 0.2 else 0.04
            rx[n], tx[n] = k, k * 0.8
        elif name == "cargo":
            rx[n] = 0.4 if rnd.random() < 0.05 else 0.0
    peak = 0.0
    if name in BURSTS:
        c, up, lo, hi = BURSTS[name]
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


DATA = {p: series(p) for p in PROCS}

# --- geometry -------------------------------------------------------------
WWIN = (SVIS - 0.5) * DX
H = y_of(L - 1) + R_LIT + 1


def pt(i, y=0.0):
    """Ridge-local point for sample i at height y (up is negative)."""
    return i * DX, i * DX * SLOPE + y


def scale(r):
    return 1 - KSTEP * r


def origin(r):
    """Ridge origin before padding: back ridges rise and slide right."""
    x = (1 - scale(r)) * WWIN * 0.7
    y = -sum(DEPTH * scale(j) for j in range(1, r + 1))
    return x, y


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v) >= 0.05 else "0"


def dots_path(points):
    """Zero-length round-capped segments, one dot each, relative moves."""
    out, cx, cy = [], 0.0, 0.0
    for x, y in points:
        out.append(f"m{f(x - cx)} {f(y - cy)}h0")
        cx, cy = x, y
    return "M0 0" + "".join(out)


# --- bounds -----------------------------------------------------------------
xs, ys = [], []
for r, name in enumerate(PROCS):
    ox, oy = origin(r)
    k = scale(r)
    rx, tx, _ = DATA[name]
    up_h = y_of(max(lit(v) for v in rx) - 1) + R_LIT if max(rx) >= 0.15 else 4
    dn_h = y_of(max(lit(v) for v in tx) - 1) + R_LIT if max(tx) >= 0.15 else 4
    for i in (-1, SVIS):
        x, y = pt(i)
        xs.append(ox + k * x)
        ys += [oy + k * (y - up_h), oy + k * (y + dn_h)]

PAD_X, PAD_Y, MARK_W = 36, 22, 250   # MARK_W: column kept clear for the wordmark
OX, OY = PAD_X + MARK_W - min(xs), PAD_Y - min(ys)
VW = round(max(xs) - min(xs) + 2 * PAD_X + MARK_W)
VH = round(max(ys) - min(ys) + 2 * PAD_Y)

dur = LOOP * TICK


def pct(s):
    return f"{100 * s / LOOP:.3f}%"


def band(j):
    """Contribution-graph style intensity: one step per braille cell."""
    return min(3, j // 4)


def render(t):
    svg = []
    add = svg.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" '
        f'aria-label="NetWatch Labs. Decorative terrain of braille dots.">')
    add(f"""<style>
.s{{animation:scroll {dur:g}s steps({LOOP}) infinite}}
@keyframes scroll{{to{{transform:translate({-LOOP * DX:.1f}px,{-LOOP * DX * SLOPE:.1f}px)}}}}
.b{{animation:boot .8s cubic-bezier(.2,.7,.2,1) both}}
@keyframes boot{{from{{opacity:0;transform:translateY(-14px)}}}}
.lg{{animation:fade 1s .8s both}}
@keyframes fade{{from{{opacity:0}}}}
text{{font-family:{MONO}}}
@media (max-width:600px){{.tag{{display:none}}}}
@media (prefers-reduced-motion:reduce){{.s,.b,.lg{{animation:none!important}}}}
</style>""")
    add("<defs>")
    add(f'<pattern id="lat" patternUnits="userSpaceOnUse" x="{-DX / 2:.2f}" y="0" width="{DX}" height="{CELL:.2f}" '
        f'patternTransform="matrix(1 {SLOPE} 0 1 0 0)">'
        + "".join(f'<circle cx="{DX / 2:.2f}" cy="{Y0 + k * DY:.2f}" r="{R_OFF}" fill="{t["off"]}"/>' for k in range(4))
        + "</pattern>")
    gx2, gy2 = pt(SVIS - 1)
    add(f'<linearGradient id="age" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{gx2:.1f}" y2="{gy2:.1f}">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset=".4" stop-color="#fff" stop-opacity=".65"/>'
        '<stop offset="1" stop-color="#fff"/></linearGradient>')
    add(f'<mask id="win" maskUnits="userSpaceOnUse" {region}><polygon points="{win}" fill="url(#age)"/></mask>')
    if t["glow"]:
        # The glow runs on the fixed window, not on the very wide scrolling layer.
        add(f'<filter id="glow" filterUnits="userSpaceOnUse" {region}>'
            '<feGaussianBlur stdDeviation="2.4" result="b"/><feColorMatrix in="b" type="matrix" '
            'values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1.2 0" result="g"/>'
            '<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    add("</defs>")

    # GitHub code-block ground: subtle canvas, 6px corners, no border
    add(f'<rect width="{VW}" height="{VH}" rx="6" fill="{t["bg"]}"/>')

    corners = []
    for r, i, dy in ((0, -2, 18), (0, SVIS + 1, 18), (P - 1, SVIS + 1, -18), (P - 1, -2, -18)):
        ox, oy = origin(r)
        x, y = pt(i)
        corners.append(f"{OX + ox + scale(r) * x:.1f},{OY + oy + scale(r) * (y + dy):.1f}")
    add(f'<polygon class="lg" points="{" ".join(corners)}" fill="{t["plane"]}" fill-opacity="{t["plane_op"]}"/>')

    glow = ' filter="url(#glow)"' if t["glow"] else ""
    for r in reversed(range(P)):  # back to front
        name = PROCS[r]
        rx, tx, _ = DATA[name]
        ox, oy = origin(r)
        k = scale(r)
        gid = f"d{r}"
        dots = {(side, b): [] for side in ("rx", "tx") for b in range(4)}
        for n in range(LOOP):
            for vals, sign, side in ((rx, -1, "rx"), (tx, 1, "tx")):
                c = lit(vals[n])
                for j in range(c):
                    # the top of a tall column takes the strongest shade
                    b = 3 if (j == c - 1 and c >= 3) else band(j)
                    dots[(side, b)].append(pt(n, sign * y_of(j)))
        add(f'<g transform="translate({OX + ox:.1f} {OY + oy:.1f}) scale({k:.3f})">')
        add(f'<g class="b" style="animation-delay:{(P - 1 - r) * 0.1:.2f}s">')
        add(f'<polygon points="{win}" fill="url(#lat)" mask="url(#win)"/>')
        e0, e1 = pt(0), pt(SVIS - 1)
        add(f'<line x1="{e0[0]:.1f}" y1="{e0[1]:.1f}" x2="{e1[0]:.1f}" y2="{e1[1]:.1f}" stroke="{t["rx"][1]}" stroke-opacity=".25"/>')
        add(f'<g{glow}><g mask="url(#win)"><g class="s">')
        add(f'<g id="{gid}" stroke-linecap="round" stroke-width="{2 * R_LIT}" fill="none">')
        for (side, b), pts in dots.items():
            if pts:
                add(f'<path stroke="{t[side][b]}" d="{dots_path(pts)}"/>')
        add("</g>")
        add(f'<use href="#{gid}" xlink:href="#{gid}" x="{LOOP * DX:.1f}" y="{LOOP * DX * SLOPE:.1f}"/>')
        add("</g></g></g>")
        add("</g></g>")

    my = VH / 2
    add(f'<g class="lg"><text x="{PAD_X}" y="{my + 2:.1f}" font-size="24" font-weight="600" fill="{t["text"]}">NetWatch Labs</text>'
        f'<text class="tag" x="{PAD_X}" y="{my + 26:.1f}" font-size="14" fill="{t["muted"]}">terminal diagnostics in Rust</text></g>')
    add("</svg>")
    return "\n".join(svg) + "\n"


a1, a2 = pt(-0.5, -H), pt(SVIS - 0.5, -H)
b2, b1 = pt(SVIS - 0.5, H), pt(-0.5, H)
win = f"{a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {b1[0]:.1f},{b1[1]:.1f}"
region = f'x="{-DX * 2}" y="{-H - 10:.1f}" width="{WWIN + DX * 4:.1f}" height="{WWIN * SLOPE + 2 * H + 20:.1f}"'

outdir = sys.argv[1].rstrip("/")
for name, theme in THEMES.items():
    path = f"{outdir}/terrain-{name}.svg"
    with open(path, "w") as fh:
        fh.write(render(theme))
    print(path, VW, VH)
