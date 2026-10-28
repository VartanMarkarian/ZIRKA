"""Генератор зірок: геометрія (мм), перевірка перемичок, SVG/DXF для ЧПК, SVG-символи для ескізу."""
import math

TAU = 2 * math.pi


def rot(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


# ---------- фігури: ('poly', pts) | ('circle', (cx, cy), r)
def shape_rot(sh, a):
    if sh[0] == 'circle':
        return ('circle', rot(sh[1], a), sh[2])
    return ('poly', [rot(p, a) for p in sh[1]])


def shape_map(sh, f):
    if sh[0] == 'circle':
        return ('circle', f(sh[1]), sh[2])
    return ('poly', [f(p) for p in sh[1]])


def poly_area(pts):
    s = 0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def poly_perim(pts):
    return sum(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))


def shape_area(sh):
    return math.pi * sh[2] ** 2 if sh[0] == 'circle' else poly_area(sh[1])


def shape_perim(sh):
    return TAU * sh[2] if sh[0] == 'circle' else poly_perim(sh[1])


def shape_center(sh):
    if sh[0] == 'circle':
        return sh[1]
    xs = [p[0] for p in sh[1]]
    ys = [p[1] for p in sh[1]]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def shape_samples(sh):
    if sh[0] == 'circle':
        (cx, cy), r = sh[1], sh[2]
        return [(cx + r * math.cos(t * TAU / 48), cy + r * math.sin(t * TAU / 48)) for t in range(48)]
    return sh[1]


def f1(v):
    return f"{v:.1f}".rstrip('0').rstrip('.')


def shape_d(sh, flip=False):
    sy = -1 if flip else 1
    if sh[0] == 'circle':
        (cx, cy), r = sh[1], sh[2]
        cy *= sy
        return (f"M{f1(cx + r)} {f1(cy)}A{f1(r)} {f1(r)} 0 1 0 {f1(cx - r)} {f1(cy)}"
                f"A{f1(r)} {f1(r)} 0 1 0 {f1(cx + r)} {f1(cy)}Z")
    pts = sh[1]
    return "M" + "L".join(f"{f1(x)} {f1(y * sy)}" for x, y in pts) + "Z"


# ---------- мотиви (локальні координати променя: вісь X — від центру до вершини)
def rhombus(x0, x1, b):
    xc = (x0 + x1) / 2
    return ('poly', [(x0, 0), (xc, -b), (x1, 0), (xc, b)])


def lens(x0, x1, b, n=14):
    a = (x1 - x0) / 2
    xc = x0 + a
    R0 = (a * a + b * b) / (2 * b)
    up = []
    for i in range(n + 1):
        x = -a + 2 * a * i / n
        y = math.sqrt(max(R0 * R0 - x * x, 0)) - (R0 - b)
        up.append((xc + x, max(y, 0)))
    lo = [(x, -y) for x, y in reversed(up[1:-1])]
    return ('poly', up + lo)


def drop(x0, x1, b, out=True, n=20):
    """Крапля: кругла частина біля x0, гострий кінчик у x1 (out=True) або навпаки."""
    r = b
    c = x0 + r
    d = x1 - c
    if d <= r * 1.05:
        return None
    phi = math.acos(r / d)
    pts = [(x1, 0)]
    for i in range(n + 1):
        a = phi + (TAU - 2 * phi) * i / n
        pts.append((c + r * math.cos(a), r * math.sin(a)))
    if not out:
        m = x0 + x1
        pts = [(m - x, y) for x, y in pts]
    return ('poly', pts)


def dot(x0, x1, b):
    return ('circle', ((x0 + x1) / 2, 0), min(b, (x1 - x0) / 2))


def slot(p1, p2, w, n=8):
    """Проріз-«зернятко» зі заокругленими кінцями."""
    (x1, y1), (x2, y2) = p1, p2
    a = math.atan2(y2 - y1, x2 - x1)
    r = w / 2
    pts = []
    for i in range(n + 1):
        t = a - math.pi / 2 - math.pi * i / n
        pts.append((x1 + r * math.cos(t), y1 + r * math.sin(t)))
    for i in range(n + 1):
        t = a + math.pi / 2 - math.pi * i / n
        pts.append((x2 + r * math.cos(t), y2 + r * math.sin(t)))
    return ('poly', pts)


# ---------- мотиви українського модерну й різьблення
def trap(x0, x1, b):
    """Трапеція, ширша до центру."""
    return ('poly', [(x0, -b), (x1, -0.55 * b), (x1, 0.55 * b), (x0, b)])


def hexa(x0, x1, b):
    """Видовжений шестикутник."""
    a = x1 - x0
    return ('poly', [(x0, 0), (x0 + 0.28 * a, -b), (x1 - 0.28 * a, -b), (x1, 0), (x1 - 0.28 * a, b), (x0 + 0.28 * a, b)])


def tri(x0, x1, b):
    """Трикутна виїмка вершиною назовні."""
    return ('poly', [(x0, -b), (x1, 0), (x0, b)])


def triin(x0, x1, b):
    """Трикутна виїмка вершиною до центру."""
    return ('poly', [(x1, -b), (x1, b), (x0, 0)])


# крин (тюльпан): ніжка біля x0, середня пелюстка до x1, бічні пелюстки розходяться
TULIP = [(0, -0.20), (0.16, -0.20), (0.22, -0.50), (0.32, -0.82), (0.46, -1.0), (0.60, -0.96),
         (0.50, -0.74), (0.44, -0.46), (0.60, -0.44), (0.80, -0.34), (0.94, -0.17), (1.0, 0)]


def tulip(x0, x1, b):
    L = x1 - x0
    lower = [(x0 + u * L, v * b) for u, v in TULIP]
    upper = [(x, -y) for x, y in reversed(lower[:-1])]
    return ('poly', lower + upper)


def whirl(x0, x1, b, d0, d1, n=28):
    """Серп вихрової розетки: дуга від (x0, -d0) до (x1, d1), найтовща посередині."""
    P0, P1, P2 = (x0, -d0), ((x0 + x1) / 2 + 0.1 * (x1 - x0), -1.2 * d0), (x1, d1)
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        cx = (1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * P1[0] + t * t * P2[0]
        cy = (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * P1[1] + t * t * P2[1]
        dx = 2 * (1 - t) * (P1[0] - P0[0]) + 2 * t * (P2[0] - P1[0])
        dy = 2 * (1 - t) * (P1[1] - P0[1]) + 2 * t * (P2[1] - P1[1])
        L = math.hypot(dx, dy) or 1
        w = b * math.sin(math.pi * t) ** 0.85
        left.append((cx - dy / L * w, cy + dx / L * w))
        right.append((cx + dy / L * w, cy - dx / L * w))
    return ('poly', left + right[::-1][1:-1])


MOTIFS = {'rhombus': rhombus, 'lens': lens, 'drop': lambda x0, x1, b: drop(x0, x1, b, True),
          'dropin': lambda x0, x1, b: drop(x0, x1, b, False), 'dot': dot,
          'trap': trap, 'hexa': hexa, 'tri': tri, 'triin': triin, 'tulip': tulip}


# ---------- зірка
class Star:
    def __init__(self, key, name, N, R, r_in, profile=(), alt=None, axle=30,
                 margin=40, seam_margin=55, r_clear=0, motifs=None, split4=False, extra=None):
        self.key, self.name, self.N, self.R, self.r_in = key, name, N, R, r_in
        self.profile = profile          # [(t, s)] — точки між западиною і вершиною
        self.alt = alt                  # радіус коротких променів (через один)
        self.axle, self.margin, self.seam_margin = axle, margin, seam_margin
        self.r_clear = r_clear
        self.motifs = motifs or {}      # {'long': [...], 'short': [...]}
        self.extra = extra
        self.split4 = split4
        self.half = math.pi / N
        self.warn = []
        self.build()

    def tip(self, k):
        return self.alt if (self.alt and k % 2 == 1) else self.R

    def half_profile(self, Rk):
        """Верхня половина променя: від западини до вершини (локально)."""
        xv, yv = self.r_in * math.cos(self.half), self.r_in * math.sin(self.half)
        pts = [(xv, yv)]
        for t, s in self.profile:
            x = xv + t * (Rk - xv)
            y = yv * (1 - t) * s
            pts.append((x, y))
        pts.append((Rk, 0.0))
        return pts

    def hf(self, x, Rk, m_ray, m_seam):
        """Допустима напівширина отвору в точці x з урахуванням перемички."""
        hp = self.half_profile(Rk)
        xv = hp[0][0]
        if x < xv:
            return x * math.tan(self.half) - m_seam / math.cos(self.half)
        for (xa, ya), (xb, yb) in zip(hp, hp[1:]):
            if xa <= x <= xb:
                y = ya + (yb - ya) * (x - xa) / (xb - xa)
                slope = abs(yb - ya) / (xb - xa)
                return y - m_ray * math.sqrt(1 + slope * slope)
        return -1

    def fits(self, sh, Rk):
        for x, y in shape_samples(sh):
            if x < self.r_clear or abs(y) > self.hf(x, Rk, self.margin, self.seam_margin):
                return False
        return True

    def fit_motif(self, kind, x0, x1, Rk, bmax, dy=0.0):
        if kind.startswith('whirl:'):
            d0, d1 = (float(v) for v in kind.split(':')[1:3])
            gen = lambda a, c, b: whirl(a, c, b, d0, d1)
        else:
            gen = MOTIFS[kind]
        lo, hi = 0.0, bmax
        best = None
        for _ in range(30):
            mid = (lo + hi) / 2
            sh = gen(x0, x1, mid)
            if sh is not None and dy:
                sh = shape_map(sh, lambda p: (p[0], p[1] + dy))
            if sh is not None and self.fits(sh, Rk):
                best, lo = sh, mid
            else:
                hi = mid
        if best is None or lo < 9:
            self.warn.append(f"{self.key}: мотив {kind} {x0}-{x1} не вміщується")
            return None
        return best

    def ray_holes(self, typ, Rk):
        out = []
        for m in self.motifs.get(typ, []):
            if m[0] == 'herring':
                _, xs, xe, step, length, ang, w = m
                x = xs
                while x + length * math.cos(ang) <= xe:
                    for sgn in (1, -1):
                        y0 = sgn * (w / 2 + 8)
                        p1 = (x, y0)
                        p2 = (x + length * math.cos(ang), y0 + sgn * length * math.sin(ang))
                        sh = slot(p1, p2, w)
                        ln = length
                        while not self.fits(sh, Rk) and ln > w:
                            ln -= 4
                            p2 = (x + ln * math.cos(ang), y0 + sgn * ln * math.sin(ang))
                            sh = slot(p1, p2, w)
                        if self.fits(sh, Rk) and ln > w * 1.3:
                            out.append(sh)
                    x += step
                continue
            if m[0] == 'pair':
                _, kind, x0, x1, dy, bmax = m
                sh = self.fit_motif(kind, x0, x1, Rk, bmax, dy)
                if sh:
                    out.append(sh)
                    out.append(shape_map(sh, lambda p: (p[0], -p[1])))
                continue
            kind, x0, x1, bmax = m
            sh = self.fit_motif(kind, x0, x1, Rk, bmax)
            if sh:
                out.append(sh)
        return out

    def build(self):
        N = self.N
        self.ray_angle = [-math.pi / 2 + k * TAU / N for k in range(N)]
        outline = []
        self.valley_index = []
        holes = []
        cache = {}
        for k in range(N):
            Rk = self.tip(k)
            hp = self.half_profile(Rk)
            lower = [(x, -y) for x, y in hp[1:-1]]
            upper = [(x, y) for x, y in reversed(hp[1:-1])]
            local = lower + [(Rk, 0.0)] + upper
            a = self.ray_angle[k]
            outline += [rot(p, a) for p in local]
            outline.append(rot((self.r_in, 0), a + self.half))
            self.valley_index.append(len(outline) - 1)
            typ = 'short' if (self.alt and k % 2 == 1) else 'long'
            if typ not in cache:
                cache[typ] = self.ray_holes(typ, Rk)
            holes += [shape_rot(h, a) for h in cache[typ]]
        # першою точкою контуру робимо западину перед променем 0
        self.outline = [rot((self.r_in, 0), self.ray_angle[0] - self.half)] + outline[:-1]
        self.valley_index = [0] + [i + 1 for i in self.valley_index[:-1]]
        self.holes = holes
        self.axle_hole = ('circle', (0, 0), self.axle)
        self.cache = cache

    # ----- статистика
    def stats(self):
        A = poly_area(self.outline)
        H = sum(shape_area(h) for h in self.holes)
        net = A - H - shape_area(self.axle_hole)
        cut = poly_perim(self.outline) + sum(shape_perim(h) for h in self.holes) + shape_perim(self.axle_hole)
        return dict(rays=self.N, outline_m2=A / 1e6, holes_m2=H / 1e6, net_m2=net / 1e6,
                    open_pct=100 * H / A, cut_m=cut / 1000, weight_kg=net / 1e6 * 6.5,
                    holes=len(self.holes))

    def d(self, flip=False):
        parts = [shape_d(('poly', self.outline), flip)] + [shape_d(h, flip) for h in self.holes] + \
                [shape_d(self.axle_hole, flip)]
        return "".join(parts)

    def holes_d(self):
        return "".join(shape_d(h) for h in self.holes)

    # ----- четвертинка
    def quarter(self, q=0):
        """Повертає (контур, отвори) чверті q у системі, де шов-початок лежить на куті 0."""
        N = self.N
        j0 = (q * N // 4) % N
        j1 = ((q + 1) * N // 4) % N
        i0, i1 = self.valley_index[j0], self.valley_index[j1]
        n = len(self.outline)
        seg = []
        i = i0
        while True:
            seg.append(self.outline[i])
            if i == i1 and len(seg) > 1:
                break
            i = (i + 1) % n
        a0 = math.atan2(seg[0][1], seg[0][0])
        a1 = math.atan2(seg[-1][1], seg[-1][0])
        span = (a1 - a0) % TAU
        r = self.axle
        arc = [(r * math.cos(a0 + span * (1 - t / 12)), r * math.sin(a0 + span * (1 - t / 12))) for t in range(13)]
        pts = seg + arc
        hs = []
        for h in self.holes:
            cx, cy = shape_center(h)
            ang = (math.atan2(cy, cx) - a0) % TAU
            if ang < span:
                hs.append(h)
        pts = [rot(p, -a0) for p in pts]
        hs = [shape_rot(h, -a0) for h in hs]
        return pts, hs


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# ---------- експорт для ЧПК
def cnc_svg(pieces, W, H, title):
    """pieces: [(outline_pts, holes)] вже в координатах листа (мм, y вниз)."""
    body = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="20 10"/>']
    for outline, holes in pieces:
        body.append(f'<path d="{shape_d(("poly", outline))}" fill="none" stroke="#000" stroke-width="0.5"/>')
        for h in holes:
            if h[0] == 'circle':
                (cx, cy), r = h[1], h[2]
                body.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="#e00" stroke-width="0.5"/>')
            else:
                body.append(f'<path d="{shape_d(h)}" fill="none" stroke="#e00" stroke-width="0.5"/>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">\n<title>{title}</title>\n'
            + "\n".join(body) + "\n</svg>\n")


def cnc_dxf(pieces):
    out = ["0", "SECTION", "2", "ENTITIES"]

    def pl(pts, layer):
        out.extend(["0", "POLYLINE", "8", layer, "66", "1", "70", "1"])
        for x, y in pts:
            out.extend(["0", "VERTEX", "8", layer, "10", f"{x:.2f}", "20", f"{-y:.2f}"])
        out.extend(["0", "SEQEND", "8", layer])

    for outline, holes in pieces:
        pl(outline, "CONTOUR")
        for h in holes:
            if h[0] == 'circle':
                (cx, cy), r = h[1], h[2]
                out.extend(["0", "CIRCLE", "8", "HOLES", "10", f"{cx:.2f}", "20", f"{-cy:.2f}", "40", f"{r:.2f}"])
            else:
                pl(h[1], "HOLES")
    out.extend(["0", "ENDSEC", "0", "EOF"])
    return "\n".join(out) + "\n"


def to_sheet(outline, holes, dx, dy, flip180=False, ext=None):
    """Переносить деталь на лист: y вниз, зсув dx/dy; flip180 — поворот на 180° в межах ext."""
    def f(p):
        x, y = p
        y = -y
        return x, y
    o = [f(p) for p in outline]
    hs = [shape_map(h, f) for h in holes]
    x0, y0, x1, y1 = bbox(o)
    if flip180:
        def g(p):
            return (x1 - (p[0] - x0), y1 - (p[1] - y0))
        o = [g(p) for p in o]
        hs = [shape_map(h, g) for h in hs]
        x0, y0, x1, y1 = bbox(o)

    def t(p):
        return (p[0] - x0 + dx, p[1] - y0 + dy)
    return [t(p) for p in o], [shape_map(h, t) for h in hs], (x1 - x0, y1 - y0)
