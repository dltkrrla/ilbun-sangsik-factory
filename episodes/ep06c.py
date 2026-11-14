"""6편 내레이션판 - 대본 길이에 맞춰 장면 시간을 계산"""
import os, sys, json
from kit import *
import ep06 as o
from ep06b import sHook, remap, T, Q

VO = os.path.join(HERE, "vo", "ep06")
LINES = [  # (spoken text, caption l1, caption l2, scene key)
    ("소주병은 왜 전부 초록색일까요?", None, None, "hook"),
    ("사실 원래는, 투명한 병이었어요.", [("사실 원래는", W_)], [("투명한 병", Y_), ("이었어요", W_)], "B"),
    ("천구백구십사 년, 초록 병의 그린소주가 대박이 났고,", [("1994년 초록 병의", W_)], [("‘그린소주’", Y_), ("가 대박", W_)], "C"),
    ("다른 회사들도 초록색으로 따라갔죠.", [("다른 회사들도", W_)], [("초록색", Y_), ("으로 따라갔죠", W_)], "C"),
    ("이천구 년에는 병 모양까지 똑같이 맞췄어요.", [("2009년엔", W_)], [("병 모양까지 똑같이", Y_)], "D"),
    ("어느 회사 병이든 씻어서 다시 쓰려고요.", [("어느 회사 병이든", W_)], [("씻어서 다시 써요", Y_)], "D"),
    ("초록 병 하나를 열 번 넘게 재사용한대요.", [("초록 병 하나를", W_)], [("10번 넘게", Y_), (" 재사용", W_)], "E"),
    ("다음 술자리에서 이야기해 보세요.", [("다음 술자리에서", W_)], [("이야기해 보세요", Y_)], "F"),
    ("알고 있었다면, 댓글로 알려 주세요!", [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)], "F"),
]
SPEED, GAP = 1.12, 0.18


def build_vo():
    os.makedirs(VO, exist_ok=True)
    meta = os.path.join(VO, "meta.json")
    if os.path.exists(meta):
        return json.load(open(meta))
    import tts_st
    durs = []
    for i, (txt, *_r) in enumerate(LINES):
        dd, _ = tts_st.say(txt, os.path.join(VO, f"l{i:02d}.wav"), 1.05 if i == 8 else SPEED)
        durs.append(dd)
    json.dump(durs, open(meta, "w")); return durs


def trim(durs):
    """measured speech length without trailing silence"""
    import soundfile as sf, numpy as np
    out = []
    for i in range(len(durs)):
        x, sr = sf.read(os.path.join(VO, f"l{i:02d}.wav")); x = x if x.ndim == 1 else x.mean(1)
        idx = np.where(np.abs(x) > 0.02)[0]
        out.append((idx[0] / sr, idx[-1] / sr) if len(idx) else (0, durs[i]))
    return out


durs = build_vo(); spans = trim(durs)
starts, t = [], 0.15
for (a, e) in spans:
    starts.append(t - a); t = t - a + e + GAP
starts[1] = max(starts[1], 2.2)
for i in range(2, len(starts)):
    starts[i] = max(starts[i], starts[i - 1] + spans[i - 1][1] - spans[i - 1][0] + GAP + spans[i - 1][0] - spans[i][0] * 0)
DUR = round(starts[-1] + spans[-1][1] + 0.9, 2)
seg = [max(0.0, s_ + spans[i][0] - 0.05) for i, s_ in enumerate(starts)]  # caption/scene boundaries = speech onsets
seg[0] = 0.0
QEND = seg[1]
CAPS = [(seg[i], seg[i + 1] if i + 1 < len(seg) else DUR, l1, l2) for i, (_, l1, l2, _) in enumerate(LINES) if l1]
first = {}
for i, (*_x, key) in enumerate(LINES):
    first.setdefault(key, seg[i])
SC_ = [(0, sHook), (first["B"], remap(o.sB, first["B"], 6.0)), (first["C"], remap(o.sC, first["C"], 11.0)),
       (first["D"], remap(o.sD, first["D"], 15.5)), (first["E"], remap(o.sE, first["E"], 20.0)), (first["F"], remap(o.sF, first["F"], 23.0))]
EV = [("thud", first["C"] + .1, .4), ("ding", first["C"] + .4, 1760), ("clank", first["D"] + 1.4, .18), ("yes", first["E"] + .3)]
EP = Episode(6, T, None, None, SC_, CAPS, events=EV, dur=DUR, qhook=(Q[0], (585, 735), Q[2]), qend=QEND, cap_y=(1186, 1290))
EP.fit = 0.82; EP.end_y = 1100
CLIPS = [(starts[i], os.path.join(VO, f"l{i:02d}.wav")) for i in range(len(LINES))]

if __name__ == "__main__":
    print("dur", DUR, "seg", [round(x, 2) for x in seg])
    if sys.argv[1] == "stills":
        EP.main()
    elif sys.argv[1] == "render":
        EP.render_voice(sys.argv[2], CLIPS)
