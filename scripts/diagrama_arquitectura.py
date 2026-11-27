"""Genera docs/arquitectura.svg y una página HTML para exportarla a PNG."""
import sys
from html import escape

OUT_SVG, OUT_HTML = sys.argv[1], sys.argv[2]
W, H = 1600, 1170

INK = "#14213D"
SUB = "#4A5468"
PAPER = "#F7F5F0"
LANE_A = "#EFEBE3"
LANE_B = "#F7F5F0"
FLOW = "#C2410C"
AI = "#5B3CC4"
DATA = "#0B6E7F"
DEPLOY = "#6B7280"

parts = []
add = parts.append


def text(x, y, s, size=13, weight=400, fill=INK, anchor="start", family="sans", spacing=0):
    fam = "'IBM Plex Mono', monospace" if family == "mono" else "'IBM Plex Sans', sans-serif"
    add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{spacing}">{escape(s)}</text>')


def box(x, y, w, h, title, lines, stroke=INK, fill="#FFFFFF", title_fill=INK, accent=None):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="1.25" filter="url(#lift)"/>')
    if accent:
        add(f'<rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{accent}"/>')
    text(x + 14, y + 26, title, 14.5, 600, title_fill)
    for i, ln in enumerate(lines):
        text(x + 14, y + 46 + i * 17, ln, 12, 400, SUB)


def badge(x, y, n, color=FLOW):
    add(f'<circle cx="{x}" cy="{y}" r="11.5" fill="{color}" stroke="#FFFFFF" stroke-width="2"/>')
    text(x, y + 4.3, str(n), 12.5, 700, "#FFFFFF", "middle")


def path(d, color=FLOW, width=2, dash=None, marker="arr"):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{marker})"' if marker else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}{mk} '
        f'stroke-linecap="round" stroke-linejoin="round"/>')


def label(x, y, s, color=FLOW, anchor="start"):
    text(x, y, s, 11.5, 500, color, anchor)


def person(cx, top, name, role):
    add(f'<circle cx="{cx}" cy="{top + 10}" r="9" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    add(f'<path d="M{cx - 16} {top + 40} a16 16 0 0 1 32 0" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    text(cx, top + 62, name, 14, 600, INK, "middle")
    text(cx, top + 79, role, 11.5, 400, SUB, "middle")


ICONS = {'github': 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12', 'githubactions': 'M10.984 13.836a.5.5 0 0 1-.353-.146l-.745-.743a.5.5 0 1 1 .706-.708l.392.391 1.181-1.18a.5.5 0 0 1 .708.707l-1.535 1.533a.504.504 0 0 1-.354.146zm9.353-.147l1.534-1.532a.5.5 0 0 0-.707-.707l-1.181 1.18-.392-.391a.5.5 0 1 0-.706.708l.746.743a.497.497 0 0 0 .706-.001zM4.527 7.452l2.557-1.585A1 1 0 0 0 7.09 4.17L4.533 2.56A1 1 0 0 0 3 3.406v3.196a1.001 1.001 0 0 0 1.527.85zm2.03-2.436L4 6.602V3.406l2.557 1.61zM24 12.5c0 1.93-1.57 3.5-3.5 3.5a3.503 3.503 0 0 1-3.46-3h-2.08a3.503 3.503 0 0 1-3.46 3 3.502 3.502 0 0 1-3.46-3h-.558c-.972 0-1.85-.399-2.482-1.042V17c0 1.654 1.346 3 3 3h.04c.244-1.693 1.7-3 3.46-3 1.93 0 3.5 1.57 3.5 3.5S13.43 24 11.5 24a3.502 3.502 0 0 1-3.46-3H8c-2.206 0-4-1.794-4-4V9.899A5.008 5.008 0 0 1 0 5c0-2.757 2.243-5 5-5s5 2.243 5 5a5.005 5.005 0 0 1-4.952 4.998A2.482 2.482 0 0 0 7.482 12h.558c.244-1.693 1.7-3 3.46-3a3.502 3.502 0 0 1 3.46 3h2.08a3.503 3.503 0 0 1 3.46-3c1.93 0 3.5 1.57 3.5 3.5zm-15 8c0 1.378 1.122 2.5 2.5 2.5s2.5-1.122 2.5-2.5-1.122-2.5-2.5-2.5S9 19.122 9 20.5zM5 9c2.206 0 4-1.794 4-4S7.206 1 5 1 1 2.794 1 5s1.794 4 4 4zm9 3.5c0-1.378-1.122-2.5-2.5-2.5S9 11.122 9 12.5s1.122 2.5 2.5 2.5 2.5-1.122 2.5-2.5zm9 0c0-1.378-1.122-2.5-2.5-2.5S18 11.122 18 12.5s1.122 2.5 2.5 2.5 2.5-1.122 2.5-2.5zm-13 8a.5.5 0 1 0 1 0 .5.5 0 0 0-1 0zm2 0a.5.5 0 1 0 1 0 .5.5 0 0 0-1 0zm12 0c0 1.93-1.57 3.5-3.5 3.5a3.503 3.503 0 0 1-3.46-3.002c-.007.001-.013.005-.021.005l-.506.017h-.017a.5.5 0 0 1-.016-.999l.506-.017c.018-.002.035.006.052.007A3.503 3.503 0 0 1 20.5 17c1.93 0 3.5 1.57 3.5 3.5zm-1 0c0-1.378-1.122-2.5-2.5-2.5S18 19.122 18 20.5s1.122 2.5 2.5 2.5 2.5-1.122 2.5-2.5z', 'googlegemini': 'M11.04 19.32Q12 21.51 12 24q0-2.49.93-4.68.96-2.19 2.58-3.81t3.81-2.55Q21.51 12 24 12q-2.49 0-4.68-.93a12.3 12.3 0 0 1-3.81-2.58 12.3 12.3 0 0 1-2.58-3.81Q12 2.49 12 0q0 2.49-.96 4.68-.93 2.19-2.55 3.81a12.3 12.3 0 0 1-3.81 2.58Q2.49 12 0 12q2.49 0 4.68.96 2.19.93 3.81 2.55t2.55 3.81', 'n8n': 'M21.4737 5.6842c-1.1772 0-2.1663.8051-2.4468 1.8947h-2.8955c-1.235 0-2.289.893-2.492 2.111l-.1038.623a1.263 1.263 0 0 1-1.246 1.0555H11.289c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947s-2.1663.8051-2.4467 1.8947H4.973c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947C1.1311 9.4737 0 10.6047 0 12s1.131 2.5263 2.5263 2.5263c1.1772 0 2.1663-.8051 2.4468-1.8947h1.4223c.2804 1.0896 1.2696 1.8947 2.4467 1.8947 1.1772 0 2.1663-.8051 2.4468-1.8947h1.0008a1.263 1.263 0 0 1 1.2459 1.0555l.1038.623c.203 1.218 1.257 2.111 2.492 2.111h.3692c.2804 1.0895 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263c-1.1772 0-2.1664.805-2.4468 1.8947h-.3692a1.263 1.263 0 0 1-1.246-1.0555l-.1037-.623A2.52 2.52 0 0 0 13.9607 12a2.52 2.52 0 0 0 .821-1.4794l.1038-.623a1.263 1.263 0 0 1 1.2459-1.0555h2.8955c.2805 1.0896 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263m0 1.2632a1.263 1.263 0 0 1 1.2631 1.2631 1.263 1.263 0 0 1-1.2631 1.2632 1.263 1.263 0 0 1-1.2632-1.2632 1.263 1.263 0 0 1 1.2632-1.2631M2.5263 10.7368A1.263 1.263 0 0 1 3.7895 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 1.2632 12a1.263 1.263 0 0 1 1.2631-1.2632m6.3158 0A1.263 1.263 0 0 1 10.1053 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 7.579 12a1.263 1.263 0 0 1 1.2632-1.2632m10.1053 3.7895a1.263 1.263 0 0 1 1.2631 1.2632 1.263 1.263 0 0 1-1.2631 1.2631 1.263 1.263 0 0 1-1.2632-1.2631 1.263 1.263 0 0 1 1.2632-1.2632', 'postgresql': 'M23.5594 14.7228a.5269.5269 0 0 0-.0563-.1191c-.139-.2632-.4768-.3418-1.0074-.2321-1.6533.3411-2.2935.1312-2.5256-.0191 1.342-2.0482 2.445-4.522 3.0411-6.8297.2714-1.0507.7982-3.5237.1222-4.7316a1.5641 1.5641 0 0 0-.1509-.235C21.6931.9086 19.8007.0248 17.5099.0005c-1.4947-.0158-2.7705.3461-3.1161.4794a9.449 9.449 0 0 0-.5159-.0816 8.044 8.044 0 0 0-1.3114-.1278c-1.1822-.0184-2.2038.2642-3.0498.8406-.8573-.3211-4.7888-1.645-7.2219.0788C.9359 2.1526.3086 3.8733.4302 6.3043c.0409.818.5069 3.334 1.2423 5.7436.4598 1.5065.9387 2.7019 1.4334 3.582.553.9942 1.1259 1.5933 1.7143 1.7895.4474.1491 1.1327.1441 1.8581-.7279.8012-.9635 1.5903-1.8258 1.9446-2.2069.4351.2355.9064.3625 1.39.3772a.0569.0569 0 0 0 .0004.0041 11.0312 11.0312 0 0 0-.2472.3054c-.3389.4302-.4094.5197-1.5002.7443-.3102.064-1.1344.2339-1.1464.8115-.0025.1224.0329.2309.0919.3268.2269.4231.9216.6097 1.015.6331 1.3345.3335 2.5044.092 3.3714-.6787-.017 2.231.0775 4.4174.3454 5.0874.2212.5529.7618 1.9045 2.4692 1.9043.2505 0 .5263-.0291.8296-.0941 1.7819-.3821 2.5557-1.1696 2.855-2.9059.1503-.8707.4016-2.8753.5388-4.1012.0169-.0703.0357-.1207.057-.1362.0007-.0005.0697-.0471.4272.0307a.3673.3673 0 0 0 .0443.0068l.2539.0223.0149.001c.8468.0384 1.9114-.1426 2.5312-.4308.6438-.2988 1.8057-1.0323 1.5951-1.6698zM2.371 11.8765c-.7435-2.4358-1.1779-4.8851-1.2123-5.5719-.1086-2.1714.4171-3.6829 1.5623-4.4927 1.8367-1.2986 4.8398-.5408 6.108-.13-.0032.0032-.0066.0061-.0098.0094-2.0238 2.044-1.9758 5.536-1.9708 5.7495-.0002.0823.0066.1989.0162.3593.0348.5873.0996 1.6804-.0735 2.9184-.1609 1.1504.1937 2.2764.9728 3.0892.0806.0841.1648.1631.2518.2374-.3468.3714-1.1004 1.1926-1.9025 2.1576-.5677.6825-.9597.5517-1.0886.5087-.3919-.1307-.813-.5871-1.2381-1.3223-.4796-.839-.9635-2.0317-1.4155-3.5126zm6.0072 5.0871c-.1711-.0428-.3271-.1132-.4322-.1772.0889-.0394.2374-.0902.4833-.1409 1.2833-.2641 1.4815-.4506 1.9143-1.0002.0992-.126.2116-.2687.3673-.4426a.3549.3549 0 0 0 .0737-.1298c.1708-.1513.2724-.1099.4369-.0417.156.0646.3078.26.3695.4752.0291.1016.0619.2945-.0452.4444-.9043 1.2658-2.2216 1.2494-3.1676 1.0128zm2.094-3.988-.0525.141c-.133.3566-.2567.6881-.3334 1.003-.6674-.0021-1.3168-.2872-1.8105-.8024-.6279-.6551-.9131-1.5664-.7825-2.5004.1828-1.3079.1153-2.4468.079-3.0586-.005-.0857-.0095-.1607-.0122-.2199.2957-.2621 1.6659-.9962 2.6429-.7724.4459.1022.7176.4057.8305.928.5846 2.7038.0774 3.8307-.3302 4.7363-.084.1866-.1633.3629-.2311.5454zm7.3637 4.5725c-.0169.1768-.0358.376-.0618.5959l-.146.4383a.3547.3547 0 0 0-.0182.1077c-.0059.4747-.054.6489-.115.8693-.0634.2292-.1353.4891-.1794 1.0575-.11 1.4143-.8782 2.2267-2.4172 2.5565-1.5155.3251-1.7843-.4968-2.0212-1.2217a6.5824 6.5824 0 0 0-.0769-.2266c-.2154-.5858-.1911-1.4119-.1574-2.5551.0165-.5612-.0249-1.9013-.3302-2.6462.0044-.2932.0106-.5909.019-.8918a.3529.3529 0 0 0-.0153-.1126 1.4927 1.4927 0 0 0-.0439-.208c-.1226-.4283-.4213-.7866-.7797-.9351-.1424-.059-.4038-.1672-.7178-.0869.067-.276.1831-.5875.309-.9249l.0529-.142c.0595-.16.134-.3257.213-.5012.4265-.9476 1.0106-2.2453.3766-5.1772-.2374-1.0981-1.0304-1.6343-2.2324-1.5098-.7207.0746-1.3799.3654-1.7088.5321a5.6716 5.6716 0 0 0-.1958.1041c.0918-1.1064.4386-3.1741 1.7357-4.4823a4.0306 4.0306 0 0 1 .3033-.276.3532.3532 0 0 0 .1447-.0644c.7524-.5706 1.6945-.8506 2.802-.8325.4091.0067.8017.0339 1.1742.081 1.939.3544 3.2439 1.4468 4.0359 2.3827.8143.9623 1.2552 1.9315 1.4312 2.4543-1.3232-.1346-2.2234.1268-2.6797.779-.9926 1.4189.543 4.1729 1.2811 5.4964.1353.2426.2522.4522.2889.5413.2403.5825.5515.9713.7787 1.2552.0696.087.1372.1714.1885.245-.4008.1155-1.1208.3825-1.0552 1.717-.0123.1563-.0423.4469-.0834.8148-.0461.2077-.0702.4603-.0994.7662zm.8905-1.6211c-.0405-.8316.2691-.9185.5967-1.0105a2.8566 2.8566 0 0 0 .135-.0406 1.202 1.202 0 0 0 .1342.103c.5703.3765 1.5823.4213 3.0068.1344-.2016.1769-.5189.3994-.9533.6011-.4098.1903-1.0957.333-1.7473.3636-.7197.0336-1.0859-.0807-1.1721-.151zm.5695-9.2712c-.0059.3508-.0542.6692-.1054 1.0017-.055.3576-.112.7274-.1264 1.1762-.0142.4368.0404.8909.0932 1.3301.1066.887.216 1.8003-.2075 2.7014a3.5272 3.5272 0 0 1-.1876-.3856c-.0527-.1276-.1669-.3326-.3251-.6162-.6156-1.1041-2.0574-3.6896-1.3193-4.7446.3795-.5427 1.3408-.5661 2.1781-.463zm.2284 7.0137a12.3762 12.3762 0 0 0-.0853-.1074l-.0355-.0444c.7262-1.1995.5842-2.3862.4578-3.4385-.0519-.4318-.1009-.8396-.0885-1.2226.0129-.4061.0666-.7543.1185-1.0911.0639-.415.1288-.8443.1109-1.3505.0134-.0531.0188-.1158.0118-.1902-.0457-.4855-.5999-1.938-1.7294-3.253-.6076-.7073-1.4896-1.4972-2.6889-2.0395.5251-.1066 1.2328-.2035 2.0244-.1859 2.0515.0456 3.6746.8135 4.8242 2.2824a.908.908 0 0 1 .0667.1002c.7231 1.3556-.2762 6.2751-2.9867 10.5405zm-8.8166-6.1162c-.025.1794-.3089.4225-.6211.4225a.5821.5821 0 0 1-.0809-.0056c-.1873-.026-.3765-.144-.5059-.3156-.0458-.0605-.1203-.178-.1055-.2844.0055-.0401.0261-.0985.0925-.1488.1182-.0894.3518-.1226.6096-.0867.3163.0441.6426.1938.6113.4186zm7.9305-.4114c.0111.0792-.049.201-.1531.3102-.0683.0717-.212.1961-.4079.2232a.5456.5456 0 0 1-.075.0052c-.2935 0-.5414-.2344-.5607-.3717-.024-.1765.2641-.3106.5611-.352.297-.0414.6111.0088.6356.1851z', 'supabase': 'M11.9 1.036c-.015-.986-1.26-1.41-1.874-.637L.764 12.05C-.33 13.427.65 15.455 2.409 15.455h9.579l.113 7.51c.014.985 1.259 1.408 1.873.636l9.262-11.653c1.093-1.375.113-3.403-1.645-3.403h-9.642z', 'telegram': 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z', 'vercel': 'M24 22.525H0l12-21.05 12 21.05z'}


def icon(slug, x, y, size, color):
    k = size / 24
    add(f'<g transform="translate({x} {y}) scale({k})"><path d="{ICONS[slug]}" fill="{color}"/></g>')


# ---------- lienzo ----------
add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
text(32, 52, "Asistencia en la puerta · arquitectura", 28, 600, INK, spacing=-0.4)
text(32, 80, "La asistencia se registra al entrar; las faltas se gestionan con la familia; la persona solo decide.",
     14.5, 400, SUB)
text(1568, 52, "FABATECH · Track T3", 13, 500, SUB, "end")
text(1568, 74, "EduTech Eight Academy by n8n · nov 2026", 12, 400, SUB, "end")

lanes = [
    (104, 110, "Personas", "quién usa el sistema"),
    (222, 130, "Interfaces", "dónde ocurre cada acción"),
    (360, 160, "Orquestación", "n8n Cloud, instancia|del equipo (Starter)"),
    (528, 130, "IA y reglas", "la IA extrae,|las reglas validan"),
    (666, 170, "Datos", "Supabase Postgres|plan gratis"),
]
for i, (y, h, name, sub) in enumerate(lanes):
    add(f'<rect x="16" y="{y}" width="1214" height="{h}" fill="{LANE_A if i % 2 == 0 else "#FBFAF7"}"/>')
    add(f'<line x1="16" y1="{y}" x2="1230" y2="{y}" stroke="#D9D3C7" stroke-width="1"/>')
    text(30, y + 30, name, 15, 600, INK)
    for k, sl in enumerate(sub.split("|")):
        text(30, y + 49 + k * 16, sl, 11.5, 400, SUB)
add('<line x1="200" y1="104" x2="200" y2="836" stroke="#D9D3C7" stroke-width="1"/>')
add('<line x1="16" y1="836" x2="1230" y2="836" stroke="#D9D3C7" stroke-width="1"/>')

# ---------- A · personas ----------
person(290, 112, "Inspector general", "aprueba y ve excepciones")
person(452, 112, "Estudiante", "escanea su carné")
person(710, 112, "Familia", "representante del estudiante")
person(1135, 112, "Docente tutor", "ve el curso sin tomar lista")

# ---------- B · interfaces ----------
box(232, 246, 220, 84, "Puerta: tótem o app", ["Tótem de autoservicio (lector", "QR USB o cámara) · app web"], accent=FLOW)
icon("vercel", 424, 258, 16, INK)
box(590, 246, 240, 84, "Bot de Telegram", ["Familias e inspector:", "texto, voz, fotos y botones"], accent=FLOW)
icon("telegram", 800, 258, 18, "#26A5E4")
box(990, 246, 220, 84, "Tablero en vivo", ["Ingresos, ausentes, pendientes", "y horas docentes ahorradas"], accent=DATA)
icon("vercel", 1182, 258, 16, INK)

# ---------- C · n8n ----------
add(f'<rect x="224" y="372" width="926" height="136" rx="8" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 4"/>')
icon("n8n", 986, 379, 16, "#EA4B71")
text(1008, 392, "n8n Cloud · Starter", 12.5, 600, INK)
box(236, 404, 160, 90, "WF1 · Ingreso", ["Valida el carné y", "registra «presente»"])
box(412, 404, 160, 90, "WF2 · Ausencias", ["Cruza la lista del", "curso con los ingresos"])
box(588, 404, 184, 90, "WF3 · Justificativo", ["Recibe texto, voz o foto", "y pide la extracción"])
box(788, 404, 172, 90, "WF4 · Aprobación", ["Send and Wait al", "inspector en Telegram"])
box(976, 404, 160, 90, "WF0 · Errores", ["Error Trigger: avisa", "al equipo si algo falla"], stroke="#9AA1AE")

# ---------- D · IA y reglas ----------
box(540, 552, 180, 84, "Gemini", ["Texto, voz, imagen →", "JSON con esquema"], stroke=AI, title_fill=AI, accent=AI)
icon("googlegemini", 690, 564, 18, "#8E75B2")
box(772, 552, 180, 84, "Reglas deterministas", ["Representante ↔ estudiante,", "fechas = faltas reales, plazo"])
box(1004, 552, 136, 84, "Revisión manual", ["Si la IA falla o", "algo no valida"], stroke="#9AA1AE")

# ---------- E · datos ----------
add(f'<rect x="224" y="678" width="1002" height="146" rx="8" fill="none" stroke="{DATA}" stroke-width="1.4" stroke-dasharray="6 4"/>')
add(f'<rect x="312" y="712" width="600" height="98" rx="6" fill="#FFFFFF" stroke="{DATA}" stroke-width="1.25" filter="url(#lift)"/>')
text(326, 736, "Postgres", 14.5, 600, DATA)
icon("postgresql", 884, 722, 18, "#4169E1")
icon("supabase", 930, 685, 16, "#3ECF8E")
text(952, 698, "Supabase · plan gratis", 12.5, 600, DATA)
chips = ["estudiantes", "representantes", "carnés", "ingresos", "faltas", "justificativos", "auditoría"]
cx, cy = 326, 752
for c in chips:
    w = 14 + len(c) * 7.6
    if cx + w > 900:
        cx, cy = 326, cy + 28
    add(f'<rect x="{cx}" y="{cy}" width="{w}" height="22" rx="4" fill="#EAF4F6" stroke="#B9DCE2"/>')
    text(cx + 7, cy + 15.5, c, 11.5, 500, DATA, family="mono")
    cx += w + 8
box(930, 712, 124, 98, "RLS por rol", ["Cada rol ve solo", "lo suyo; claves", "en el servidor"], stroke=DATA, title_fill=DATA)
box(1070, 712, 140, 98, "Realtime", ["Postgres Changes:", "el tablero cambia", "sin recargar"], stroke=DATA, title_fill=DATA)

# ---------- E2 · entrega continua ----------
add(f'<rect x="1246" y="222" width="338" height="614" rx="8" fill="#FFFFFF" stroke="{DEPLOY}" stroke-width="1.4"/>')
text(1264, 250, "Entrega continua", 15, 600, INK)
text(1264, 269, "nada se despliega a mano", 11.5, 400, SUB)
box(1264, 286, 302, 72, "Repositorio GitHub", ["Rama + PR · n8n/*.json · migraciones SQL"], stroke=DEPLOY)
icon("github", 1538, 298, 18, INK)
box(1264, 376, 302, 90, "CI en cada PR", ["Estructura, secretos, JSON de n8n,", "pruebas · preview de Vercel"], stroke=DEPLOY)
icon("githubactions", 1538, 388, 18, "#2088FF")
path("M1415 358 L1415 372", DEPLOY, 1.6, marker="arrg")
path("M1415 466 L1415 482", DEPLOY, 1.6, marker="arrg")
add(f'<rect x="1264" y="486" width="302" height="334" rx="6" fill="#FFFFFF" stroke="{DEPLOY}" stroke-width="1.25" filter="url(#lift)"/>')
text(1278, 512, "Al fusionar a main", 14.5, 600, INK)
icon("githubactions", 1538, 498, 18, "#2088FF")
text(1278, 530, "el número indica el orden de ejecución", 11.5, 400, SUB)
steps = [
    ("4", "Vercel publica app y tablero", "producción desde main", "vercel", INK),
    ("2", "n8n API: PUT borrador", "y luego POST /publish", "n8n", "#EA4B71"),
    ("3", "Prueba de humo", "webhook de producción + fila en BD", "githubactions", "#2088FF"),
    ("1", "supabase db push", "migraciones antes que nada", "supabase", "#3ECF8E"),
]
for i, (k, t1, t2, ic, icc) in enumerate(steps):
    y0 = 540 + i * 70
    add(f'<rect x="1278" y="{y0}" width="22" height="22" rx="4" fill="#F1F2F4" stroke="#C9CDD4"/>')
    text(1289, y0 + 15.5, k, 12, 600, DEPLOY, "middle", family="mono")
    text(1310, y0 + 15, t1, 13, 600, INK)
    text(1310, y0 + 33, t2, 11.5, 400, SUB)
    icon(ic, 1538, y0 + 2, 18, icc)

# despliegues (gris punteado)
path("M1264 551 L1218 551 L1218 300 L1212 300", DEPLOY, 1.5, "5 4", "arrg")
path("M1264 621 L1200 621 Q1192 613 1184 621 L1152 621 L1152 470", DEPLOY, 1.5, "5 4", "arrg")
path("M1264 761 L1228 761", DEPLOY, 1.5, "5 4", "arrg")

# ---------- flujo del demo (numerado) ----------
path("M440 200 L440 244")                       # 1 estudiante -> puerta
badge(462, 222, 1)
path("M316 330 L316 402")                       # 2 app -> WF1
badge(338, 368, 2)
path("M492 404 L492 300 L588 300")              # 3 WF2 -> bot -> familia
path("M700 246 L700 206")
badge(540, 300, 3)
path("M720 206 L720 244")                       # 4 familia -> bot -> WF3
path("M720 330 L720 402")
badge(742, 368, 4)
path("M640 494 L640 550", AI)                   # 5 WF3 -> Gemini
badge(618, 522, 5, AI)
path("M720 594 L770 594", AI)                   # 6 Gemini -> reglas
badge(746, 572, 6, AI)
path("M870 552 L870 496")                       # reglas -> WF4 (válido)
label(880, 532, "válido")
path("M952 594 L1002 594", "#9AA1AE", 1.6, "4 3", "arrs")
path("M874 404 L874 300 L832 300")              # 7 WF4 -> bot -> inspector
path("M610 246 L610 108 L290 108 L290 110")
badge(874, 352, 7)
label(330, 101, "aprueba o rechaza con un toque")
path("M270 494 L270 761 L310 761", DATA, 2)     # 8 n8n <-> Postgres
add(f'<path d="M262 510 L270 496 L278 510" fill="none" stroke="{DATA}" stroke-width="2" stroke-linecap="round"/>')
badge(270, 620, 8, DATA)
label(284, 616, "SQL", DATA)
path("M1185 712 L1185 332", DATA, 2)            # 9 realtime -> tablero -> docente
path("M1135 246 L1135 208", DATA, 2)
badge(1185, 540, 9, DATA)

# ---------- leyenda ----------
add('<line x1="32" y1="866" x2="1568" y2="866" stroke="#D9D3C7"/>')
text(32, 898, "El flujo, paso a paso", 14, 600, INK)
flujo = [
    "El estudiante escanea su carné en el tótem (o el inspector con la app).",
    "El escaneo llega a WF1, que registra «presente».",
    "Al cerrar el ingreso, WF2 detecta ausentes y escribe a cada familia.",
    "La familia responde con texto, nota de voz o foto (WF3).",
    "Gemini extrae estudiante, fechas y motivo en un JSON con esquema.",
    "Reglas deterministas validan; si algo no cuadra, revisión manual.",
    "WF4 pide al inspector aprobar o rechazar en Telegram.",
    "Cada paso queda en Postgres, con auditoría.",
    "Realtime actualiza el tablero que ven inspector y tutor.",
]
for i, t in enumerate(flujo):
    y0 = 926 + i * 24
    c = AI if i in (4, 5) else (DATA if i in (7, 8) else FLOW)
    add(f'<circle cx="41" cy="{y0 - 4.5}" r="9" fill="{c}"/>')
    text(41, y0 - 0.5, str(i + 1), 11, 700, "#FFFFFF", "middle")
    text(60, y0, t, 13, 400, INK)

text(640, 898, "Qué deja de hacer el docente", 14, 600, INK)
gain = [
    ("1–2", "No toma lista: el tótem la registra."),
    ("3–6", "No persigue justificativos: llegan armados."),
    ("7", "Solo decide, con un toque."),
    ("9", "Ve su curso en vivo, sin hojas."),
]
for i, (n, t) in enumerate(gain):
    y0 = 926 + i * 24
    text(640, y0, n, 12, 600, FLOW, family="mono")
    text(680, y0, t, 13, 400, INK)

text(640, 1046, "Líneas", 14, 600, INK)
leg = [(FLOW, None, "Flujo del demo"), (AI, None, "IA: solo extrae"),
       (DATA, None, "Datos y tiempo real"), (DEPLOY, "5 4", "Despliegue automático")]
for i, (c, d, t) in enumerate(leg):
    x0 = 640 + (i % 2) * 210
    y0 = 1072 + (i // 2) * 26
    da = f' stroke-dasharray="{d}"' if d else ""
    add(f'<line x1="{x0}" y1="{y0}" x2="{x0 + 36}" y2="{y0}" stroke="{c}" stroke-width="2.2"{da}/>')
    text(x0 + 46, y0 + 4.5, t, 12.5, 400, INK)

text(1110, 898, "Si algo falla", 14, 600, INK)
fail = [
    "La IA no decide: extrae; las reglas",
    "validan y una persona aprueba.",
    "Si Gemini falla o algo no valida,",
    "el caso va a revisión manual.",
    "El registro en la puerta no depende",
    "de la IA. WF0 avisa al equipo ante",
    "cualquier error de ejecución.",
]
for i, t in enumerate(fail):
    text(1110, 926 + i * 22, t, 13, 400, INK)

text(32, 1150, "Fuente del problema: Ministerio de Educación, «Tiempo para Ser Docente» (2025). Datos del demo: sintéticos.",
     11.5, 400, SUB)

defs = f"""<defs>
<filter id="lift" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="1.5" stdDeviation="1.6" flood-color="#14213D" flood-opacity="0.10"/></filter>
<marker id="arr" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" fill="{FLOW}"/></marker>
<marker id="arrg" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" fill="{DEPLOY}"/></marker>
<marker id="arrs" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" fill="#9AA1AE"/></marker>
</defs>"""
# Las flechas de IA y datos usan su propio color de marcador.
svg_body = "\n".join(parts)
svg_body = svg_body.replace(f'stroke="{AI}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arr)"',
                            f'stroke="{AI}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arra)"')
svg_body = svg_body.replace(f'stroke="{DATA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arr)"',
                            f'stroke="{DATA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrd)"')
defs = defs.replace("</defs>",
    f'<marker id="arra" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" fill="{AI}"/></marker>'
    f'<marker id="arrd" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" fill="{DATA}"/></marker></defs>')

font = ("<style>@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600"
        "&amp;family=IBM+Plex+Sans:wght@400;500;600;700&amp;display=block');</style>")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'role="img" aria-label="Arquitectura de Asistencia en la puerta">{font}{defs}{svg_body}</svg>')
open(OUT_SVG, "w", encoding="utf-8", newline="\n").write(svg)
html = (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:{PAPER}}}</style>'
        f'</head><body>{svg}</body></html>')
open(OUT_HTML, "w", encoding="utf-8", newline="\n").write(html)
print("ok")
