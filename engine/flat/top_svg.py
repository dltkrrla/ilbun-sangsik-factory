"""Top view of the lacing area (world coords: x 200..880, y 380..1240). python3 top_svg.py out.svg"""
import sys
DX = (430, 650); DROWS = [1150 - 78 * k for k in range(7)]; DTOP = [(392, 560), (688, 560)]
X0, Y0, WD, HT = 200, 380, 680, 860
DEFS = '''<defs>
 <linearGradient id="mesh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C9D0DE"/><stop offset=".25" stop-color="#EEF1F6"/><stop offset=".75" stop-color="#EEF1F6"/><stop offset="1" stop-color="#C9D0DE"/></linearGradient>
 <linearGradient id="navy" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1F3270"/><stop offset=".5" stop-color="#34539E"/><stop offset="1" stop-color="#1F3270"/></linearGradient>
 <linearGradient id="tongue" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2A4590"/><stop offset=".5" stop-color="#4469C2"/><stop offset="1" stop-color="#2A4590"/></linearGradient>
 <radialGradient id="metal" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#C3C8D4"/><stop offset="1" stop-color="#8A91A3"/></radialGradient>
 <radialGradient id="hole" cx=".5" cy=".35" r=".7"><stop offset="0" stop-color="#4A5070"/><stop offset="1" stop-color="#151926"/></radialGradient>
 <linearGradient id="yel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD84D"/><stop offset="1" stop-color="#F2B800"/></linearGradient>
 <pattern id="dots" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="1.8" fill="#AEB7CB" fill-opacity=".55"/></pattern>
 <clipPath id="cs"><path id="shoe" d="M 300,540 C 300,452 380,418 540,418 C 700,418 780,452 780,540 C 790,720 806,960 812,1260 L 268,1260 C 274,960 290,720 300,540 Z"/></clipPath>
</defs>'''
OL = 'stroke="#1E2440" stroke-width="3.2" stroke-linejoin="round"'
SHOE = "M 300,540 C 300,452 380,418 540,418 C 700,418 780,452 780,540 C 790,720 806,960 812,1260 L 268,1260 C 274,960 290,720 300,540 Z"


def eye(x, y):
    return (f'<ellipse cx="{x}" cy="{y}" rx="17" ry="16" fill="url(#metal)" stroke="#1E2440" stroke-width="2.4"/>'
            f'<ellipse cx="{x}" cy="{y+1}" rx="8.5" ry="8" fill="url(#hole)"/>')


def lace(a, b, w=15):
    return (f'<path d="M {a[0]},{a[1]} L {b[0]},{b[1]}" stroke="#8E97AD" stroke-width="{w+7}" stroke-linecap="round"/>'
            f'<path d="M {a[0]},{a[1]} L {b[0]},{b[1]}" stroke="#FFFFFF" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M {a[0]},{a[1]-4} L {b[0]},{b[1]-4}" stroke="#FFFFFF" stroke-opacity=".0" stroke-width="3"/>')


g = [f'<path d="{SHOE}" fill="url(#mesh)" {OL}/>',
     f'<g clip-path="url(#cs)"><rect x="200" y="380" width="680" height="900" fill="url(#dots)"/></g>',
     '<ellipse cx="540" cy="470" rx="168" ry="44" fill="#22273A" stroke="#1E2440" stroke-width="3.2"/>',
     '<ellipse cx="540" cy="466" rx="150" ry="32" fill="#3A4060"/>',
     '<path d="M 372,470 C 372,436 450,424 540,424 C 630,424 708,436 708,470" fill="none" stroke="#2A4590" stroke-width="16" stroke-linecap="round"/>',
     f'<path d="M 470,520 C 470,452 490,432 540,432 C 590,432 610,452 610,520 L 612,1260 L 468,1260 Z" fill="url(#tongue)" {OL}/>',
     '<rect x="522" y="452" width="36" height="22" rx="5" fill="url(#yel)"/>',
     f'<path d="M 374,540 C 380,600 400,700 404,1260 L 462,1260 C 460,900 456,640 446,560 C 430,540 398,532 374,540 Z" fill="url(#navy)" {OL}/>',
     f'<path d="M 706,540 C 700,600 680,700 676,1260 L 618,1260 C 620,900 624,640 634,560 C 650,540 682,532 706,540 Z" fill="url(#navy)" {OL}/>',
     '<path d="M 414,580 C 424,700 430,900 432,1240 M 666,580 C 656,700 650,900 648,1240" fill="none" stroke="#8FA6E0" stroke-width="2.4" stroke-dasharray="7 6"/>']
for k in range(len(DROWS) - 1):
    g.append(lace((DX[0], DROWS[k]), (DX[1], DROWS[k + 1])))
    g.append(lace((DX[1], DROWS[k]), (DX[0], DROWS[k + 1])))
for y in DROWS:
    g.append(eye(DX[0], y)); g.append(eye(DX[1], y))
for x, y in DTOP:
    g.append(eye(x, y))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WD}" height="{HT}" viewBox="{X0} {Y0} {WD} {HT}">' + DEFS + "".join(g) + "</svg>")
open(sys.argv[1], "w").write(svg)
