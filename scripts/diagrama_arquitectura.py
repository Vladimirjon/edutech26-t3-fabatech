"""Diagrama de arquitectura v2: fronteras por proveedor, baldosas con logo y flujo numerado.

Uso: python -I gen2.py <carpeta_iconos> <salida.svg> <salida.html>
"""
import os
import re
import sys
from html import escape

ICON_DIR, OUT_SVG, OUT_HTML = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 1800, 1270

INK = "#1B2333"
SUB = "#5B6475"
STEP = "#4C4CE0"
DEPLOY = "#7A8291"
N8N, TG, SUPA, GEM, VER, GH, GHA, PG = "#EA4B71", "#229ED9", "#249361", "#8E75B2", "#000000", "#24292F", "#2088FF", "#336791"
CODE, WAIT, ALERT = "#FF6D5A", "#D9822B", "#C2410C"

BRAND = {}
for f in os.listdir(ICON_DIR):
    BRAND[f[:-4]] = re.search(r'<path d="([^"]+)"', open(os.path.join(ICON_DIR, f), encoding="utf-8").read()).group(1)

out = []
add = out.append
FONT = "'Geist', 'Inter', sans-serif"


def text(x, y, s, size=13, weight=400, fill=INK, anchor="start"):
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')


# ---------- glifos propios (24x24, trazo blanco) ----------
G = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "qr": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>'
          '<rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v.01M14 20h.01M17 20h4v-3"/>',
    "phone": '<rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M21 20H3"/>',
    "hook": '<circle cx="12" cy="6" r="3"/><circle cx="5.5" cy="17" r="3"/><circle cx="18.5" cy="17" r="3"/>'
            '<path d="M10.5 8.6 7 14.4M13.5 8.6 17 14.4M8.5 17h7"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "code": '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "shield": '<path d="M12 2.5 4 5.5v6c0 5 3.4 8.6 8 10 4.6-1.4 8-5 8-10v-6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "check": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="m7.5 12.5 3 3 6-7"/>',
    "alert": '<path d="M12 3 2 20.5h20z"/><path d="M12 10v4.5M12 17.5v.01"/>',
    "chat": '<path d="M4 4h16v12H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
    "pulse": '<path d="M2 12h4l3-7 4 14 3-7h6"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><circle cx="17" cy="9" r="2.8"/><path d="M16 14.2c3.2.2 5.5 2.3 5.5 5.8"/>',
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "schema": '<path d="M8 3H6a2 2 0 0 0-2 2v4l-2 3 2 3v4a2 2 0 0 0 2 2h2M16 3h2a2 2 0 0 1 2 2v4l2 3-2 3v4a2 2 0 0 1-2 2h-2"/>',
}


def glyph(name, cx, cy, size):
    k = size / 24
    add(f'<g transform="translate({cx - size / 2} {cy - size / 2}) scale({k})" fill="none" stroke="#FFFFFF" '
        f'stroke-width="{2 / k * 0.75:.2f}" stroke-linecap="round" stroke-linejoin="round">{G[name]}</g>')


def brand(slug, cx, cy, size, color="#FFFFFF"):
    k = size / 24
    add(f'<g transform="translate({cx - size / 2} {cy - size / 2}) scale({k})"><path d="{BRAND[slug]}" fill="{color}"/></g>')


def tile(cx, cy, color, icon, lines, sub=None, side="below", size=46, gfill=None):
    h = size / 2
    add(f'<rect x="{cx - h}" y="{cy - h}" width="{size}" height="{size}" rx="9" fill="{color}" filter="url(#tile)"/>')
    if icon in BRAND:
        brand(icon, cx, cy, size * 0.52, gfill or "#FFFFFF")
    else:
        glyph(icon, cx, cy, size * 0.56)
    if side == "below":
        for i, ln in enumerate(lines):
            text(cx, cy + h + 17 + i * 15, ln, 12.5, 600, INK, "middle")
        if sub:
            text(cx, cy + h + 17 + len(lines) * 15, sub, 11.5, 400, SUB, "middle")
    else:
        for i, ln in enumerate(lines):
            text(cx + h + 12, cy - 4 + i * 15, ln, 12.5, 600, INK)
        if sub:
            text(cx + h + 12, cy - 4 + len(lines) * 15, sub, 11.5, 400, SUB)


def zone(x, y, w, h, title, color, icon=None, tint=0.06, dash=None, stroke_w=1.4):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}" fill-opacity="{tint}" '
        f'stroke="{color}" stroke-width="{stroke_w}"{da}/>')
    if icon:
        add(f'<rect x="{x}" y="{y}" width="30" height="30" rx="6" fill="{color}"/>')
        if icon in BRAND:
            brand(icon, x + 15, y + 15, 17)
        else:
            glyph(icon, x + 15, y + 15, 18)
        text(x + 40, y + 20, title, 13.5, 600, color if color not in (VER, GH) else INK)
    else:
        text(x + 12, y + 20, title, 13, 600, color)


MARK = {}


def marker(color):
    if color not in MARK:
        MARK[color] = f"m{len(MARK)}"
    return MARK[color]


def line(d, color=INK, width=1.8, dash=None, end=True):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{marker(color)})"' if end else ""
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}{mk} stroke-linejoin="round"/>')


def hop_h(x1, x2, y, hops):
    """Tramos (sin punto inicial) de una horizontal de x1 a x2 con saltos en las x indicadas."""
    d, sgn = "", 1 if x2 > x1 else -1
    for hx in sorted(hops, reverse=sgn < 0):
        d += f" L{hx - 6 * sgn} {y} A6 6 0 0 {1 if sgn > 0 else 0} {hx + 6 * sgn} {y}"
    return d + f" L{x2} {y}"


def step(x, y, n, color=STEP, size=22):
    h = size / 2
    add(f'<rect x="{x - h}" y="{y - h}" width="{size}" height="{size}" rx="5" fill="{color}" stroke="#FFFFFF" stroke-width="2"/>')
    text(x, y + 4.5, str(n), 12, 700, "#FFFFFF", "middle")


# ---------- lienzo ----------
add(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
text(40, 54, "Pórtika", 30, 600, INK)
text(40, 82, "La asistencia se registra en la puerta: así viaja un ingreso hasta el tablero y así se despliega cada pieza.", 15, 400, SUB)
text(1760, 54, "Equipo FABATECH, track T3", 13, 600, INK, "end")
text(1760, 74, "Hackathon EduTech Eight Academy by n8n, noviembre de 2026", 12, 400, SUB, "end")

# ---------- personas ----------
for cx, name, role in [(380, "Estudiante", "escanea su carné"), (560, "Docente tutor", "ve su curso en vivo"),
                       (830, "Familia", "justifica la falta"), (1000, "Inspector general", "aprueba con un toque")]:
    add(f'<circle cx="{cx}" cy="124" r="19" fill="#E9ECF2"/>')
    add(f'<g transform="translate({cx - 11} 113) scale(0.92)" fill="none" stroke="{INK}" stroke-width="1.9" '
        f'stroke-linecap="round">{G["user"]}</g>')
    text(cx + 28, 121, name, 13, 600, INK)
    text(cx + 28, 137, role, 11.5, 400, SUB)

# ---------- capa superior: proveedores externos ----------
zone(230, 200, 410, 150, "Vercel", VER, "vercel", tint=0.035)
tile(270, 280, VER, "phone", ["App del", "inspector"])
tile(380, 280, VER, "qr", ["Tótem de", "autoservicio"])
tile(560, 280, VER, "chart", ["Tablero en vivo"], "inspector y tutor")

zone(660, 200, 380, 150, "Telegram", TG, "telegram")
tile(710, 280, TG, "telegram", ["Bot Pórtika"])
tile(830, 280, TG, "chat", ["Chat de la", "familia"])
tile(1000, 280, TG, "chat", ["Chat del", "inspector"])

zone(1070, 200, 380, 150, "Google AI Studio", GEM, "googlegemini")
tile(1130, 280, GEM, "googlegemini", ["Gemini API"], "nivel gratis")
tile(1340, 280, GEM, "schema", ["Salida con", "JSON Schema"])

# ---------- n8n ----------
zone(230, 390, 1220, 460, "n8n Cloud", N8N, "n8n", tint=0.045)
cols = [
    (250, "WF1", "Ingreso", [("hook", N8N, ["Webhook"], "/ingreso"), ("code", CODE, ["Validar carné"], "sin duplicados"),
                             ("db", PG, ["Registrar"], "«presente»")]),
    (490, "WF2", "Ausencias", [("clock", N8N, ["Schedule"], "cierre 07:30"), ("db", PG, ["Cruzar lista"], "curso vs ingresos"),
                               ("telegram", TG, ["Avisar a"], "cada familia")]),
    (730, "WF3", "Justificativo", [("telegram", N8N, ["Telegram"], "Trigger"), ("googlegemini", GEM, ["AI node"], "texto, voz, foto"),
                                   ("code", CODE, ["Reglas"], "deterministas")]),
    (970, "WF4", "Aprobación", [("telegram", TG, ["Confirmar"], "a la familia"), ("db", PG, ["Falta y"], "auditoría"),
                                ("check", WAIT, ["Send and Wait"], "al inspector")]),
    (1210, "WF0", "Errores", [("alert", ALERT, ["Error Trigger"], None), ("telegram", TG, ["Alerta al"], "equipo"),
                              ("list", "#6B7280", ["Ejecuciones"], "7 días de historial")]),
]
for x0, wid, name, nodes in cols:
    add(f'<rect x="{x0}" y="430" width="220" height="405" rx="6" fill="#FFFFFF" stroke="{N8N}" stroke-opacity="0.55" '
        f'stroke-width="1.2" stroke-dasharray="5 4"/>')
    text(x0 + 14, 456, wid, 14, 700, N8N)
    text(x0 + 14, 473, name, 12.5, 500, INK)
    cx = x0 + 130
    for i, (ic, col, ln, sub) in enumerate(nodes):
        tile(cx, 520 + i * 112, col, ic, ln, sub, size=44)
    for i in range(2):
        upper, lower = 520 + i * 112, 520 + (i + 1) * 112
        if wid == "WF4":
            line(f"M{cx} {lower - 24} L{cx} {upper + 60}", INK, 1.5)
        elif not (wid == "WF0" and i == 1):
            line(f"M{cx} {upper + 58} L{cx} {lower - 25}", INK, 1.5)

# ---------- Supabase ----------
zone(1480, 200, 290, 650, "Supabase, plan gratis", SUPA, "supabase")
tile(1700, 290, SUPA, "bolt", ["Realtime"], "Postgres Changes")
tile(1580, 430, SUPA, "shield", ["RLS por rol"], "el tablero solo lee")
tile(1530, 600, PG, "postgresql", [], None)
text(1566, 596, "Postgres", 13.5, 600, INK)
text(1566, 612, "datos sintéticos", 11.5, 400, SUB)
chips = ["estudiantes", "representantes", "carnés", "ingresos", "faltas", "justificativos", "auditoría"]
for i, c in enumerate(chips):
    x = 1500 + (i % 2) * 132
    y = 650 + (i // 2) * 30
    add(f'<rect x="{x}" y="{y}" width="124" height="22" rx="4" fill="#FFFFFF" stroke="{SUPA}" stroke-opacity="0.55"/>')
    text(x + 10, y + 15.5, c, 11.5, 500, SUPA)

# ---------- GitHub ----------
zone(230, 885, 1540, 135, "GitHub, entrega continua", GH, "github", tint=0.03)
tile(330, 960, "#6B7280", "users", ["Equipo"], "3 personas + agentes")
tile(500, 960, GH, "github", ["Repositorio"], "rama + PR por issue")
tile(680, 960, GHA, "githubactions", ["CI en cada PR"], "estructura, gitleaks, JSON, pruebas")
tile(880, 960, GHA, "githubactions", ["CD al fusionar"], "secretos en GitHub Secrets")
tile(1080, 960, GHA, "pulse", ["Prueba de humo"], "webhook + fila en BD")
line("M353 960 L475 960", INK, 1.5)
line("M523 960 L655 960", INK, 1.5)
line("M703 960 L855 960", INK, 1.5)
line("M903 960 L1055 960", INK, 1.5)
text(1250, 955, "Previews de Vercel en cada PR.", 12, 400, SUB)
text(1250, 972, "Nada se despliega a mano.", 12, 400, SUB)

# ---------- flujo numerado ----------
line("M380 158 L380 255")                         # 1 estudiante -> tótem
step(399, 200, 1)
line("M380 344 L380 496")                         # 2 tótem -> webhook
step(399, 372, 2)
line("M642 744 L676 744 L676 290 L686 290")      # 3 aviso -> bot
step(676, 560, 3)
line("M733 268 L770 268 L770 372 L860 372 L860 496")  # 4 bot -> trigger
line("M830 158 L830 255", INK, 1.5)               # familia <-> chat
line("M830 255 L830 158", INK, 1.5)
line("M807 280 L735 280", INK, 1.5)               # chat -> bot
step(815, 372, 4)
line("M882 632 L960 632 L960 376 L1080 376 L1080 280 L1106 280", GEM)   # 5 AI node -> Gemini
step(960, 500, 5, GEM)
line("M1152 280 L1315 280", GEM, 1.5)             # Gemini -> esquema
line("M882 744 L1076 744")                        # 6 reglas -> send and wait
step(1000, 744, 6)
line("M1122 744 L1200 744 L1200 364" + hop_h(1200, 1032, 364, [1080]) + " L1032 280 L1024 280")
step(1200, 560, 7)
line("M1000 255 L1000 158", INK, 1.5)             # chat -> inspector
line("M1450 632 L1505 632", SUPA, 2)              # 8 n8n -> postgres
step(1466, 610, 8, SUPA)
line("M1515 577 L1515 290 L1675 290", SUPA, 2)    # postgres -> realtime
line("M1700 266 L1700 190" + hop_h(1700, 650, 190, [1000, 830]) + " L650 280 L585 280", SUPA, 2)              # 9 realtime -> tablero
step(1260, 190, 9, SUPA)
line("M560 255 L560 158", INK, 1.5)               # tablero -> docente

# ---------- despliegue ----------
line("M880 937 L880 852", DEPLOY, 1.6, "5 4")     # D2 n8n
line("M1080 937 L1080 852", DEPLOY, 1.6, "5 4")   # D3 humo
line("M896 937 L896 912" + hop_h(896, 1690, 912, [1080]) + " L1690 852",
     DEPLOY, 1.6, "5 4")                           # D1 supabase
line("M864 937 L864 924 L214 924 L214 280 L228 280", DEPLOY, 1.6, "5 4")  # D4 vercel
for x, y, t in [(1690, 880, "D1"), (880, 870, "D2"), (1080, 870, "D3"), (214, 600, "D4")]:
    step(x, y, t, DEPLOY, 26)

# ---------- leyenda ----------
add(f'<line x1="40" y1="1048" x2="1760" y2="1048" stroke="#E3E6EC"/>')
text(40, 1080, "El flujo, paso a paso", 14.5, 600, INK)
flujo = [
    (1, STEP, "El estudiante escanea su carné en el tótem; el inspector usa la app solo para casos puntuales."),
    (2, STEP, "El webhook de WF1 valida el carné y registra «presente»."),
    (3, STEP, "A las 07:30, WF2 cruza la lista del curso y avisa por Telegram a cada familia."),
    (4, STEP, "La familia responde con texto, voz o foto; WF3 lo recibe."),
    (5, GEM, "Gemini extrae estudiante, fechas y motivo con un JSON Schema."),
    (6, STEP, "Reglas deterministas validan; si algo no cuadra, va a revisión del inspector."),
    (7, STEP, "WF4 pide aprobación al inspector (Send and Wait)."),
    (8, SUPA, "La decisión y la auditoría quedan en Postgres."),
    (9, SUPA, "Realtime actualiza el tablero del inspector y del tutor."),
]
for i, (n, c, t) in enumerate(flujo):
    y = 1104 + (i % 5) * 26
    x = 40 if i < 5 else 640
    step(x + 11, y - 5, n, c, 20)
    text(x + 30, y, t, 12.5, 400, INK)

text(1240, 1080, "Despliegue al fusionar a main", 14.5, 600, INK)
for i, (k, t) in enumerate([("D1", "supabase db push: migraciones primero"), ("D2", "API de n8n: PUT borrador y POST /publish"),
                            ("D3", "Prueba de humo contra producción"), ("D4", "Vercel publica la app y el tablero")]):
    y = 1104 + i * 26
    step(1251, y - 5, k, DEPLOY, 24)
    text(1272, y, t, 12.5, 400, INK)

text(640, 1234, "La IA solo extrae datos: las reglas validan y una persona aprueba. Si Gemini falla, el caso va a revisión manual;",
     12, 400, SUB)
text(640, 1250, "el registro en la puerta no depende de la IA. Problema: Ministerio de Educación, «Tiempo para Ser Docente» (2025). Datos del demo: sintéticos.",
     12, 400, SUB)
text(40, 1250, "Logos: Simple Icons (CC0).", 11.5, 400, SUB)

# ---------- defs ----------
mk = "".join(
    f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.6" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
    f'<path d="M0 1 L9 5 L0 9 z" fill="{col}"/></marker>' for col, mid in MARK.items())
defs = (f'<defs><filter id="tile" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.5" stdDeviation="1.5" '
        f'flood-color="#1B2333" flood-opacity="0.18"/></filter>{mk}</defs>')
font = ("<style>@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&amp;display=block');</style>")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Arquitectura de Pórtika">{font}{defs}{"".join(out)}</svg>')
open(OUT_SVG, "w", encoding="utf-8", newline="\n").write(svg)
open(OUT_HTML, "w", encoding="utf-8", newline="\n").write(
    f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#fff}}</style></head><body>{svg}</body></html>')
print("ok")
