import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

import segno

RAIZ = Path(__file__).resolve().parents[1]
COLUMNAS_ESTUDIANTE = ("codigo", "nombre_ficticio", "curso", "paralelo", "representante_codigo")
ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
ESTADOS_FALTA = {"falta_injustificada": "injustificada", "falta_justificada": "justificada"}


def leer_csv(ruta):
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def generar_tokens(estudiantes):
    azar = random.Random(20260112)
    tokens = {}
    usados = set()
    for codigo, *_ in estudiantes:
        while True:
            token = "".join(azar.choice(ALFABETO) for _ in range(16))
            if token not in usados:
                tokens[codigo] = token
                usados.add(token)
                break
    return tokens


def elegir_demo(estudiantes, familias):
    hermanos = next(familias[codigo] for codigo in sorted(familias) if len(familias[codigo]) >= 2)
    demo = hermanos[:2]
    demo.extend(e for e in estudiantes if e[2:4] == ("8vo EGB", "A") and e not in hermanos[:2])
    if len(demo) < 10:
        raise ValueError("El dataset no alcanza para seleccionar 10 estudiantes del demo")
    return demo[:10]


def literal_sql(valor):
    return "'" + valor.replace("'", "''") + "'"


def bloques_insert(tabla, columnas, filas):
    for inicio in range(0, len(filas), 500):
        valores = ",\n".join(
            "(" + ", ".join(map(literal_sql, fila)) + ")" for fila in filas[inicio:inicio + 500]
        )
        yield f"insert into public.{tabla} ({', '.join(columnas)}) values\n{valores}\non conflict do nothing;\n"


def escribir_seed(estudiantes, familias, tokens, faltas):
    representantes = [
        (codigo, "Familia " + " ".join(hijos[0][1].split()[-2:]))
        for codigo, hijos in sorted(familias.items())
    ]
    representantes.append(("REP-999", "Representante técnico"))
    tecnico = ("EST-999", "Estudiante técnico", "PRUEBA", "A", "REP-999")
    carnes = [(token, codigo) for codigo, token in tokens.items()]
    carnes.append(("HUMO-0000000000000", "EST-999"))
    tablas = [
        ("representantes", ("codigo", "nombre_ficticio"), representantes),
        ("estudiantes", COLUMNAS_ESTUDIANTE, [*estudiantes, tecnico]),
        ("carnes", ("token", "estudiante_codigo"), carnes),
        ("faltas", ("estudiante_codigo", "fecha", "estado"), faltas),
    ]
    with (RAIZ / "supabase/seed.sql").open("w", encoding="utf-8", newline="\n") as archivo:
        archivo.write("begin;\n")
        for tabla, columnas, filas in tablas:
            archivo.writelines(bloques_insert(tabla, columnas, filas))
        archivo.write("commit;\n")


def dibujar_carne(estudiante, token, x, y):
    codigo, nombre, curso, paralelo, _ = estudiante
    qr = segno.make_qr(token, error="m")
    # El borde blanco de cuatro módulos queda libre alrededor del QR.
    comandos = [f"0.75 G 0.5 w {x} {y} 264 144 re S", "0 g"]
    for fila, modulos in enumerate(qr.matrix_iter(border=4)):
        for columna, oscuro in enumerate(modulos):
            if oscuro:
                comandos.append(f"{x + 9 + 3 * columna} {y + 114 - 3 * fila} 3 3 re f")
    for texto, alto, tamano in (
        (nombre, 103, 10), (codigo, 85, 10), (f"{curso} {paralelo}", 67, 10),
        ("Pórtika · dato sintético", 43, 9),
    ):
        # Las cadenas hexadecimales evitan escapes para paréntesis y barras.
        cadena = texto.encode("cp1252").hex()
        comandos.append(f"BT /F1 {tamano} Tf {x + 113} {y + alto} Td <{cadena}> Tj ET")
    return "\n".join(comandos)


def escribir_pdf(demo, tokens):
    contenido = "\n".join(
        dibujar_carne(e, tokens[e[0]], 27 + (i % 2) * 278, 674 - (i // 2) * 161)
        for i, e in enumerate(demo)
    ).encode("ascii")
    contenido += b"\n"
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        f"<< /Length {len(contenido)} >>\nstream\n".encode("ascii") + contenido + b"endstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    posiciones = []
    for numero, objeto in enumerate(objetos, start=1):
        posiciones.append(len(pdf))
        pdf.extend(f"{numero} 0 obj\n".encode("ascii") + objeto + b"\nendobj\n")
    xref = len(pdf)
    total = len(objetos) + 1
    pdf.extend(f"xref\n0 {total}\n0000000000 65535 f \n".encode("ascii"))
    for posicion in posiciones:
        pdf.extend(f"{posicion:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {total} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    (RAIZ / "data/carnes_demo.pdf").write_bytes(pdf)


def main():
    parser = argparse.ArgumentParser(description="Genera el seed sintético y los carnés del demo")
    parser.add_argument("--dataset", required=True, type=Path)
    carpeta = parser.parse_args().dataset
    estudiantes = sorted(
        tuple(fila[columna] for columna in COLUMNAS_ESTUDIANTE)
        for fila in leer_csv(carpeta / "estudiantes.csv")
    )
    familias = defaultdict(list)
    for estudiante in estudiantes:
        familias[estudiante[4]].append(estudiante)
    faltas = [
        (fila["codigo_estudiante"], fila["fecha"], ESTADOS_FALTA[fila["estado"]])
        for fila in leer_csv(carpeta / "asistencia.csv")
        if fila["estado"] in ESTADOS_FALTA
    ]
    tokens = generar_tokens(estudiantes)
    demo = elegir_demo(estudiantes, familias)
    escribir_seed(estudiantes, familias, tokens, faltas)
    escribir_pdf(demo, tokens)
    print("Estudiantes del demo:")
    for codigo, nombre, curso, paralelo, representante in demo:
        print(f"{codigo} | {nombre} | {curso} {paralelo} | {representante}")


if __name__ == "__main__":
    main()
