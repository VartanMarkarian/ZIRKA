"""Щільна розкладка двох однакових чвертей на лист: друга повернута на 180° і входить променями в першу."""
import math
from stars import rot, bbox

SHEET_W, SHEET_H = 1220, 2440
EDGE = 10      # поле від краю листа
GAP = 12       # мінімальна відстань між деталями (≥ діаметра фрези)
COL = 2.0      # крок колонок, мм


def dense(pts, step=2.0):
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n) for t in range(n)]
    return out


def place(outline, theta, s):
    """Повертає (A, B) як списки точок контуру в координатах листа (y вниз) або None, якщо не влазить."""
    p = [rot((x * s, y * s), theta) for x, y in outline]
    x0, y0, x1, y1 = bbox(p)
    if x1 - x0 > SHEET_W - 2 * EDGE:
        return None
    A = [(x - x0 + EDGE, y - y0 + EDGE) for x, y in p]
    w, h = x1 - x0, y1 - y0
    B0 = [(EDGE + w - (x - EDGE), EDGE + h - (y - EDGE)) for x, y in A]   # 180° у тій самій рамці
    # профілі по колонках: верх A (макс. y) і низ B (мін. y)
    top, bot = {}, {}
    for x, y in dense(A):
        c = int(x // COL)
        top[c] = max(top.get(c, -1e9), y)
    for x, y in dense(B0):
        c = int(x // COL)
        bot[c] = min(bot.get(c, 1e9), y)
    k = int(math.ceil(GAP / COL))
    dy = -1e9
    for c, yb in bot.items():
        t = max((top.get(c + j, -1e9) for j in range(-k, k + 1)), default=-1e9)
        dy = max(dy, t + GAP - yb)
    B = [(x, y + dy) for x, y in B0]
    L = max(y for _, y in B) + EDGE
    if L > SHEET_H:
        return None
    return A, B, theta, dy, L


def best_nest(outline, s_min=1.0, s_max=1.25):
    """Найбільший масштаб s, за якого дві чверті влазять на лист; перебір кута повороту."""
    best = None
    for i in range(0, 181):
        th = math.radians(i * 0.5)
        lo, hi = s_min if best is None else best[0], s_max
        if place(outline, th, lo) is None:
            continue
        for _ in range(22):
            mid = (lo + hi) / 2
            if place(outline, th, mid):
                lo = mid
            else:
                hi = mid
        if best is None or lo > best[0]:
            best = (lo, th)
    return best


def transform_for(outline, theta, s, which, res):
    """Матриця (a,b,c,d,e,f) SVG, що переводить локальну чверть у позицію на листі."""
    A, B, th, dy, L = res
    p = [rot((x * s, y * s), theta) for x, y in outline]
    x0, y0, x1, y1 = bbox(p)
    c, sn = math.cos(theta) * s, math.sin(theta) * s
    if which == 'A':
        return (c, sn, -sn, c, EDGE - x0, EDGE - y0)
    w, h = x1 - x0, y1 - y0
    # B = 180° навколо центру рамки + зсув dy
    return (-c, -sn, sn, -c, EDGE + w + x0, EDGE + h + y0 + dy)
