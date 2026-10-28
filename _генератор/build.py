import os, io, json, math, base64, shutil
from PIL import Image
from stars import shape_d, shape_map, to_sheet, cnc_svg, cnc_dxf, bbox, f1
from variants import BIG, SMALL
from nest import best_nest, place, transform_for

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)   # папка проєкту — на рівень вище за _генератор
CNC = os.path.join(PROJ, "ЧПК_розкрій")
if os.path.isdir(CNC):
    shutil.rmtree(CNC)
os.makedirs(CNC)

LAT = {'v1': 'roza', 'v2': 'kolosok', 'v3': 'sontse', 's1': 'iskra', 's2': 'kvitka', 's3': 'siaivo'}
SHEET_W, SHEET_H = 1220, 2440
BASE_D = 2400


def mat_apply(m, p):
    a, b, c, d, e, f = m
    return (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)


def mat_piece(m, s, outline, holes):
    o = [mat_apply(m, p) for p in outline]
    hs = []
    for h in holes:
        if h[0] == 'circle':
            hs.append(('circle', mat_apply(m, h[1]), h[2] * s))
        else:
            hs.append(('poly', [mat_apply(m, p) for p in h[1]]))
    return o, hs


def write_pair(folder, base, pieces, W, H, title):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, base + ".svg"), "w", encoding="utf-8") as f:
        f.write(cnc_svg(pieces, W, H, title))
    with open(os.path.join(folder, base + ".dxf"), "w", encoding="ascii") as f:
        f.write(cnc_dxf(pieces))


# ---------------- ЧПК-файли: великі зірки в кількох розмірах, щільна розкладка
NEST = {}
for s in BIG:
    qo, qh = s.quarter(0)
    smax, th = best_nest(qo)
    dmax = int(BASE_D * smax // 10 * 10)
    sizes = [BASE_D] + [d for d in range(BASE_D + 100, dmax - 49, 100)] + ([dmax] if dmax > BASE_D else [])
    NEST[s.key] = {'max': dmax, 'theta': round(math.degrees(th), 1), 'sizes': {}}
    for D in sizes:
        sc = D / BASE_D
        res = place(qo, th, sc)
        assert res, (s.key, D)
        mA = transform_for(qo, th, sc, 'A', res)
        mB = transform_for(qo, th, sc, 'B', res)
        A = mat_piece(mA, sc, qo, qh)
        B = mat_piece(mB, sc, qo, qh)
        folder = os.path.join(CNC, f"велика_Ø{D}")
        base = f"big_{s.key}_{LAT[s.key]}_D{D}"
        x0, y0, x1, y1 = bbox(A[0])
        one = [([(x - x0, y - y0) for x, y in A[0]], [shape_map(h, lambda p: (p[0] - x0, p[1] - y0)) for h in A[1]])]
        write_pair(folder, base + "_chvert_x4", one, math.ceil(x1 - x0), math.ceil(y1 - y0),
                   f"Велика зірка «{s.name}» Ø{D}, 1/4, фанера 10 мм, різати 4 шт")
        write_pair(folder, base + "_arkush_1220x2440_2chverti", [A, B], SHEET_W, SHEET_H,
                   f"«{s.name}» Ø{D}: 2 чверті на листі 1220×2440 (потрібно 2 листи)")
        NEST[s.key]['sizes'][D] = {'A': [round(v, 5) for v in mA], 'B': [round(v, 5) for v in mB],
                                   'L': round(res[4])}
    print(s.key, 'max', dmax, 'theta', NEST[s.key]['theta'], 'sizes', sizes)

sheets_page = {}
for s in SMALL:
    pc = to_sheet(s.outline, s.holes + [s.axle_hole], 10, 10)
    one = [(pc[0], pc[1])]
    write_pair(os.path.join(CNC, "передня_Ø1200"), f"small_{s.key}_{LAT[s.key]}_cila", one, SHEET_W,
               math.ceil(pc[2][1] + 20), f"Передня зірка «{s.name}» Ø1200, фанера 10 мм, 1 шт")
    sheets_page[s.key] = ([(pc[0], pc[1])], pc[2])

# ---------------- статистика + вітер
Q, CF = 0.5, 1.2   # кПа, аеродинамічний коефіцієнт пластини
stats = {}
for s in BIG + SMALL:
    st = s.stats()
    st['name'] = s.name
    st['wind_kN'] = Q * CF * st['net_m2']
    stats[s.key] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items()}
for s in BIG:
    st = stats[s.key]
    print(s.key, st)
    for w in s.warn:
        print('   !', w)
for s in SMALL:
    print(s.key, stats[s.key])
    for w in s.warn:
        print('   !', w)

# ---------------- SVG-символи зірок
def star_def(s, rim):
    full = s.d()
    holes = s.holes_d()
    return (f'<g id="{"big" if s.R > 700 else "small"}-{s.key}">'
            f'<clipPath id="clip-{s.key}"><path d="{full}" clip-rule="evenodd"/></clipPath>'
            f'<path d="{full}" fill-rule="evenodd" style="fill:var(--face)"/>'
            f'<path d="{holes}" clip-path="url(#clip-{s.key})" style="fill:none;stroke:var(--rim);stroke-width:{rim}"/>'
            f'<circle r="{s.axle + 22}" style="fill:none;stroke:var(--rim);stroke-width:{rim * 0.8}"/>'
            f'</g>')

def quarter_def(s):
    qo, qh = s.quarter(0)
    d = shape_d(('poly', qo)) + "".join(shape_d(h) for h in qh)
    return f'<g id="q-{s.key}"><path d="{d}" fill-rule="evenodd" style="fill:var(--wood);stroke:var(--ink);stroke-width:1;vector-effect:non-scaling-stroke"/></g>'


defs = ("".join(star_def(s, 30) for s in BIG) + "".join(star_def(s, 22) for s in SMALL)
        + "".join(quarter_def(s) for s in BIG))


# ---------------- креслення
def dim_v(x, y1, y2, label, side=-1, fs=150):
    tk = 70
    t = (f'<line class="dm" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/>'
         f'<line class="dm" x1="{x - tk}" y1="{y1 + tk}" x2="{x + tk}" y2="{y1 - tk}"/>'
         f'<line class="dm" x1="{x - tk}" y1="{y2 + tk}" x2="{x + tk}" y2="{y2 - tk}"/>')
    ym = (y1 + y2) / 2
    tx = x + side * 60
    t += (f'<text class="dt" x="{tx}" y="{ym}" font-size="{fs}" text-anchor="middle" '
          f'transform="rotate(-90 {tx} {ym})">{label}</text>')
    return t


def dim_h(y, x1, x2, label, fs=150, below=False):
    tk = 70
    t = (f'<line class="dm" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/>'
         f'<line class="dm" x1="{x1 - tk}" y1="{y + tk}" x2="{x1 + tk}" y2="{y - tk}"/>'
         f'<line class="dm" x1="{x2 - tk}" y1="{y + tk}" x2="{x2 + tk}" y2="{y - tk}"/>')
    ty = y + (fs * 1.1 if below else -50)
    t += f'<text class="dt" x="{(x1 + x2) / 2}" y="{ty}" font-size="{fs}" text-anchor="middle">{label}</text>'
    return t


def quad(p1, p2, w):
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L * w / 2, (x2 - x1) / L * w / 2
    return f"{x1 + nx},{y1 + ny} {x2 + nx},{y2 + ny} {x2 - nx},{y2 - ny} {x1 - nx},{y1 - ny}"


def wheel(cx, cy, r, cls):
    t = f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}"/>'
    t += f'<circle class="ln" cx="{cx}" cy="{cy}" r="{r - 45}" fill="none"/>'
    for i in range(8):
        a = i * math.pi / 4
        t += f'<line class="ln" x1="{cx}" y1="{cy}" x2="{cx + (r - 45) * math.cos(a):.0f}" y2="{cy + (r - 45) * math.sin(a):.0f}"/>'
    hx, hy = cx + r * 0.62, cy - r * 0.62
    t += f'<circle class="knob" cx="{hx:.0f}" cy="{hy:.0f}" r="45"/>'
    return t


AX = -4650          # вісь зірок над землею
PT = -850           # верх постаменту
BT = -1000          # верх основи (брус 150)
TOP = -5000


def pedestal():
    return (f'<rect class="stone" x="-2200" y="-425" width="4400" height="425"/>'
            f'<rect class="stone" x="-1800" y="-850" width="3600" height="425"/>'
            f'<line class="gl" x1="-3600" y1="0" x2="3600" y2="0"/>')


def base_frame():
    t = f'<rect class="wood" x="-1626" y="{BT}" width="3252" height="150"/>'
    for sx in (-1, 1):
        t += f'<rect class="box" x="{sx * 1414 - 250}" y="{BT - 450}" width="500" height="450"/>'
        t += f'<polygon class="wood" points="{quad((sx * 75, -2600), (sx * 1060, BT), 100)}"/>'
    return t


def person(x):
    return (f'<g class="person"><circle cx="{x}" cy="-1620" r="115"/>'
            f'<path d="M{x - 190} -1440 L{x + 190} -1440 L{x + 150} -800 L{x + 120} 0 L{x + 20} 0 L{x} -760 '
            f'L{x - 20} 0 L{x - 120} 0 L{x - 150} -800 Z"/></g>')


def stars_front():
    return (f'<g transform="translate(0 {AX})">'
            f'<line class="rope-b" x1="-320" y1="0" x2="-320" y2="{-1100 - AX}"/>'
            f'<line class="rope-b" x1="320" y1="0" x2="320" y2="{-1100 - AX}"/>'
            f'<g class="spin-big"><use class="u-big" href="#big-v2"/></g>'
            f'<line class="rope-s" x1="-220" y1="0" x2="-220" y2="{-1100 - AX}"/>'
            f'<line class="rope-s" x1="220" y1="0" x2="220" y2="{-1100 - AX}"/>'
            f'<g class="spin-small"><use class="u-small" href="#small-s3"/></g></g>')


front = (f'<svg viewBox="-3500 -6650 6900 7200" class="dwg" role="img" aria-label="Фасад інсталяції з розмірами">'
         + pedestal() + base_frame()
         + f'<use href="#post-deco" transform="translate(0 {BT})"/>'
         + stars_front()
         + f'<rect class="wood" x="-460" y="-1100" width="920" height="100"/>'
         + wheel(-640, -1250, 260, 'wh-b') + wheel(640, -1250, 260, 'wh-s')
         + person(-2950)
         + dim_v(2650, 0, AX, "4650 — вісь", side=-1)
         + dim_v(-2300, BT, TOP, "4000 — колода 150×150", side=-1)
         + dim_v(-3350, 0, PT, "≈850", side=-1)
         + '<g id="dyn-front"></g>'
         + dim_h(330, -1800, 1800, "3600 — верх постаменту", below=True)
         + f'<text class="dt" x="-2950" y="-1850" font-size="140" text-anchor="middle">1,75 м</text>'
         + f'<text class="dt" x="-1414" y="{BT - 520}" font-size="130" text-anchor="middle">баласт</text>'
         + f'<text class="dt" x="0" y="-760" font-size="130" text-anchor="middle">2 колеса для глядачів</text>'
         + '</svg>')

# --- бічний вид
F0 = 75   # передня грань колоди
side_parts = (f'<rect class="wood" x="{F0 + 30}" y="{AX - 320}" width="54" height="640"/>'
              f'<rect class="wood2" x="{F0 + 84}" y="{AX - 600}" width="25" height="1200"/>'
              f'<rect class="face-b" id="side-big" x="{F0 + 109}" y="{AX - 1200}" width="14" height="2400"/>'
              f'<rect class="wood" x="{F0 + 160}" y="{AX - 220}" width="54" height="440"/>'
              f'<rect class="face-s" x="{F0 + 214}" y="{AX - 600}" width="14" height="1200"/>'
              f'<rect class="steel" x="{F0}" y="{AX - 15}" width="262" height="30"/>')
side = (f'<svg viewBox="-3000 -6650 6000 7200" class="dwg" role="img" aria-label="Бічний вид інсталяції">'
        + pedestal() + base_frame()
        + f'<use href="#post-deco" transform="translate(0 {BT})"/>'
        + side_parts
        + f'<polyline class="rope-b" points="{F0 + 57},{AX} {F0 + 57},-1130 1560,-1450"/>'
        + f'<polyline class="rope-b" points="{F0 + 57},-1090 1560,-1050"/>'
        + f'<polyline class="rope-s" points="{F0 + 187},{AX} {F0 + 187},-1160 1560,-1470"/>'
        + f'<polyline class="rope-s" points="{F0 + 187},-1060 1560,-1030"/>'
        + f'<rect class="wood" x="1550" y="-1250" width="100" height="400"/>'
        + f'<rect class="wh-b" x="1530" y="-1510" width="40" height="520"/>'
        + f'<circle cx="{F0 + 130}" cy="{AX}" r="520" class="callout"/>'
        + f'<text class="dt" x="{F0 + 130 + 420}" y="{AX - 420}" font-size="200">А</text>'
        + f'<text class="dt" x="1600" y="-1640" font-size="130" text-anchor="middle">колеса на краю</text>'
        + dim_v(2600, 0, AX, "4650 — вісь", side=-1)
        + dim_h(330, -1800, 1800, "3600", below=True)
        + f'<text class="dt" x="-1800" y="-6150" font-size="150">← до будівлі</text>'
        + f'<text class="dt" x="1800" y="-6150" font-size="150" text-anchor="end">до глядачів →</text>'
        + person(-2500)
        + '</svg>')

# --- вузол А (у мм від передньої грані колоди, y від осі)
def lab(n, x, y, tx, ty):
    return (f'<line class="ld" x1="{x}" y1="{y}" x2="{tx - 18}" y2="{ty}"/>'
            f'<circle class="nb" cx="{tx}" cy="{ty}" r="17"/><text class="nt" x="{tx}" y="{ty + 7}" '
            f'font-size="20" text-anchor="middle">{n}</text>')

detail = ('<svg viewBox="-190 -430 900 870" class="dwg dwg-detail" role="img" aria-label="Вузол А: вісь і підшипники">'
          '<defs><pattern id="hatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          '<line x1="0" y1="0" x2="0" y2="14" class="hl"/></pattern></defs>'
          '<rect class="wood" x="-150" y="-430" width="150" height="860"/>'
          '<rect x="-150" y="-430" width="150" height="860" fill="url(#hatch)"/>'
          # наскрізні шпильки
          '<rect class="steel" x="-170" y="-126" width="190" height="12"/><rect class="steel" x="-170" y="114" width="190" height="12"/>'
          '<rect class="steel" x="-176" y="-140" width="10" height="40"/><rect class="steel" x="-176" y="100" width="10" height="40"/>'
          '<rect class="steel" x="0" y="-160" width="10" height="320"/>'
          # підшипник великої зірки + шків
          '<rect class="brg" x="12" y="-62" width="22" height="124"/>'
          '<rect class="wood" x="34" y="-320" width="18" height="640"/><rect class="wood" x="52" y="-300" width="18" height="600"/>'
          '<rect class="wood" x="70" y="-320" width="18" height="640"/>'
          '<rect class="wood2" x="88" y="-430" width="25" height="860"/>'
          '<rect class="face-b" x="113" y="-430" width="10" height="860"/>'
          '<rect class="steel" x="123" y="-24" width="37" height="48"/>'
          # мала зірка
          '<rect class="brg" x="160" y="-62" width="22" height="124"/>'
          '<rect class="wood" x="182" y="-220" width="18" height="440"/><rect class="wood" x="200" y="-200" width="18" height="400"/>'
          '<rect class="wood" x="218" y="-220" width="18" height="440"/>'
          '<rect class="face-s" x="236" y="-430" width="10" height="860"/>'
          '<rect class="steel" x="246" y="-30" width="12" height="60"/><rect class="steel" x="258" y="-20" width="14" height="40"/>'
          '<rect class="steel" x="10" y="-14" width="268" height="28"/>'
          '<line class="axis" x1="-190" y1="0" x2="300" y2="0"/>'
          # шнури
          '<line class="rope-b" x1="61" y1="300" x2="61" y2="430"/><line class="rope-s" x1="209" y1="200" x2="209" y2="430"/>'
          '<circle class="rope-dot-b" cx="61" cy="300" r="6"/><circle class="rope-dot-s" cx="209" cy="200" r="6"/>'
          + dim_h(-395, 123, 182, "59", fs=20)
          + lab(1, -75, 200, 330, -380) + lab(2, 5, 150, 330, -320) + lab(3, 23, -50, 330, -260)
          + lab(4, 61, -290, 330, -200) + lab(5, 100, -380, 330, -140) + lab(6, 118, -350, 330, -80)
          + lab(7, 140, -20, 330, -20) + lab(8, 209, -190, 330, 40) + lab(9, 241, -300, 330, 100)
          + lab(10, 265, 0, 330, 160) + lab(11, 61, 380, 330, 220) + lab(12, 209, 400, 330, 280)
          + ''.join(f'<text class="dt" x="360" y="{y + 7}" font-size="19">{t}</text>' for y, t in [
              (-380, 'колода 150×150'), (-320, 'пластина 10 мм + 2 шпильки M12'),
              (-260, 'підшипник UCFL205'), (-200, 'шків Ø640/600, 3×18 мм'),
              (-140, 'хрестовина, дошка 25×120'), (-80, 'велика зірка, фанера 10'),
              (-20, 'втулка-дистанція'), (40, 'шків Ø440/400 + UCFL205'),
              (160, 'шайба, гайка, шплінт'), (100, 'передня зірка, фанера 10'),
              (220, 'шнур великої зірки'), (280, 'шнур передньої зірки')])
          + '<text class="dt" x="-180" y="420" font-size="20">вал Ø25, сталь</text>'
          + '</svg>')

# --- розкрій на сторінці
def sheet_svg(key, pieces, H, label):
    body = f'<rect class="sheet" x="0" y="0" width="{SHEET_W}" height="{H}"/>'
    for o, hs in pieces:
        d = shape_d(('poly', o)) + "".join(shape_d(h) for h in hs)
        body += f'<path class="piece" d="{d}" fill-rule="evenodd"/>'
    body += dim_h(-70, 0, SHEET_W, "1220", fs=60) + dim_v(-70, 0, H, str(H), side=-1, fs=60)
    body += f'<text class="dt" x="{SHEET_W / 2}" y="{H + 110}" font-size="64" text-anchor="middle">{label}</text>'
    return (f'<svg viewBox="-170 -170 {SHEET_W + 230} {H + 320}" class="dwg sheet-svg" data-key="{key}" '
            f'role="img" aria-label="{label}">{body}</svg>')

cnc_big = (f'<svg viewBox="-170 -170 {SHEET_W + 230} {SHEET_H + 320}" class="dwg" role="img" '
           f'aria-label="Розкладка двох чвертей на листі 1220×2440">'
           f'<rect class="sheet" x="0" y="0" width="{SHEET_W}" height="{SHEET_H}"/>'
           f'<rect class="used" id="nest-used" x="0" y="0" width="{SHEET_W}" height="{SHEET_H}"/>'
           f'<use id="nest-a" href="#q-v2"/><use id="nest-b" href="#q-v2"/>'
           + dim_h(-70, 0, SHEET_W, "1220", fs=60) + dim_v(-70, 0, SHEET_H, str(SHEET_H), side=-1, fs=60)
           + f'<text class="dt" id="nest-label" x="{SHEET_W / 2}" y="{SHEET_H + 110}" font-size="52" '
             f'text-anchor="middle"></text></svg>')
cnc_small = "".join(sheet_svg(s.key, sheets_page[s.key][0], SHEET_H, "лист 1220×2440 · ціла передня зірка")
                    for s in SMALL)

# ---------------- фото
im = Image.open(os.path.join(PROJ, "photo_2026-10-28_18-34-28.jpg")).convert("RGB")
k = 1100 / im.width
im = im.resize((1100, round(im.height * k)), Image.LANCZOS)
buf = io.BytesIO()
im.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
photo = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
PH = im.height

# поверх фото: центр верху постаменту і кути (у px зменшеного фото)
CX, CY = 586, 955
S = 0.195 * k      # px/мм
corners = {'L': (303.5, 938), 'F': (479, 976.7), 'R': (868.3, 972.7), 'B': (692.6, 934.5)}


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def mm(x, y):
    return (CX + x * S, CY + y * S)


mont = []
C = (CX, CY)
for c in ('B', 'L', 'R', 'F'):
    p = lerp(C, corners[c], 0.9)
    mont.append(f'<polygon class="m-wood" points="{quad(C, p, 14)}"/>')
for c in ('B', 'L', 'R', 'F'):
    p = lerp(C, corners[c], 0.78)
    w, h = 500 * S, 450 * S
    mont.append(f'<rect class="m-box" x="{p[0] - w / 2:.1f}" y="{p[1] - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2"/>')
    if c == 'B':
        mont.append(f'<rect class="m-wood" x="{CX - 75 * S:.1f}" y="{CY - 4150 * S:.1f}" width="{150 * S:.1f}" height="{4150 * S:.1f}"/>')
        mont.append(f'<use href="#post-deco" transform="translate({CX} {CY - 150 * S:.1f}) scale({S:.5f})"/>')
for c in ('L', 'R', 'F'):
    p = lerp(C, corners[c], 0.59)
    top = mm(0, -1800)
    mont.append(f'<polygon class="m-wood" points="{quad(top, p, 10)}"/>')
ax = mm(0, -3800)
FR = lerp(corners['F'], corners['R'], 0.35)
FR2 = lerp(corners['F'], corners['R'], 0.6)
mont.append(f'<g class="m-glow"><circle fill="url(#glow)" cx="{ax[0]:.1f}" cy="{ax[1]:.1f}" r="{1500 * S:.1f}"/></g>')
for dx, cls in ((-320, 'rope-b'), (320, 'rope-b')):
    mont.append(f'<line class="{cls} m-rope" x1="{ax[0] + dx * S:.1f}" y1="{ax[1]:.1f}" x2="{ax[0] + dx * S:.1f}" y2="{CY - 260 * S:.1f}"/>')
mont.append(f'<g transform="translate({ax[0]:.1f} {ax[1]:.1f}) scale({S:.5f})">'
            f'<g class="spin-big"><use class="u-big" href="#big-v2"/></g>'
            f'<line class="rope-s" x1="-220" y1="0" x2="-220" y2="3540"/><line class="rope-s" x1="220" y1="0" x2="220" y2="3540"/>'
            f'<g class="spin-small"><use class="u-small" href="#small-s3"/></g></g>')
for p, cls in ((FR, 'wh-b'), (FR2, 'wh-s')):
    wy = p[1] - 350 * S
    mont.append(f'<line class="m-rope rope-{"b" if cls == "wh-b" else "s"}" x1="{CX:.1f}" y1="{CY - 260 * S:.1f}" x2="{p[0]:.1f}" y2="{wy:.1f}"/>')
    mont.append(f'<rect class="m-wood" x="{p[0] - 50 * S:.1f}" y="{wy:.1f}" width="{100 * S:.1f}" height="{350 * S:.1f}"/>')
    mont.append(f'<g transform="translate({p[0]:.1f} {wy:.1f}) scale({S:.5f})">{wheel(0, 0, 260, cls)}</g>')
montage = (f'<svg viewBox="150 260 860 1010" class="montage" role="img" aria-label="Ескіз на фото постаменту">'
           f'<image href="{photo}" x="0" y="0" width="1100" height="{PH}"/>'
           f'<rect x="0" y="0" width="1100" height="{PH}" class="m-dim"/>' + "".join(mont) + '</svg>')

# ---------------- збірка HTML
tpl = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
out = (tpl.replace("%%DEFS%%", defs).replace("%%MONTAGE%%", montage).replace("%%FRONT%%", front)
       .replace("%%SIDE%%", side).replace("%%DETAIL%%", detail)
       .replace("%%CNC_BIG%%", cnc_big).replace("%%CNC_SMALL%%", cnc_small)
       .replace("%%STATS%%", json.dumps(stats, ensure_ascii=False))
       .replace("%%NEST%%", json.dumps(NEST, ensure_ascii=False)))
dst = os.path.join(PROJ, "zirka-eskiz.html")
open(dst, "w", encoding="utf-8").write(out)
# окрема повна сторінка для GitHub Pages: свій doctype, viewport і базовий скид стилів
page = ('<!doctype html>\n<html lang="uk">\n<head>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>body{margin:0}img{max-width:100%}:root{padding-top:env(safe-area-inset-top,0px);'
        'padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n' + out + '\n</html>\n')
open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8").write(page)
print("html", len(out) // 1024, "KB")
print(sorted(os.listdir(CNC)))
