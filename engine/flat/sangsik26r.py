"""26편 실사판: AI 실사 영상 위에 얹을 투명 오버레이(글자·로고·표시) + 소리.
배경 영상은 Higgsfield 샌드박스에서 합성한다. 시간은 sangsik26의 OB(원래 애니메이션 시간)/NB(내레이션 시간)를 그대로 쓴다.
usage: python3 sangsik26r.py overlay out.webm | audio out.wav | stills name t1 t2 ... (t = 내레이션 시간)"""
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sangsik26 as s
from sangsik26 import *

RED = (235, 70, 50)


def grad_layer():
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = np.zeros((H, W), np.uint8)
    for y in range(H):
        top = max(0.0, 1 - y / 330) * 150
        bot = max(0.0, (y - 1180) / (H - 1180)) ** 1.2 * 200
        a[y, :] = int(min(230, top + bot))
    g.putalpha(Image.fromarray(a)); return g


GRAD = grad_layer()
TIE_MASK = Image.new("L", (W, 1000), 0)
ImageDraw.Draw(TIE_MASK).rounded_rectangle((24, 0, W - 25, 999), 56, fill=255)


def guess(im, t, x, y, label, t_in, t_x):
    if t < t_in:
        return
    put(im, box_img(label, 64, WHITE, INK, pad=40), x, y, ease((t - t_in) / 0.12), 0.7 + 0.3 * back((t - t_in) / 0.25))
    if t >= t_x:
        L = Image.new("RGBA", (180, 180), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((10, 10, 170, 170), fill=RED + (255,), outline=(255, 255, 255, 255), width=10)
        d.line((58, 58, 122, 122), fill=(255, 255, 255, 255), width=22); d.line((122, 58, 58, 122), fill=(255, 255, 255, 255), width=22)
        put(im, L, x + 150, y - 60, 1.0, 0.45 + 0.55 * back((t - t_x) / 0.22))


def ring(im, t, x, y, t0):
    d = ImageDraw.Draw(im)
    for ph in (0.0, 0.5):
        p = ((t - t0) * 1.1 + ph) % 1; R = 40 + 60 * p
        d.ellipse((x - R, y - R, x + R, y + R), outline=YEL + (int(255 * (1 - p) ** 1.3),), width=8)


def overlay(t):  # t = original animation time (OB)
    im = GRAD.copy()
    if 10.0 <= t < 15.5:  # 묶는 법: 실사 손 영상 + 오른쪽 위 작은 그림으로 순서 확인
        k = ease((t - 10.0) / 0.25) * (1 - ease((t - 15.25) / 0.25))
        ins = scene_tie(t).reduce(SC).crop((70, 200, 1010, 980)).resize((340, 282), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", ins.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ins.width - 1, ins.height - 1), 28, fill=int(255 * k)); ins.putalpha(m)
        sh = Image.new("RGBA", (ins.width + 40, ins.height + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 24, ins.width + 20, ins.height + 24), 28, fill=(0, 0, 0, int(120 * k)))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (W - 40 - ins.width - 20, 250 - 20))
        im.alpha_composite(ins, (W - 40 - ins.width, 250))
        lt = t - 10.0
        msg = "① 같은 쪽 맨 위 구멍 → 작은 고리" if lt < 2.2 else ("② 반대쪽 고리에 통과" if lt < 3.7 else "③ 당기고 평소처럼 묶기")
        t_in = 10.1 if lt < 2.2 else (12.2 if lt < 3.7 else 13.7)
        put(im, box_img(msg, 50, YEL, INK, pad=34), 540, 1262, k, 0.7 + 0.3 * back((t - t_in) / 0.25))
    signature2(im, t)
    kinetic(im, t, 0.0, 1.5, [[[("이거", WHITE)]], [[("알고", YEL)], [("있었나요?", YEL)]]], (690, 850), 128, stagger=0.17, slam=0.9)
    kinetic(im, t, 1.4, 3.6, [[[("운동화", WHITE)], [("맨", WHITE)], [("위에", WHITE)]], [[("남는", WHITE)], [("구멍", YEL), ("?", WHITE)]]], (1388, 1500), 84, stagger=0.12, slam=0.5)
    if 3.6 <= t < 6.6:
        guess(im, t, 330, 560, "통풍?", 3.75, 4.6); guess(im, t, 700, 760, "장식?", 4.95, 5.8)
    if 6.6 <= t < 8.6:
        put(im, box_img("뒤꿈치 들썩!", 60, RED, WHITE, pad=36), 540, 560, ease((t - 6.8) / 0.12), 0.7 + 0.3 * back((t - 6.8) / 0.25))
    if 8.6 <= t < 10.0:
        put(im, box_img("물집 주의", 60, RED, WHITE, pad=36), 540, 560, ease((t - 8.75) / 0.12), 0.7 + 0.3 * back((t - 8.75) / 0.25))
    if 15.5 <= t < 18.5:
        put(im, box_img("뒤꿈치 고정 ✓", 60, YEL, INK, pad=36), 540, 560, ease((t - 15.8) / 0.12), 0.7 + 0.3 * back((t - 15.8) / 0.25))
    if 18.5 <= t < 21.5:
        put(im, box_img("힐락 (Heel Lock)", 76, YEL, INK, pad=44), 540, 600, ease((t - 18.9) / 0.12), 0.6 + 0.4 * back((t - 18.9) / 0.3))
    if 21.5 <= t < 24.0:
        put(im, box_img("물집 예방", 70, WHITE, INK, pad=40), 540, 600, ease((t - 21.7) / 0.12), 0.7 + 0.3 * back((t - 21.7) / 0.25))
    if t >= 26.2:
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1252, 1.0, 0.6 + 0.4 * back((t - 26.2) / 0.28))
    for t0, t1, l1, l2 in CAPS[2:]:
        if t0 <= t < t1:
            a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if t1 < DUR else 1
            for i, (segs, cy) in enumerate(((l1, 1388), (l2, 1500))):
                lt = t - t0 - i * 0.13
                if lt >= 0:
                    put(im, line_img(tuple(segs)), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
    return im


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        ims = []
        for v in sys.argv[3:]:
            bg = Image.new("RGBA", (W, H), (120, 110, 95, 255)); bg.alpha_composite(overlay(warp(float(v))))
            ims.append(bg.convert("RGB").resize((360, 640), Image.LANCZOS))
        st = Image.new("RGB", (360 * len(ims), 640))
        for i, x in enumerate(ims):
            st.paste(x, (i * 360, 0))
        st.save(f"{OUT}/{sys.argv[2]}.jpg", quality=88)
    elif mode == "audio":
        out = sys.argv[2]; sfx(f"{OUT}/s26r_sfx.wav"); fo = DUR2 - 0.8
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", f"{OUT}/music/theme.wav", "-i", f"{OUT}/s26r_sfx.wav",
                        "-filter_complex", f"[0:a]atrim=0:{DUR2},volume=-17dB,afade=t=in:d=0.05,afade=t=out:st={fo}:d=0.8[m];[m][1:a]amix=inputs=2:normalize=0[a]",
                        "-map", "[a]", "-ar", "44100", "-ac", "2", "-t", str(DUR2), out], check=True)
        print("ok", out, DUR2)
    else:
        out = sys.argv[2]; tmp = out + ".part.webm"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-deadline", "realtime", "-cpu-used", "8",
                              "-row-mt", "1", "-auto-alt-ref", "0", tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR2 * FPS)):
            p.stdin.write(overlay(warp(i / FPS)).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, out); print("ok", out)
