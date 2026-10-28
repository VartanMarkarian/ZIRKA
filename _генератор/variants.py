import math
from stars import Star


def stair(levels):
    """Уступчастий промінь: рівні висоти (частки від западини) на рівних кроках уздовж променя."""
    n = len(levels) - 1
    pts = []
    for i in range(1, n + 1):
        t = i / (n + 1)
        pts += [(t, levels[i - 1] / (1 - t)), (t, levels[i] / (1 - t))]
    return pts


TOWER = [(0.42, 1.42), (0.62, 0.95)]   # промінь-вежа: стіни, шатро, шпиль

# Великі зірки Ø2400, ріжуться на 4 однакові чверті (N кратне 4, шви по западинах)
BIG_KW = dict(axle=30, r_clear=265, margin=32, seam_margin=50, split4=True)
BIG = [
    Star('v1', 'Рожа', 12, 1200, 560, profile=[], **BIG_KW, motifs={
        'long': [('dot', 270, 330, 30), ('drop', 355, 520, 95), 
                 ('rhombus', 565, 790, 130), ('lens', 830, 1010, 70)]}),
    Star('v2', 'Колосок', 16, 1200, 600, alt=930, profile=[], **BIG_KW, motifs={
        'long': [('lens', 285, 560, 80), ('drop', 600, 745, 70), ('drop', 775, 885, 60),
                 ('drop', 910, 990, 45)],
        'short': [('lens', 285, 560, 80), ('rhombus', 600, 760, 70)]}),
    Star('v3', 'Сонце', 20, 1200, 660, profile=[(0.5, 0.86)], **BIG_KW, motifs={
        'long': [('dot', 445, 505, 40), ('rhombus', 530, 670, 70),
                 ('lens', 700, 940, 60)]}),
    # мотиви українського модерну (будинок Полтавського земства) і народного різьблення
    Star('v4', 'Модерн', 12, 1200, 600, profile=[(0.32, 1.16), (0.33, 0.78)], **BIG_KW, motifs={
        'long': [('hexa', 285, 450, 80), ('dot', 475, 530, 24), ('trap', 610, 760, 120),
                 ('hexa', 810, 960, 50)]}),
    Star('v5', 'Крин', 12, 1200, 620, profile=[(0.38, 1.12)], **BIG_KW, motifs={
        'long': [('tulip', 290, 545, 120), ('dot', 575, 620, 22), ('tulip', 650, 930, 130),
                 ('dot', 965, 1015, 22)]}),
    Star('v6', 'Вихор', 12, 1200, 580, profile=[], **BIG_KW, motifs={
        'long': [('whirl:35:85', 330, 560, 34), ('tri', 610, 720, 100), ('triin', 745, 840, 70),
                 ('tri', 865, 950, 45)]}),
    # мотиви Полтавського краєзнавчого музею (колишнього будинку земства) та полтавських плахт
    Star('v7', 'Вежа', 12, 1200, 560, profile=TOWER, **BIG_KW, motifs={
        'long': [('hexa', 290, 470, 80), ('dot', 495, 545, 22), ('window', 595, 795, 120),
                 ('rhombus', 830, 930, 70)]}),
    Star('v8', 'Плахта', 12, 1200, 580, profile=stair([1, 0.8, 0.55, 0.3]), strict=True, **BIG_KW, motifs={
        'long': [('steprh', 290, 530, 95), ('steprh', 605, 810, 100),
                 ('rhombus', 840, 920, 50)]}),
]

# Передні зірки Ø1200 — цілі, з одного листа
SM_KW = dict(axle=30, margin=26, seam_margin=12, r_clear=92)
SMALL = [
    Star('s1', 'Іскра', 16, 600, 300, profile=[], **SM_KW, motifs={
        'long': [('dropin', 95, 275, 50), ('dot', 300, 345, 22)]}),
    Star('s2', 'Квітка', 10, 600, 320, profile=[(0.42, 1.14)], **SM_KW,
         motifs={'long': [('dropin', 100, 235, 40), ('rhombus', 270, 420, 70), ('dot', 450, 500, 25)]}),
    Star('s3', 'Сяйво', 24, 600, 330, alt=450, profile=[], **SM_KW,
         motifs={'long': [('lens', 100, 300, 40), ('dot', 335, 375, 20)],
                 'short': [('dot', 230, 280, 25)]}),
    Star('s4', 'Вихрова', 12, 600, 300, profile=[], **SM_KW, motifs={
        'long': [('whirl:8:50', 108, 285, 24), ('tri', 320, 410, 45), ('dot', 430, 470, 14)]}),
    Star('s5', 'Тюльпан', 10, 600, 330, profile=[(0.4, 1.1)], **SM_KW, motifs={
        'long': [('dropin', 100, 230, 40), ('tulip', 255, 480, 90)]}),
    Star('s6', 'Віконце', 12, 600, 300, profile=TOWER, **dict(SM_KW, seam_margin=14), motifs={
        'long': [('hexa', 105, 255, 30), ('window', 318, 425, 60)]}),
    Star('s7', 'Ружа', 12, 600, 320, profile=stair([1, 0.8, 0.55, 0.3]), strict=True, **SM_KW, motifs={
        'long': [('steprh', 100, 300, 50), ('steprh', 330, 465, 45)]}),
]

if __name__ == '__main__':
    for s in BIG + SMALL:
        st = s.stats()
        print(s.key, s.name, {k: round(v, 3) for k, v in st.items()})
        for w in s.warn:
            print('   !', w)
