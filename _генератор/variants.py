import math
from stars import Star

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
]

if __name__ == '__main__':
    for s in BIG + SMALL:
        st = s.stats()
        print(s.key, s.name, {k: round(v, 3) for k, v in st.items()})
        for w in s.warn:
            print('   !', w)
