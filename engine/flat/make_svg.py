"""Generic low-top running sneaker, flat-vector illustration with gradients. python3 make_svg.py variant out.svg
variants: normal | lock | xray_shoe | foot"""
import sys
V = sys.argv[1]; OUTF = sys.argv[2]
UPPER = ("M 142,474 C 118,424 116,352 148,306 C 163,285 190,280 216,291 C 262,312 300,334 345,337 "
         "C 371,338 386,322 396,296 C 406,268 422,248 453,246 C 481,244 501,258 503,281 C 504,293 499,301 493,306 "
         "C 602,350 722,384 842,404 C 932,416 1012,424 1052,452 C 1074,470 1080,496 1076,513 L 1000,506 C 700,496 300,481 142,474 Z")
MID = ("M 134,470 C 300,478 700,500 1004,498 C 1050,497 1080,505 1080,519 C 1080,541 1064,557 1042,567 "
       "C 902,589 502,593 166,589 C 141,588 124,571 122,541 C 120,506 124,478 134,470 Z")
OUTS = ("M 166,588 C 502,592 902,588 1042,566 C 1054,561 1062,556 1067,552 L 1072,566 C 1060,579 1048,584 1032,588 "
        "C 902,607 502,611 170,607 C 151,606 140,599 138,590 Z")
HEELC = "M 142,474 C 118,424 116,352 148,306 C 163,285 190,280 216,291 C 242,340 268,418 272,478 Z"
COLLAR_IN = "M 172,298 C 202,292 262,320 345,331 C 369,331 382,318 390,300 C 384,322 366,340 338,341 C 282,340 224,322 172,298 Z"
TONGUE = "M 404,302 C 409,268 425,247 453,245 C 481,243 502,257 504,281 C 505,293 500,301 494,306 Z"
EYESTAY = ("M 486,300 C 602,346 722,384 846,410 C 852,426 848,440 838,444 C 722,420 602,388 480,346 "
           "C 470,330 474,312 486,300 Z")
TOEB = "M 896,503 C 898,456 948,430 1004,436 C 1044,442 1072,474 1076,513 L 1000,506 Z"
SADDLE = "M 548,346 C 540,398 524,446 506,489 L 742,496 C 748,456 754,430 768,402 C 700,384 620,366 548,346 Z"
PULL = "M 146,312 C 132,284 138,252 160,250 C 176,249 184,266 180,292 Z"
# eyelets along the eyestay (top extra one = HOLE)
import math
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0], u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1])
LP = ((488, 318), (602, 362), (722, 398), (836, 424))
EYES = [bez(*LP, t) for t in (0.12, 0.28, 0.44, 0.60, 0.76, 0.92)]
HOLE = (446, 314)


def lace_seg(a, b, w=13):
    return (f'<path d="M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}" stroke="#9AA3B8" stroke-width="{w+6}" stroke-linecap="round"/>'
            f'<path d="M {a[0]:.1f},{a[1]:.1f} L {b[0]:.1f},{b[1]:.1f}" stroke="#FFFFFF" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M {a[0]+2:.1f},{a[1]-3:.1f} L {b[0]+2:.1f},{b[1]-3:.1f}" stroke="#FFFFFF" stroke-opacity=".0" stroke-width="3"/>')


def lace_path(d, w=13, col="#FFFFFF", edge="#9AA3B8"):
    return (f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{w+6}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def eyelet(p):
    x, y = p
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="11" ry="10" fill="url(#metal)" stroke="#1E2440" stroke-width="2"/>'
            f'<ellipse cx="{x:.1f}" cy="{y+0.5:.1f}" rx="5.2" ry="4.6" fill="#141826"/>')


DEFS = '''<defs>
 <linearGradient id="mesh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7F9FC"/><stop offset=".7" stop-color="#E7EBF3"/><stop offset="1" stop-color="#C9D0DE"/></linearGradient>
 <linearGradient id="navy" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#34539E"/><stop offset="1" stop-color="#1F3270"/></linearGradient>
 <linearGradient id="navy2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3F64BD"/><stop offset="1" stop-color="#28428C"/></linearGradient>
 <linearGradient id="foam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#F3F4F7"/><stop offset="1" stop-color="#D8DCE6"/></linearGradient>
 <linearGradient id="rub" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3F52"/><stop offset="1" stop-color="#22263A"/></linearGradient>
 <linearGradient id="ao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F2A4A" stop-opacity="0"/><stop offset="1" stop-color="#1F2A4A" stop-opacity=".28"/></linearGradient>
 <linearGradient id="yel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD84D"/><stop offset="1" stop-color="#F2B800"/></linearGradient>
 <radialGradient id="metal" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#C3C8D4"/><stop offset="1" stop-color="#8A91A3"/></radialGradient>
 <linearGradient id="skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD9BC"/><stop offset="1" stop-color="#F2B894"/></linearGradient>
 <pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="4.5" cy="4.5" r="1.6" fill="#AEB7CB" fill-opacity=".55"/></pattern>
 <clipPath id="cu"><path d="''' + UPPER + '''"/></clipPath>
 <clipPath id="cm"><path d="''' + MID + '''"/></clipPath>
 <filter id="blur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>'''

OL = 'stroke="#1E2440" stroke-width="3.2" stroke-linejoin="round"'


def shoe(alpha_upper=1.0, lock=False, laces=True, base=True, upper=True):
    g = []
    if not upper:
        g.append('<ellipse cx="610" cy="606" rx="470" ry="18" fill="#1E2440" fill-opacity=".28" filter="url(#blur)"/>')
        g.append(f'<path d="{OUTS}" fill="url(#rub)" {OL}/>')
        g.append(f'<path d="{MID}" fill="url(#foam)" {OL}/>')
        g.append('<path d="M 150,540 C 400,548 700,552 1030,534" fill="none" stroke="#C9CFDC" stroke-width="5" stroke-linecap="round"/>')
        return "\n".join(g)
    if base:
        g.append('<ellipse cx="610" cy="606" rx="470" ry="18" fill="#1E2440" fill-opacity=".28" filter="url(#blur)"/>')
        g.append(f'<path d="{OUTS}" fill="url(#rub)" {OL}/>')
    for x in (range(200, 1010, 30) if base else []):       # tread marks on the outsole edge
        y = 592 + 0.000012 * (x - 600) ** 2 - (0.03 * (x - 900) if x > 900 else 0)
        g.append(f'<path d="M {x},{y:.1f} l 0,9" stroke="#5A6075" stroke-width="3" stroke-linecap="round"/>')
    ua = f' fill-opacity="{alpha_upper}"' if alpha_upper < 1 else ""
    g.append(f'<path d="{UPPER}" fill="url(#mesh)"{ua} {OL}/>')
    if alpha_upper >= 1:
        g.append(f'<g clip-path="url(#cu)"><rect x="100" y="230" width="1000" height="300" fill="url(#dots)"/>'
                 f'<rect x="100" y="430" width="1000" height="80" fill="url(#ao)"/></g>')
    g.append(f'<path d="{COLLAR_IN}" fill="#2C3248" fill-opacity="{0.95 if alpha_upper >= 1 else 0.3}"/>')
    g.append(f'<path d="{PULL}" fill="url(#yel)" {OL}/>')
    g.append(f'<path d="{HEELC}" fill="url(#navy)"' + (f' fill-opacity="{alpha_upper+0.2}"' if alpha_upper < 1 else "") + f' {OL}/>')
    g.append('<path d="M 214,306 C 238,352 258,420 262,470" fill="none" stroke="#8FA6E0" stroke-width="2.4" stroke-dasharray="7 6"/>')
    g.append(f'<path d="{SADDLE}" fill="#D9E2F5"' + (f' fill-opacity="{alpha_upper+0.2}"' if alpha_upper < 1 else "") + f' {OL}/>')
    g.append('<path d="M 560,360 C 552,404 540,446 526,486 M 752,494 C 756,460 762,436 772,412" fill="none" stroke="#8FA6E0" stroke-width="2.4" stroke-dasharray="7 6"/>')
    g.append(f'<path d="{TOEB}" fill="url(#navy)"' + (f' fill-opacity="{alpha_upper+0.2}"' if alpha_upper < 1 else "") + f' {OL}/>')
    g.append('<path d="M 910,500 C 916,464 952,446 1000,450" fill="none" stroke="#8FA6E0" stroke-width="2.4" stroke-dasharray="7 6"/>')
    if laces:
        g.append(f'<path d="{TONGUE}" fill="url(#navy2)" {OL}/>')
        g.append('<rect x="438" y="262" width="34" height="16" rx="4" fill="url(#yel)" transform="rotate(-8 455 270)"/>')
        g.append(f'<path d="{EYESTAY}" fill="url(#navy)" {OL}/>')
        g.append('<path d="M 492,330 C 604,370 722,404 834,430" fill="none" stroke="#8FA6E0" stroke-width="2.4" stroke-dasharray="7 6"/>')
    if base:
        g.append(f'<path d="{MID}" fill="url(#foam)" {OL}/>')
    if base: g.append('<path d="M 150,540 C 400,548 700,552 1030,534" fill="none" stroke="#C9CFDC" stroke-width="5" stroke-linecap="round"/>')
    if base: g.append('<path d="M 160,500 C 260,508 330,520 380,546" fill="none" stroke="#E2E6EE" stroke-width="4" stroke-linecap="round"/>')
    if base: g.append('<path d="M 150,488 C 400,494 700,512 1000,512" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-opacity=".9"/>')
    if laces:
        for i in range(len(EYES) - 1):        # crisscross segments visible over the tongue edge
            a = EYES[i]; b = (EYES[i][0] + 34, EYES[i][1] - 40)
            g.append(lace_seg(a, b))
        for p in EYES:
            g.append(eyelet(p))
        g.append(eyelet(HOLE))
        bx, by = EYES[0][0] + 26, EYES[0][1] - 36     # bow
        g.append(lace_path(f"M {EYES[0][0]:.0f},{EYES[0][1]:.0f} L {bx:.0f},{by:.0f}", 11))
        g.append(lace_path(f"M {bx},{by} C {bx-36},{by-30} {bx-56},{by-4} {bx},{by}", 11))
        g.append(lace_path(f"M {bx},{by} C {bx+28},{by-42} {bx+58},{by-14} {bx},{by}", 11))
        g.append(lace_path(f"M {bx},{by} C {bx+2},{by+22} {bx+14},{by+40} {bx+30},{by+62}", 11))
        g.append(lace_path(f"M {bx},{by} C {bx+12},{by+16} {bx+34},{by+30} {bx+56},{by+44}", 11))
        g.append(f'<circle cx="{bx}" cy="{by}" r="7.5" fill="#FFFFFF" stroke="#9AA3B8" stroke-width="3"/>')
        if lock:
            ax, ay = EYES[0]; hx, hy = HOLE
            g.append(lace_path(f"M {ax:.0f},{ay:.0f} C {ax-6},{ay+60} {hx-44},{hy+64} {hx},{hy}", 13, "#FFD23F", "#B88A00"))
            g.append(eyelet(HOLE))
    return "\n".join(g)


FOOT = ("M 214,30 C 204,120 224,220 248,290 C 258,330 252,366 238,392 C 220,424 212,458 220,484 "
        "C 230,502 262,504 304,502 C 520,500 700,498 820,500 C 860,504 900,506 960,503 "
        "C 1000,505 1034,504 1048,494 C 1060,482 1058,456 1044,440 C 1024,428 996,418 968,414 "
        "C 930,408 880,406 840,402 C 760,388 660,362 590,344 C 510,324 430,304 394,268 "
        "C 378,210 370,120 366,30 Z")
TOES = [  # nearer toes drawn on top: (outline path, nail path)
    ("M 930,438 C 950,432 990,436 1016,450 C 1034,460 1040,478 1034,494 C 1026,508 1000,512 970,510 C 950,508 936,498 930,486 C 922,474 922,450 930,438 Z",
     "M 1004,448 C 1018,450 1030,460 1032,470 C 1022,470 1010,464 1004,448 Z"),
    ("M 912,458 C 930,450 962,454 984,466 C 1000,476 1004,492 996,502 C 986,512 962,512 944,510 C 926,506 914,496 912,484 C 905,476 905,464 912,458 Z",
     "M 974,466 C 986,468 996,476 997,484 C 988,484 979,478 974,466 Z"),
]
TOE_LINES = []
NAILS = []


def foot():
    g = ['<defs><linearGradient id="skinv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6C9A6"/><stop offset=".55" stop-color="#EDB48D"/><stop offset="1" stop-color="#D99872"/></linearGradient>'
         '<linearGradient id="skinh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C98060" stop-opacity=".45"/><stop offset=".18" stop-color="#C98060" stop-opacity="0"/><stop offset=".85" stop-color="#C98060" stop-opacity="0"/><stop offset="1" stop-color="#B8704E" stop-opacity=".35"/></linearGradient>'
         '<radialGradient id="mall" cx=".45" cy=".4" r=".6"><stop offset="0" stop-color="#FFE0C8" stop-opacity=".9"/><stop offset="1" stop-color="#E8A985" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="heelg" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#FFD9BE" stop-opacity=".7"/><stop offset="1" stop-color="#E0A07C" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="cf"><path d="{FOOT}"/></clipPath></defs>']
    g.append(f'<path d="{FOOT}" fill="url(#skinv)"/>')
    g.append(f'<g clip-path="url(#cf)"><rect x="200" y="20" width="900" height="500" fill="url(#skinh)"/>'
             '<ellipse cx="312" cy="296" rx="36" ry="38" fill="url(#mall)"/>'
             '<path d="M 284,318 C 296,342 324,344 342,328" fill="none" stroke="#C98863" stroke-width="2.4" stroke-opacity=".6"/>'
             '<ellipse cx="262" cy="452" rx="58" ry="46" fill="url(#heelg)"/>'
             '<path d="M 252,120 C 252,200 258,260 266,300" fill="none" stroke="#FFE3CF" stroke-width="7" stroke-opacity=".55" stroke-linecap="round"/>'
             '<path d="M 300,500 C 500,486 760,486 960,494" fill="none" stroke="#B9785A" stroke-width="10" stroke-opacity=".35"/>'
             ''
             '<ellipse cx="860" cy="492" rx="70" ry="14" fill="#C98060" fill-opacity=".22"/><ellipse cx="268" cy="490" rx="50" ry="12" fill="#C98060" fill-opacity=".22"/></g>')
    g.append(f'<path d="{FOOT}" fill="none" stroke="#A8664A" stroke-width="3" stroke-linejoin="round"/>')
    g.append('<path d="M 1032,454 C 1046,460 1052,474 1048,486" fill="none" stroke="#FBE3D6" stroke-width="8" stroke-linecap="round" stroke-opacity=".9"/>')
    for body_, nail in TOES:
        g.append(f'<path d="{body_}" fill="url(#skinv)" stroke="#A8664A" stroke-width="2.6" stroke-linejoin="round"/>')
        g.append(f'<path d="{nail}" fill="#FCE6DA" stroke="#C98863" stroke-width="1.8"/>')
    g.append('<path d="M 600,358 C 700,384 800,402 900,412 M 640,352 C 740,374 840,392 930,404" fill="none" stroke="#FFE3CF" stroke-width="4" stroke-opacity=".35" stroke-linecap="round"/>')
    return "".join(g)


body = {"normal": shoe(), "lock": shoe(lock=True), "xray_shoe": shoe(alpha_upper=0.28, laces=False), "xray_base": shoe(upper=False), "xray_upper": shoe(alpha_upper=0.30, laces=False, base=False), "foot": foot()}[V]
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700">{DEFS}{body}</svg>'
open(OUTF, "w").write(svg)
