"""6편 - 소주병은 왜 초록색일까"""
from kit import *

GREEN_G, CLEAR_G, BLUE_G = (46, 160, 92), (214, 232, 240), (156, 200, 232)
TABLE = (150, 104, 70)


def bottle(d, cam, x, y, s, col, a=255, label=None, lab_col=WHITE):
    """Base at (x, y). s = scale."""
    c = col + (a,)
    rr(d, cam, x - 13 * s, y - 330 * s, x + 13 * s, y - 300 * s, 5, fill=(220, 190, 60, a) if col == GREEN_G else (190, 196, 210, a))
    rr(d, cam, x - 17 * s, y - 302 * s, x + 17 * s, y - 220 * s, 6, fill=c)
    d.polygon([cxy(cam, x - 17 * s, y - 225 * s), cxy(cam, x + 17 * s, y - 225 * s), cxy(cam, x + 48 * s, y - 165 * s), cxy(cam, x - 48 * s, y - 165 * s)], fill=c)
    rr(d, cam, x - 48 * s, y - 170 * s, x + 48 * s, y, 16 * s, fill=c)
    rr(d, cam, x - 34 * s, y - 150 * s, x - 22 * s, y - 20 * s, 6, fill=(255, 255, 255, int(a * .35)))
    if label:
        rr(d, cam, x - 44 * s, y - 120 * s, x + 44 * s, y - 50 * s, 6, fill=(255, 255, 255, int(a * .9)))
        txt(d, cam, x, y - 86 * s, label, 22 * s, lab_col, a=a)


def table(d):
    rr(d, C0, 70, 1040, 1010, 1240, 0, fill=TABLE)
    rr(d, C0, 70, 1030, 1010, 1052, 0, fill=(176, 126, 88))


def sA(t, im, d):
    panel(d, (40, 52, 84)); table(d)
    k = eio((t - 1.2) / 0.9); cam = (lerp(1.0, 1.2, k), 540, lerp(760, 820, k))
    for i, x in enumerate((360, 540, 720)):
        bottle(d, cam, x, 1040, 1.5 if i == 1 else 1.25, GREEN_G)
    if 1.9 < t < 3.6:
        rings(d, cam, 540, 780, 170, t)
    if t >= 3.9:
        pill(d, C0, 540, 400, "원래부터 초록색?", 46, WHITE, INK, sc=kpop(t, 3.9))
    if t >= 4.9:
        badge(d, C0, 790, 400, 56, RED, "x", kpop(t, 4.9, .25))


def sB(t, im, d):
    panel(d, (52, 60, 88)); table(d)
    for x, col in ((330, CLEAR_G), (540, BLUE_G), (750, CLEAR_G)):
        bottle(d, C0, x, 1040, 1.3, col, a=200)
    pill(d, C0, 540, 400, "1994년 이전", 50, YEL, INK, sc=kpop(t, 6.2))


def sC(t, im, d):
    panel(d, (40, 52, 84)); table(d)
    k = ease((t - 13.3) / 0.6)
    for x in (300, 780):
        bottle(d, C0, x, 1040, 1.15, mix(CLEAR_G, GREEN_G, k), a=int(lerp(200, 255, k)))
    s = 1.55 * (0.6 + 0.4 * kpop(t, 11.1, .35))
    bottle(d, C0, 540, 1040, s, GREEN_G, label="그린", lab_col=GREEN_G)
    if t >= 11.4:
        for i in range(6):
            a = (t * 1.5 + i / 6) % 1
            ang = i * math.pi / 3 + t
            emo(im, 540 + math.cos(ang) * 230, 640 + math.sin(ang) * 150, 44 * (1 - a) + 10, "✨", a=1 - a)
    pill(d, C0, 540, 400, "1994년 ‘그린소주’", 46, GREEN, INK, sc=kpop(t, 11.2))
    if t >= 13.3:
        pill(d, C0, 540, 1150, "다른 회사도 초록색으로", 36, WHITE, INK, sc=kpop(t, 13.4))


def sD(t, im, d):
    panel(d, (36, 64, 70)); table(d)
    u = eio((t - 15.9) / 1.0)
    for i, x in enumerate((300, 460, 620, 780)):
        sh = [(1.1, 18), (1.25, -10), (1.0, 24), (1.18, -16)][i]
        s = lerp(sh[0], 1.15, u); w = lerp(sh[1], 0, u)
        bottle(d, C0, x + w, 1040, s, GREEN_G)
    pill(d, C0, 540, 400, "2009년 공용병 협약", 46, YEL, INK, sc=kpop(t, 15.8))
    if t >= 18.0:
        emo(im, 540, 560, 120 * kpop(t, 18.0, .3), "♻️", rot=-t * 60)


def sE(t, im, d):
    panel(d, (36, 64, 70))
    emo(im, 540, 560, 210, "♻️", rot=-t * 40)
    k = kpop(t, 20.3, .35)
    if k > 0:
        txt(d, C0, 540, 860, "10번+", 150 * k, YEL)
        txt(d, C0, 540, 990, "한 병을 씻어서 다시", 44, WHITE, a=255 * ease((t - 20.7) / .3))


def sF(t, im, d):
    panel(d, (40, 52, 84)); table(d)
    k = eio((t - 23.0) / 1.4); cam = (lerp(1.2, 1.0, k), 540, lerp(820, 760, k))
    for i, x in enumerate((360, 540, 720)):
        bottle(d, cam, x, 1040, 1.5 if i == 1 else 1.25, GREEN_G)
    if t > 23.5:
        rings(d, cam, 540, 780, 170, t)


T = ((("소주병은 왜 ", W_), ("초록색", Y_), ("일까?", W_)))
HOOK2 = [[[("소주병은", W_)], [("왜", W_)]], [[("초록색", Y_), ("일까?", W_)]]]
CAPS = [
    (3.6, 6.0, [("원래부터 초록색?", W_)], [("아닙니다", Y_)]),
    (6.0, 11.0, [("90년대 초까지는", W_)], [("투명·하늘색 병", Y_), ("이었어요", W_)]),
    (11.0, 13.3, [("1994년 초록 병의", W_)], [("‘그린소주’", Y_), ("가 대박", W_)]),
    (13.3, 15.5, [("다른 회사들도", W_)], [("초록색", Y_), ("으로 따라갔죠", W_)]),
    (15.5, 18.0, [("2009년엔", W_)], [("병 모양까지 통일", Y_)]),
    (18.0, 20.0, [("회사 상관없이", W_)], [("씻어서 다시 써요", Y_)]),
    (20.0, 23.0, [("초록 병 하나를", W_)], [("10번 넘게", Y_), (" 재사용", W_)]),
    (23.0, 25.0, [("다음 술자리에서", W_)], [("이야기해 보세요", Y_)]),
    (25.0, 27.0, [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)]),
]
EP = Episode(6, T, HOOK_KNOW, HOOK2, [(0, sA), (6.0, sB), (11.0, sC), (15.5, sD), (20.0, sE), (23.0, sF)], CAPS,
             events=[("ding", 2.3, 1568), ("pop", 3.9, 900), ("no", 4.9), ("pop", 6.2, 800), ("thud", 11.1, .4), ("ding", 11.4, 1760),
                     ("ding", 13.4, 1175), ("pop", 15.8, 900), ("clank", 16.9, .18), ("pop", 18.0, 1000), ("yes", 20.3)])
if __name__ == "__main__":
    EP.main()
