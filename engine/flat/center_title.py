"""첫 화면 가운데 큰 제목 (엘리베이터 거울 20편 방식, 사용자 결정 2026-11-24).

"한국인 99%가 모르는 / 도어락 숨은 기능"처럼 두 줄 제목을 0초부터 화면 가운데 크게 띄운다.
- 흰 글자 + 강조 단어 노랑, 두꺼운 검은 테두리 (line_img)
- 단어마다 '팡' (크게 → 제자리), 노랑 단어는 살짝 숨쉬듯 커졌다 작아짐
- 첫 문장 나레이션이 끝나면(t_out) 사라지고 아래 자막으로 넘어간다
- 위쪽 빨간 태그·?? 스티커는 쓰지 않는다 (11/21 결정 유지)

사용:
    from center_title import center_title
    ROWS = [[[("한국인", W)], [("99%가", Y)], [("모르는", W)]],
            [[("도어락", W)], [("숨은 기능", Y)]]]
    center_title(im, t, ROWS, t_out=NB[1], hits=[0.10, 0.40, 0.70, 1.05, 1.35])
"""
import math
from PIL import Image, ImageDraw
from sangsik2 import F, YEL, ease, line_img, put

YS = (600, 745)     # 마스코트판(전체 화면) 기준 — 물건 윗부분, 릴스 버튼·캡션 자리(B5) 밖
SIZE = 116


def _layout(rows, size, ys):
    f = F(size); tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); out = []
    for words, cy in zip(rows, ys):
        ws = [sum(tmp.textlength(s, font=f) for s, _ in w) for w in words]
        sp = size * 0.24; total = sum(ws) + sp * (len(ws) - 1)
        sc = min(1.0, 1000 / total)                     # 화면 폭(양옆 40px) 안에 맞춤
        x = 540 - total * sc / 2
        for w, ww in zip(words, ws):
            out.append((w, x + ww * sc / 2, cy, sc)); x += (ww + sp) * sc
    return out


def center_title(im, t, rows, t_in=0.0, t_out=2.4, hits=None, size=SIZE, ys=YS):
    if not (t_in <= t < t_out):
        return
    items = _layout(rows, size, ys)
    if hits is None:
        hits = [t_in + 0.08 + 0.2 * i for i in range(len(items))]
    a_out = 1 - ease((t - (t_out - 0.15)) / 0.15)
    for (w, cx, cy, sc0), h in zip(items, hits):
        lt = t - h
        if lt < 0:
            continue
        sc = sc0 * (1 + 0.75 * (1 - ease(lt / 0.17)))   # 팡
        if any(c == YEL for _, c in w):
            sc *= 1 + 0.04 * math.sin(t * 9)
        put(im, line_img(tuple(w), size), cx, cy, ease(lt / 0.07) * a_out, sc)
