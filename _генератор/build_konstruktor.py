"""Збирає сторінку конструктора звізд: konstruktor/index.html зі сценами в стилі народного малярства,
де звізда з конструктора показана в різних місцях."""
import os, math, random, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, "konstruktor")
os.makedirs(OUT, exist_ok=True)

# звізда з конструктора: основний шар, другий шар і прикраси (JS оновлює всі такі групи разом)
SLOT = ('<g class="m-spin"><use href="#k-star"/><g class="deco-fix"></g></g>'
        '<g class="spin2" hidden><use href="#k-star2"/></g><g class="deco-hang"></g>')
rnd = random.Random(11)
INK = '#1d1410'                       # темний контур, як пензлем
RED, YEL, GRN, BLU, OCH, WHT = '#c3262e', '#f2c230', '#2f7a3a', '#2c4f9a', '#e0912a', '#f6efe0'


def ol(w=2):
    return f' stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def star(x, y, k, glow=True):
    """Звізда з конструктора радіусом 1200·k px."""
    g = f'<circle cx="{x}" cy="{y}" r="{1500 * k:.1f}" fill="url(#glow)"/>' if glow else ''
    return g + f'<g transform="translate({x} {y}) scale({k})">{SLOT}</g>'


def fstar(x, y, r, fill=YEL):
    """Восьмипроменева зірочка неба, як у народному розписі."""
    pts = ' '.join(f'{x + (r if i % 2 == 0 else r * .42) * math.cos(i * math.pi / 8 - math.pi / 2):.1f},'
                   f'{y + (r if i % 2 == 0 else r * .42) * math.sin(i * math.pi / 8 - math.pi / 2):.1f}' for i in range(16))
    return f'<polygon points="{pts}" fill="{fill}"{ol(1.2)}/>'


def flake(x, y, r, c=WHT):
    o = ''.join(f'<line x1="{x - r * math.cos(a):.1f}" y1="{y - r * math.sin(a):.1f}" x2="{x + r * math.cos(a):.1f}" y2="{y + r * math.sin(a):.1f}" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>'
                for a in (0, math.pi / 3, 2 * math.pi / 3))
    return o + f'<circle cx="{x}" cy="{y}" r="1.4" fill="{c}"/>'


def sky_bits(n_star, n_flake, y1=150, x0=20, x1=380, y0=20):
    o = ''
    for _ in range(n_star):
        o += fstar(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(3, 6.5), rnd.choice([YEL, YEL, WHT]))
    for _ in range(n_flake):
        o += flake(rnd.uniform(x0, x1), rnd.uniform(y0, y1 + 90), rnd.uniform(2.5, 4.5))
    return o


def dots_row(x0, x1, y, step=9, r=1.8, c=BLU, wave=0.0):
    return ''.join(f'<circle cx="{x}" cy="{y + wave * math.sin(x / 23):.1f}" r="{r}" fill="{c}"/>' for x in range(int(x0), int(x1), step))


def flower(x, y, r, petal=RED, core=YEL):
    """Квітка з п'яти пелюсток-крапель і серединки."""
    o = ''
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        px, py = x + r * .62 * math.cos(a), y + r * .62 * math.sin(a)
        o += f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * .42:.1f}" ry="{r * .26:.1f}" transform="rotate({math.degrees(a):.0f} {px:.1f} {py:.1f})" fill="{petal}"{ol(1)}/>'
    return o + f'<circle cx="{x}" cy="{y}" r="{r * .28:.1f}" fill="{core}"{ol(1)}/>'


def leaf(x, y, L, ang, c=GRN):
    return (f'<ellipse cx="{x + L / 2 * math.cos(ang):.1f}" cy="{y + L / 2 * math.sin(ang):.1f}" rx="{L / 2:.1f}" ry="{L / 5:.1f}" '
            f'transform="rotate({math.degrees(ang):.0f} {x + L / 2 * math.cos(ang):.1f} {y + L / 2 * math.sin(ang):.1f})" fill="{c}"{ol(1)}/>')


def kalyna(x, y, s=1.0, flip=1):
    """Гілка калини: стебло, листки, грона ягід."""
    o = f'<path d="M{x} {y}Q{x + 18 * s * flip} {y - 30 * s} {x + 8 * s * flip} {y - 62 * s}" fill="none"{ol(2.2)}/>'
    for t, side in ((.3, 1), (.55, -1), (.8, 1)):
        px, py = x + 14 * s * flip * t, y - 62 * s * t
        o += leaf(px, py, 18 * s, -math.pi / 2 + side * flip * .9)
    for cx, cy in ((x + 10 * s * flip, y - 64 * s), (x + 22 * s * flip, y - 40 * s)):
        for i in range(6):
            a = i * math.pi / 3
            o += f'<circle cx="{cx + 5 * s * math.cos(a):.1f}" cy="{cy + 5 * s * math.sin(a):.1f}" r="{3.2 * s:.1f}" fill="{RED}"{ol(.9)}/>'
        o += f'<circle cx="{cx}" cy="{cy}" r="{3.2 * s:.1f}" fill="{RED}"{ol(.9)}/>'
    return o


def bird(x, y, s=1.0, flip=1, body=OCH):
    """Птах у дусі народного розпису: тулуб-крапля, крило з горошком, хвіст віялом."""
    f = flip
    o = (f'<path d="M{x - 26 * s * f} {y - 4 * s}L{x - 42 * s * f} {y - 18 * s}L{x - 40 * s * f} {y + 2 * s}L{x - 44 * s * f} {y + 14 * s}Z" fill="{RED}"{ol(1.4)}/>'
         f'<path d="M{x - 28 * s * f} {y}Q{x - 6 * s * f} {y - 22 * s} {x + 14 * s * f} {y - 8 * s}Q{x + 6 * s * f} {y + 14 * s} {x - 28 * s * f} {y}Z" fill="{body}"{ol(1.6)}/>'
         f'<circle cx="{x + 14 * s * f}" cy="{y - 12 * s}" r="{6 * s}" fill="{body}"{ol(1.4)}/>'
         f'<path d="M{x + 19 * s * f} {y - 13 * s}L{x + 26 * s * f} {y - 11 * s}L{x + 19 * s * f} {y - 9 * s}Z" fill="{YEL}"{ol(1)}/>'
         f'<circle cx="{x + 15 * s * f}" cy="{y - 13 * s}" r="{1.3 * s}" fill="{INK}"/>'
         f'<path d="M{x - 14 * s * f} {y - 4 * s}Q{x - 2 * s * f} {y - 16 * s} {x + 6 * s * f} {y - 4 * s}Z" fill="{GRN}"{ol(1.2)}/>')
    o += ''.join(f'<circle cx="{x + (-8 + i * 5) * s * f:.1f}" cy="{y + 3 * s:.1f}" r="{1.4 * s:.1f}" fill="{WHT}"/>' for i in range(4))
    return o


def person(x, base, h, coat, reach):
    """Колядник: кучма, рум'яні щоки, кожух з вишитою облямівкою, червоні чоботи, держак зі звіздою."""
    t = base - h
    return (f'<line x1="{x + 13}" y1="{base - 4}" x2="{x + 13}" y2="{reach}" stroke="#8a5a2a" stroke-width="3.2"/>'
            f'<line x1="{x + 13}" y1="{base - 4}" x2="{x + 13}" y2="{reach}" stroke="{INK}" stroke-width="1" opacity=".5"/>'
            f'<ellipse cx="{x - 6}" cy="{base - 2}" rx="6" ry="3.5" fill="{RED}"{ol(1.2)}/><ellipse cx="{x + 6}" cy="{base - 2}" rx="6" ry="3.5" fill="{RED}"{ol(1.2)}/>'
            f'<path d="M{x - 10} {t + 20}Q{x} {t + 15} {x + 10} {t + 20}L{x + 16} {base - 6}Q{x} {base - 2} {x - 16} {base - 6}Z" fill="{coat}"{ol(1.8)}/>'
            + ''.join(f'<path d="M{x - 13 + i * 5} {base - 9}l2 -2 2 2 -2 2z" fill="{YEL}"/>' for i in range(6))
            + f'<line x1="{x}" y1="{t + 22}" x2="{x}" y2="{base - 8}" stroke="{WHT}" stroke-width="1.6" stroke-dasharray="2 3"/>'
            f'<path d="M{x + 8} {t + 26}Q{x + 14} {t + 22} {x + 13} {t + 16}" fill="none" stroke="{coat}" stroke-width="5" stroke-linecap="round"/>'
            f'<circle cx="{x}" cy="{t + 11}" r="8.5" fill="#f1c9a5"{ol(1.6)}/>'
            f'<circle cx="{x - 4}" cy="{t + 13.5}" r="2" fill="#e8707a"/><circle cx="{x + 4}" cy="{t + 13.5}" r="2" fill="#e8707a"/>'
            f'<circle cx="{x - 3}" cy="{t + 10}" r="1" fill="{INK}"/><circle cx="{x + 3}" cy="{t + 10}" r="1" fill="{INK}"/>'
            f'<path d="M{x - 10} {t + 7}Q{x - 9} {t - 7} {x} {t - 7}Q{x + 9} {t - 7} {x + 10} {t + 7}Z" fill="#2a1d16"{ol(1.4)}/>')


def frame(i):
    """Розписна рамка: червоне тло, жовті горошини, квіточки в кутах."""
    o = (f'<path d="M0 0H400V280H0ZM14 14V266H386V14Z" fill-rule="evenodd" fill="{RED}"/>'
         f'<rect x="7" y="7" width="386" height="266" fill="none" stroke="{YEL}" stroke-width="4" stroke-dasharray="0.01 10" stroke-linecap="round"/>'
         f'<rect x="14" y="14" width="372" height="252" fill="none"{ol(2.4)}/><rect x="1" y="1" width="398" height="278" fill="none"{ol(2)}/>')
    return o + ''.join(flower(x, y, 7.5, YEL, RED) for x, y in ((14, 14), (386, 14), (14, 266), (386, 266)))


def scene(i, body):
    return (f'<defs><clipPath id="sc{i}"><rect x="14" y="14" width="372" height="252"/></clipPath></defs>'
            f'<g clip-path="url(#sc{i})">{body}</g>' + frame(i))


def hill(y, c=WHT, amp=10):
    return f'<path d="M0 {y}Q100 {y - amp} 200 {y}T400 {y - 2}V280H0Z" fill="{c}"{ol(2)}/>'


SCENES = []

# 1. Хода звіздарів
b = '<rect width="400" height="280" fill="#16205a"/>' + sky_bits(14, 22, 120)
for hx, hy, w in ((40, 196, 54), (300, 192, 60)):
    b += (f'<rect x="{hx}" y="{hy}" width="{w}" height="26" fill="{WHT}"{ol(1.6)}/>'
          f'<path d="M{hx - 6} {hy + 2}L{hx + w / 2} {hy - 22}L{hx + w + 6} {hy + 2}Z" fill="{OCH}"{ol(1.6)}/>'
          f'<rect x="{hx + w / 2 - 6}" y="{hy + 8}" width="12" height="10" fill="{YEL}"{ol(1.2)}/>')
b += hill(222) + dots_row(10, 400, 238, 10, 1.8, BLU, 2) + dots_row(16, 400, 252, 12, 1.6, BLU, 2)
for x, k, coat, base, hgt in ((110, .022, RED, 262, 64), (200, .03, GRN, 266, 70), (290, .022, BLU, 262, 64)):
    sy = base - hgt - (44 if k > .025 else 36)
    b += person(x, base, hgt, coat, sy) + star(x + 13, sy, k)
b += kalyna(30, 262, .8, 1) + kalyna(370, 262, .8, -1)
SCENES.append(('Хода звіздарів', scene(1, b), 'Звізда на держаку, як у колядників. Ø 45–60 см: половини чи чверті на A3, з клапанами для склеювання.'))

# 2. На підвіконні
b = f'<rect width="400" height="280" fill="#efdcb4"/>'
b += ''.join(flower(x, 30, 6, RED, YEL) + leaf(x - 4, 30, 12, math.pi * .85) + leaf(x + 4, 30, 12, math.pi * .15) for x in range(40, 380, 44))
b += f'<rect x="92" y="50" width="216" height="170" fill="#15205a"{ol(2)}/>' + sky_bits(8, 14, 130, 100, 300, 58)
b += f'<path d="M92 196L130 182 170 192 210 176 250 188 308 178V220H92Z" fill="{WHT}"{ol(1.6)}/>' + dots_row(100, 300, 206, 9, 1.5, BLU, 1.5)
b += (f'<rect x="92" y="50" width="216" height="170" fill="none" stroke="{BLU}" stroke-width="9"/><rect x="196" y="50" width="8" height="170" fill="{BLU}"{ol(1)}/>'
      f'<rect x="92" y="130" width="216" height="7" fill="{BLU}"{ol(1)}/><rect x="87" y="45" width="226" height="180" fill="none"{ol(2)}/>')
b += dots_row(96, 306, 54, 9, 1.4, YEL)
for cx, d in ((60, 1), (340, -1)):
    b += (f'<path d="M{cx - 24 * d} 40Q{cx + 4 * d} 140 {cx - 14 * d} 232L{cx + 26 * d} 232Q{cx + 14 * d} 140 {cx + 30 * d} 40Z" fill="{RED}"{ol(1.8)}/>'
          + ''.join(f'<path d="M{cx + 2 * d + (y - 40) * .04 * d:.0f} {y}l4 -4 4 4 -4 4z" fill="{YEL}"/>' for y in range(56, 224, 16)))
b += f'<rect x="64" y="222" width="272" height="14" fill="#c98f4a"{ol(2)}/>' + dots_row(70, 334, 229, 10, 1.6, RED)
b += f'<path d="M110 222L106 200H134L130 222Z" fill="{OCH}"{ol(1.6)}/>' + dots_row(110, 132, 211, 6, 1.3, RED)
b += f'<path d="M120 200Q118 184 112 176M120 200Q124 182 132 172" fill="none"{ol(1.6)}/>' + flower(112, 172, 7) + flower(132, 168, 7, YEL, RED)
b += f'<path d="M188 222L196 208 204 208 212 222Z" fill="#8a5a2a"{ol(1.6)}/>' + star(200, 144, .05, glow=False)
SCENES.append(('На підвіконні', scene(2, b), 'Звізда на підставці на тлі вечірнього вікна. Ø 25–30 см: ціла звізда на A3. Світло з кімнати проходить крізь прорізи.'))

# 3. Біля кав'ярні
b = '<rect width="400" height="280" fill="#16205a"/>' + sky_bits(6, 10, 40)
b += f'<rect x="10" y="44" width="380" height="196" fill="{OCH}"{ol(2)}/>'
b += ''.join(f'<path d="M{x} 58l7 -7 7 7 -7 7z" fill="{RED}"{ol(1)}/>' for x in range(22, 380, 22)) + dots_row(18, 390, 70, 11, 1.6, GRN)
b += (f'<rect x="34" y="112" width="160" height="104" fill="{YEL}"{ol(2.4)}/><rect x="112" y="112" width="4" height="104" fill="{INK}"/>'
      f'<rect x="46" y="186" width="40" height="5" fill="#8a5a2a"{ol(1)}/><rect x="62" y="191" width="6" height="25" fill="#8a5a2a"{ol(1)}/>'
      f'<path d="M88 176h12v-6h-12z" fill="{WHT}"{ol(1)}/>')
b += ''.join(f'<path d="M{x} 92L{x + 20} 92L{x + 22} 110Q{x + 10} 116 {x - 2} 110Z" fill="{c}"{ol(1.4)}/>' for x, c in zip(range(30, 200, 20), [RED, YEL] * 5))
b += (f'<rect x="232" y="118" width="62" height="122" fill="{GRN}"{ol(2)}/><rect x="242" y="128" width="42" height="50" fill="{YEL}"{ol(1.4)}/>'
      f'<circle cx="284" cy="194" r="3" fill="{YEL}"{ol(1)}/>' + flower(263, 214, 9, RED, YEL))
b += (f'<rect x="216" y="80" width="150" height="28" rx="4" fill="{INK}"/><text x="291" y="99" text-anchor="middle" '
      f'font-family="IBM Plex Sans, Arial, sans-serif" font-size="14" font-weight="700" fill="{YEL}" letter-spacing="2">КАВ\'ЯРНЯ</text>'
      + fstar(226, 94, 4) + fstar(356, 94, 4))
b += f'<path d="M14 40Q200 64 386 40" fill="none"{ol(1.4)}/>'
b += ''.join(f'<circle cx="{x}" cy="{40 + 12 * (1 - ((x - 200) / 186) ** 2):.1f}" r="3.6" fill="{c}"{ol(1)}/>' for x, c in zip(range(22, 386, 22), [YEL, RED, GRN, BLU] * 5))
b += hill(242, WHT, 4) + dots_row(16, 390, 256, 10, 1.6, BLU)
b += f'<line x1="338" y1="246" x2="338" y2="160" stroke="#8a5a2a" stroke-width="4"/><path d="M326 248L350 248 338 236Z" fill="#8a5a2a"{ol(1.4)}/>' + star(338, 150, .032)
b += star(150, 150, .018, glow=False)
SCENES.append(('Біля кав\'ярні', scene(3, b), 'Велика звізда на стійці біля входу й менша у вітрині. Ø 60–80 см: чверті на A2. Для вулиці краще вирізати з фанери.'))

# 4. Хата на снігу
b = '<rect width="400" height="280" fill="#120f22"/>' + sky_bits(16, 26, 130)
b += f'<path d="M324 30A22 22 0 1 0 344 66A17 17 0 1 1 324 30Z" fill="{YEL}"{ol(1.6)}/>'
b += hill(196, '#dbe4f2', 14) + hill(222) + dots_row(10, 400, 240, 10, 1.8, BLU, 2) + dots_row(16, 400, 256, 12, 1.6, BLU, 2)
b += f'<rect x="100" y="156" width="150" height="66" fill="{WHT}"{ol(2)}/>'
b += f'<path d="M84 160Q170 92 266 160Z" fill="{OCH}"{ol(2)}/>' + ''.join(f'<line x1="{x}" y1="{158 - 54 * (1 - ((x - 175) / 90) ** 2):.0f}" x2="{x - 3}" y2="158" stroke="#8a5a2a" stroke-width="1.2"/>' for x in range(96, 258, 7))
b += f'<path d="M108 128Q175 92 242 128Q175 112 108 128Z" fill="{WHT}"{ol(1.4)}/>'
b += ''.join(f'<path d="M{x} 164l5 6 5 -6" fill="none" stroke="{RED}" stroke-width="2"/>' for x in range(104, 246, 10))
for wx in (116, 202):
    b += (f'<rect x="{wx}" y="176" width="30" height="24" fill="{YEL}"{ol(1.6)}/><rect x="{wx + 14}" y="176" width="2" height="24" fill="{INK}"/>'
          f'<rect x="{wx - 9}" y="176" width="9" height="24" fill="{BLU}"{ol(1.2)}/><rect x="{wx + 30}" y="176" width="9" height="24" fill="{BLU}"{ol(1.2)}/>')
b += f'<rect x="162" y="172" width="26" height="50" fill="#8a5a2a"{ol(1.6)}/>' + flower(175, 166, 5, RED, YEL)
for x0, x1 in ((20, 92), (258, 300)):
    b += ''.join(f'<line x1="{x}" y1="202" x2="{x}" y2="232" stroke="#8a5a2a" stroke-width="3"/>' for x in range(x0, x1 + 1, 12))
    b += f'<path d="M{x0} 212Q{(x0 + x1) / 2} 204 {x1} 212M{x0} 222Q{(x0 + x1) / 2} 214 {x1} 222" fill="none" stroke="#8a5a2a" stroke-width="3"/>'
b += kalyna(34, 236, .75, 1)
b += f'<line x1="336" y1="248" x2="336" y2="122" stroke="#8a5a2a" stroke-width="4"/>' + star(336, 112, .03)
SCENES.append(('Хата на снігу', scene(4, b), 'Звізда на жердині над тином, як на ходах звіздарів у селі. Велику звізду Ø 1–2,4 м вирізають з фанери, файли для ЧПК є на основному сайті.'))

# 5. На ялинці
b = '<rect width="400" height="280" fill="#16205a"/>' + sky_bits(14, 20, 120)
b += hill(236) + dots_row(10, 400, 250, 10, 1.8, BLU, 2)
b += f'<rect x="194" y="214" width="12" height="26" fill="#8a5a2a"{ol(1.6)}/>'
for i, (y, w) in enumerate(((92, 22), (116, 34), (140, 46), (164, 58), (188, 70), (212, 82))):
    b += f'<path d="M200 {y - 22}L{200 - w} {y}Q200 {y - 8} {200 + w} {y}Z" fill="{GRN}"{ol(1.8)}/>'
    b += ''.join(f'<circle cx="{200 + d * w * .55:.0f}" cy="{y - 6}" r="3.6" fill="{c}"{ol(1)}/>' for d, c in ((-1, [RED, YEL, BLU][i % 3]), (1, [YEL, RED, WHT][i % 3])))
b += star(200, 64, .024)
b += bird(92, 222, .9, 1) + bird(308, 222, .9, -1, YEL)
b += flower(46, 246, 8) + flower(354, 246, 8, YEL, RED)
SCENES.append(('На ялинці', scene(5, b), 'Звізда-верхівка для ялинки на площі чи вдома. Ø 15–20 см: ціла звізда на A4, з отвором для шнурка біля кінчика.'))

# 6. У вікні багатоповерхівки
b = '<rect width="400" height="280" fill="#120f22"/>' + sky_bits(10, 16, 40)
b += f'<rect x="50" y="44" width="300" height="240" fill="#d9a95a"{ol(2)}/>'
b += ''.join(f'<path d="M{x} 54l6 -6 6 6 -6 6z" fill="{RED}"{ol(1)}/>' for x in range(60, 344, 20))
for r in range(5):
    for c in range(5):
        x, y = 66 + c * 56, 70 + r * 44
        lit = (r, c) == (2, 2) or rnd.random() < .4
        b += f'<rect x="{x}" y="{y}" width="40" height="30" fill="{YEL if lit else "#16205a"}"{ol(1.6)}/>'
        b += f'<rect x="{x - 3}" y="{y + 30}" width="46" height="4" fill="{WHT}"{ol(1)}/>'
        if lit and (r, c) != (2, 2) and rnd.random() < .5:
            b += flower(x + 32, y + 24, 4.5, RED, YEL)
b += f'<line x1="200" y1="158" x2="200" y2="163" stroke="{INK}" stroke-width="1"/>' + star(200, 173, .0095, glow=False)
b += '<circle cx="200" cy="173" r="30" fill="url(#glow)"/>'
b += ''.join(flake(rnd.uniform(20, 380), rnd.uniform(20, 270), rnd.uniform(2.5, 4)) for _ in range(18))
SCENES.append(('У вікні багатоповерхівки', scene(6, b), 'Звізда на шнурку у вікні, видно з вулиці. Ø 30–40 см: ціла на A2 або половинами на A3.'))

scenes = ''.join(f'<figure class="scene"><svg viewBox="0 0 400 280" role="img" aria-label="{t}">{body}</svg>'
                 f'<figcaption><b>{t}</b><span>{cap}</span></figcaption></figure>' for t, body, cap in SCENES)

tpl = open(os.path.join(HERE, "konstruktor.html"), encoding="utf-8").read()
from i18n_en import EN   # англійська версія сторінки
body = tpl.replace("%%SCENES%%", scenes).replace("%%I18N_EN%%", json.dumps(EN, ensure_ascii=False, indent=0))
open(os.path.join(PROJ, "konstruktor.html"), "w", encoding="utf-8").write(body)
def wrap(head, doc):
    doc = doc.replace('<meta charset="utf-8">\n', "", 1)   # кодування має стояти на самому початку шапки
    return ('<!doctype html>\n<html lang="uk">\n<head>\n<meta charset="utf-8">\n' + head +
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>body{margin:0}img{max-width:100%}:root{padding-top:env(safe-area-inset-top,0px);'
            'padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n' + doc + '\n</html>\n')

# копія для GitHub Pages: поки звізди погоджують, сторінки немає в пошуку
page = wrap('<meta name="robots" content="noindex">\n', body)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
print("konstruktor", len(page) // 1024, "KB")

# копія для Netlify: відкрита для пошуку, з описом сторінки й даними про розробника
SITE_URL = "https://constructorzvizd.netlify.app"   # без скісної риски в кінці
AUTHOR, AUTHOR_LAT = "Вартан Маркар'ян", "Vartan Markarian"
SEO_TITLE = "Конструктор звізд — різдвяні звізди за полтавськими мотивами"
SEO_DESC = ("Онлайн-конструктор різдвяних звізд за мотивами полтавської різьби по дереву, майоліки, "
            "вишивки й писанок. 18 основ, кольори, прикраси, викрійки A4, A3 і A2.")
SEO_KEYS = ("конструктор звізд, різдвяна звізда, різдвяна зірка, викрійка звізди, викрійка зірки, "
            "полтавська різьба по дереву, полтавська майоліка, полтавська вишивка, писанка, "
            f"{AUTHOR}, {AUTHOR_LAT}, Christmas star builder, printable star template, Ukrainian folk star")
person = {"@type": "Person", "name": AUTHOR, "alternateName": AUTHOR_LAT}
ld = {"@context": "https://schema.org", "@type": "WebApplication",
      "name": "Конструктор звізд", "alternateName": "Star Builder",
      "description": ("Різдвяні звізди за мотивами полтавської різьби по дереву, майоліки й вікон будинку "
                      "губернського земства, дерев'яних церков, вишивки й писанок. Основу можна змінити: кількість "
                      "і форму променів, орнамент прорізів і кольори. Готову звізду можна роздрукувати викрійкою "
                      "на аркуші A4, A3 або A2."),
      "applicationCategory": "DesignApplication", "browserRequirements": "JavaScript",
      "inLanguage": ["uk", "en"], "isAccessibleForFree": True,
      "author": person, "creator": person, "copyrightHolder": person, "copyrightYear": 2026,
      "featureList": ["18 основ звізд за полтавськими мотивами", "кількість і форма променів, зокрема форма «Сливки»",
                      "орнамент прорізів і кольорові палітри", "другий шар і прикраси на кінчиках променів",
                      "викрійки PDF і SVG на A4, A3 і A2: цілою, половинами чи чвертями",
                      "українська й англійська версії"],
      "about": ["Різдвяна звізда", "Полтавська різьба по дереву", "Будинок Полтавського губернського земства",
                "Полтавська вишивка", "Писанка"]}
if SITE_URL: ld["url"] = SITE_URL + "/"
seo = (f'<meta name="description" content="{SEO_DESC}">\n'
       f'<meta name="keywords" content="{SEO_KEYS}">\n'
       f'<meta name="author" content="{AUTHOR} ({AUTHOR_LAT})">\n'
       f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Конструктор звізд">\n'
       f'<meta property="og:title" content="{SEO_TITLE}">\n<meta property="og:description" content="{SEO_DESC}">\n'
       f'<meta property="og:locale" content="uk_UA">\n<meta property="og:locale:alternate" content="en_US">\n'
       f'<meta property="og:image" content="{SITE_URL}/og-image.jpg">\n'   # netlify/og-image.jpg — знімок конструктора
       f'<meta property="og:image:type" content="image/jpeg">\n'
       f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
       f'<meta property="og:image:alt" content="Конструктор звізд: звізда «Розетка», галерея з 18 основ і налаштування променів">\n'
       f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{SITE_URL}/og-image.jpg">\n')
if SITE_URL: seo += f'<link rel="canonical" href="{SITE_URL}/">\n<meta property="og:url" content="{SITE_URL}/">\n'
seo += f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
seo += '<script data-goatcounter="https://constructorzvizd.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n'
NETLIFY = os.path.join(PROJ, "netlify")
os.makedirs(NETLIFY, exist_ok=True)
doc = (body.replace("<title>Конструктор звізд</title>", f"<title>{SEO_TITLE}</title>", 1)
           .replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "", 1)
           .replace("SHARE_URL = ''", f"SHARE_URL = '{SITE_URL}/'", 1)   # посилання на звізду веде на сайт
           .replace("const CNC_OFF = false", "const CNC_OFF = true", 1))
doc = re.sub(r"[ \t]*<!--cnc-->.*?<!--/cnc-->\n?", "", doc, flags=re.S)   # розділу для ЧПК на сайті немає
open(os.path.join(NETLIFY, "index.html"), "w", encoding="utf-8").write(wrap(seo, doc))
robots = "User-agent: *\nAllow: /\n"
if SITE_URL:
    robots += f"Sitemap: {SITE_URL}/sitemap.xml\n"
    open(os.path.join(NETLIFY, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'<url><loc>{SITE_URL}/</loc></url>\n</urlset>\n')
open(os.path.join(NETLIFY, "robots.txt"), "w", encoding="utf-8").write(robots)
print("netlify", os.path.getsize(os.path.join(NETLIFY, "index.html")) // 1024, "KB")
