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
person(316, 112, "Inspector general", "controla la puerta y aprueba")
person(710, 112, "Familia", "representante del estudiante")
person(1135, 112, "Docente tutor", "ve el curso sin tomar lista")

# ---------- B · interfaces ----------
box(232, 246, 200, 84, "App del inspector", ["Escáner QR del carné", "en el celular · Vercel"], accent=FLOW)
box(590, 246, 240, 84, "Bot de Telegram", ["Familias e inspector:", "texto, voz, fotos y botones"], accent=FLOW)
box(990, 246, 220, 84, "Tablero en vivo", ["Ingresos, ausentes, pendientes", "y horas docentes ahorradas"], accent=DATA)

# ---------- C · n8n ----------
add(f'<rect x="224" y="372" width="926" height="136" rx="8" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 4"/>')
box(236, 404, 160, 90, "WF1 · Ingreso", ["Valida el carné y", "registra «presente»"])
box(412, 404, 160, 90, "WF2 · Ausencias", ["Cruza la lista del", "curso con los ingresos"])
box(588, 404, 184, 90, "WF3 · Justificativo", ["Recibe texto, voz o foto", "y pide la extracción"])
box(788, 404, 172, 90, "WF4 · Aprobación", ["Send and Wait al", "inspector en Telegram"])
box(976, 404, 160, 90, "WF0 · Errores", ["Error Trigger: avisa", "al equipo si algo falla"], stroke="#9AA1AE")

# ---------- D · IA y reglas ----------
box(540, 552, 180, 84, "Gemini", ["Texto, voz, imagen →", "JSON con esquema"], stroke=AI, title_fill=AI, accent=AI)
box(772, 552, 180, 84, "Reglas deterministas", ["Representante ↔ estudiante,", "fechas = faltas reales, plazo"])
box(1004, 552, 136, 84, "Revisión manual", ["Si la IA falla o", "algo no valida"], stroke="#9AA1AE")

# ---------- E · datos ----------
add(f'<rect x="224" y="678" width="1002" height="146" rx="8" fill="none" stroke="{DATA}" stroke-width="1.4" stroke-dasharray="6 4"/>')
add(f'<rect x="312" y="712" width="600" height="98" rx="6" fill="#FFFFFF" stroke="{DATA}" stroke-width="1.25" filter="url(#lift)"/>')
text(326, 736, "Postgres", 14.5, 600, DATA)
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
box(1264, 376, 302, 90, "CI en cada PR", ["Estructura, secretos, JSON de n8n,", "pruebas · preview de Vercel"], stroke=DEPLOY)
path("M1415 358 L1415 372", DEPLOY, 1.6, marker="arrg")
path("M1415 466 L1415 482", DEPLOY, 1.6, marker="arrg")
add(f'<rect x="1264" y="486" width="302" height="334" rx="6" fill="#FFFFFF" stroke="{DEPLOY}" stroke-width="1.25" filter="url(#lift)"/>')
text(1278, 512, "Al fusionar a main", 14.5, 600, INK)
steps = [
    ("a", "Vercel publica app y tablero", "producción desde main"),
    ("b", "n8n API: PUT borrador", "y luego POST /publish"),
    ("c", "Prueba de humo", "webhook de producción + fila en BD"),
    ("d", "supabase db push", "migraciones de la base"),
]
for i, (k, t1, t2) in enumerate(steps):
    y0 = 540 + i * 70
    add(f'<rect x="1278" y="{y0}" width="22" height="22" rx="4" fill="#F1F2F4" stroke="#C9CDD4"/>')
    text(1289, y0 + 15.5, k, 12, 600, DEPLOY, "middle", family="mono")
    text(1310, y0 + 15, t1, 13, 600, INK)
    text(1310, y0 + 33, t2, 11.5, 400, SUB)

# despliegues (gris punteado)
path("M1264 551 L1218 551 L1218 300 L1212 300", DEPLOY, 1.5, "5 4", "arrg")
path("M1264 621 L1200 621 Q1192 613 1184 621 L1152 621 L1152 470", DEPLOY, 1.5, "5 4", "arrg")
path("M1264 761 L1228 761", DEPLOY, 1.5, "5 4", "arrg")

# ---------- flujo del demo (numerado) ----------
path("M316 200 L316 244")                       # 1 inspector -> app
badge(338, 222, 1)
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
path("M610 246 L610 122 L340 122")
badge(874, 352, 7)
label(352, 114, "aprueba o rechaza con un toque")
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
    "El inspector escanea el QR del carné en la puerta.",
    "La app envía el escaneo a WF1, que registra «presente».",
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
    ("1–2", "No toma lista en cada clase."),
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
