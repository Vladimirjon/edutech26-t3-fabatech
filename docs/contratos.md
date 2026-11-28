# Contratos de Pórtika

Los acuerdos que conectan las piezas. Si alguien necesita cambiar uno, lo propone en un PR que toque este archivo **antes** de cambiar el código. Con esto cada persona construye su parte contra datos de prueba sin esperar a las demás.

Nombre del producto: **Pórtika** (la app web y el bot de Telegram).

## C0 · Convenciones

- Zona horaria: `America/Guayaquil`. Fechas `AAAA-MM-DD`; marcas de tiempo ISO 8601 con zona (`2026-01-12T07:14:03-05:00`).
- Códigos del dataset: estudiante `EST-###`, representante `REP-###`, curso `"8vo EGB"`, paralelo `"A"`.
- Fecha del demo (`FECHA_DEMO`): `2026-01-12` (lunes). Los workflows la leen de la fila `fecha_demo` de `configuracion` (C9). Es un día **sin datos**: el historial del dataset llega hasta el 19-dic-2025. Así el demo arranca limpio y todo lo de ese día lo crean el tótem y WF2.
- Las pruebas automáticas fijan su propia fecha y no dependen de `FECHA_DEMO`.
- Todo es sintético. Los únicos `chat_id` reales son los de los teléfonos del equipo y del jurado en el demo, y se borran después.

## C1 · Base de datos (Supabase Postgres)

Migraciones en `supabase/migrations/`. El seed se genera con `scripts/seed.py` desde el dataset ficticio y se guarda en `supabase/seed.sql`. Esto es lo que carga:
- estudiantes y representantes;
- un carné activo por estudiante;
- el historial de `asistencia.csv` como faltas: `falta_injustificada` se guarda como `injustificada` y `falta_justificada` como `justificada`. Los `presente` y los `atraso` no generan fila.

- un estudiante técnico `EST-999` (curso `PRUEBA`, excluido de `v_tablero_hoy`) con el carné `HUMO-0000000000000` para la prueba de humo del despliegue.

Los 10 estudiantes del demo no tienen ingresos ni faltas en `FECHA_DEMO`, porque ese día no tiene datos.

Además, `scripts/seed.py` genera `data/carnes_demo.pdf` con los QR de 10 estudiantes para el demo. Los demás carnés quedan solo como datos.

| Tabla | Columnas | Reglas |
| --- | --- | --- |
| `representantes` | `codigo text pk`, `nombre_ficticio text`, `telegram_chat_id bigint null` | `chat_id` se llena al vincular el bot (C4) |
| `estudiantes` | `codigo text pk`, `nombre_ficticio text`, `curso text`, `paralelo text`, `representante_codigo text fk` | Del dataset |
| `carnes` | `token text pk`, `estudiante_codigo text fk`, `activo boolean default true` | El QR del carné contiene **solo el token** (aleatorio, 16 caracteres o más); nunca el código del estudiante |
| `ingresos` | `id bigserial pk`, `estudiante_codigo text fk`, `fecha date`, `hora timestamptz`, `origen text check (origen in ('totem','app'))` | `unique (estudiante_codigo, fecha)`: un ingreso por día |
| `faltas` | `id bigserial pk`, `estudiante_codigo text fk`, `fecha date`, `estado text check (estado in ('injustificada','pendiente','justificada','rechazada'))` | `unique (estudiante_codigo, fecha)` |
| `justificativos` | `id bigserial pk`, `representante_codigo text fk`, `estudiante_codigo text fk null`, `tipo_entrada text check (tipo_entrada in ('texto','voz','foto'))`, `mensaje_original text`, `foto_file_id text null`, `extraccion jsonb`, `validacion jsonb`, `estado text check (estado in ('pendiente','aprobado','rechazado','revision_manual'))`, `creado timestamptz default now()` | `mensaje_original`: el texto o la transcripción. `foto_file_id`: el `file_id` de Telegram (la foto no se guarda en la base). `extraccion` guarda la salida de C5 y `validacion` la de C6 |
| `auditoria` | `id bigserial pk`, `actor text`, `accion text`, `entidad text`, `entidad_id text`, `detalle jsonb`, `creado timestamptz default now()` | Solo inserción. Actor: `inspector:<chat_id>`, `sistema:WF1`… |
| `eventos_tablero` | `id bigserial pk`, `tipo text`, `curso text`, `paralelo text`, `creado timestamptz default now()` | **Sin datos personales.** Es lo único que el navegador escucha en tiempo real |
| `configuracion` | `clave text pk`, `valor text` | Configuración de los workflows (C9). Las filas se cargan a mano una vez; solo `inspector_chat_id` la escribe n8n (C4) |

**Vista** `v_tablero_hoy` (curso, paralelo, presentes, ausentes, pendientes, justificadas, sin_contacto) calculada para `FECHA_DEMO`. La fecha está fija en la vista y se cambia con una migración.

**Seguridad:**
- RLS activado en todas las tablas.
- El rol `anon` (navegador) solo puede leer `v_tablero_hoy` y `eventos_tablero`.
- n8n se conecta como `postgres` con la contraseña de la base de datos, por el Session pooler y con SSL. Esa contraseña nunca sale de la credencial de n8n.
- El tablero se suscribe a `eventos_tablero` y, ante cada evento, vuelve a leer `v_tablero_hoy`. Así ningún dato personal viaja al navegador.

**Realtime:** publicar solo `eventos_tablero` en `supabase_realtime`.

**Escrituras atómicas:** cada paso que toca varias tablas se hace con **una sola sentencia SQL con CTE** en un único nodo Postgres. Por ejemplo: insertar el ingreso, el evento y la auditoría. Así no quedan escrituras a medias.

## C2 · Webhook de ingreso (tótem y app → WF1)

`POST {N8N_BASE_URL}/webhook/portika/ingreso`

Cabecera `X-Portika-Clave: <PORTIKA_CLAVE_DISPOSITIVO>`. Es un secreto compartido de los dispositivos de la puerta; si no coincide, la respuesta es 401.

**CORS:** el navegador envía una cabecera propia, así que hace un `OPTIONS` previo. El webhook debe permitir el origen del dominio de Vercel y la cabecera `X-Portika-Clave` (opción de orígenes permitidos del nodo Webhook; **verificar en la instancia**).

```json
{ "carne_token": "k3P9xQ2mVt7LwZ4a", "origen": "totem", "dispositivo": "puerta-principal", "escaneado_en": "2026-01-12T07:14:03-05:00" }
```

Respuestas (nodo Respond to Webhook, meta de menos de 2 s):

| Código | Cuerpo | Qué muestra el tótem |
| --- | --- | --- |
| 200 | `{ "estado": "registrado", "estudiante": { "codigo": "EST-014", "nombre_ficticio": "…", "curso": "9no EGB", "paralelo": "A" }, "hora": "…" }` | Verde con el nombre |
| 200 | `{ "estado": "duplicado", "estudiante": { … }, "hora_original": "…" }` | Ámbar: «Ya registrado a las 07:02» |
| 404 | `{ "estado": "carne_desconocido" }` | Rojo: «Carné no válido, acércate a inspección» |
| 401 | `{ "estado": "no_autorizado" }` | Error de configuración del dispositivo |

Efectos de un `registrado`:
- inserta en `ingresos`;
- inserta un evento `ingreso` en `eventos_tablero`;
- escribe en `auditoria` con actor `sistema:WF1`.

**Entrada en la puerta.** El lector QR USB funciona como teclado: escribe el token y pulsa Enter sobre un campo con foco permanente. Es la entrada principal porque funciona en cualquier navegador. La cámara es la alternativa; el soporte de `BarcodeDetector` depende del navegador y del sistema operativo, así que hay que **verificarlo en la tablet del demo** antes de depender de él.

## C3 · Cierre del ingreso (WF2)

- Disparadores:
  - Schedule a las 07:30 (`America/Guayaquil`), de lunes a viernes;
  - para el demo, `POST {N8N_BASE_URL}/webhook/portika/cierre` con `{ "fecha": "AAAA-MM-DD" }` y la misma cabecera de C2.
- Para cada estudiante sin ingreso en esa fecha:
  - inserta una falta `injustificada`, sin duplicar si se repite el cierre;
  - inserta un evento `ausencia`.
- Agrupa las faltas por representante (los hermanos van en un solo mensaje). Si el representante tiene `telegram_chat_id`, envía:

> «Hola, en Pórtika no registramos el ingreso de EST-014 hoy 12 de enero. Si faltó por un motivo, respóndenos aquí con un texto, una nota de voz o la foto del justificativo.»

- Si un representante no tiene `chat_id`, la falta aparece como «sin contacto» en el tablero.
- Respuesta: `{ "faltas_creadas": 12, "mensajes_enviados": 9, "sin_contacto": 3 }`.

## C4 · Bot de Telegram «Pórtika»

- Dos bots: **Pórtika** para el demo y **Pórtika dev** para desarrollo. Telegram admite un solo webhook por bot, y la URL de prueba pisa la de producción.
- **Un único Telegram Trigger por bot**, ubicado en WF3, que enruta por tipo de mensaje:
  - `/start REP-014` (enlace `t.me/<bot>?start=REP-014`): guarda el `chat_id` en `representantes` y responde «Listo, recibirás aquí los avisos de asistencia».
  - `/start INSPECTOR-<PORTIKA_CLAVE_INSPECTOR>`: si la clave coincide, guarda el chat del inspector. La guarda en la fila `inspector_chat_id` de `configuracion`. Si el vínculo falla, esa fila se carga a mano.
  - Texto, nota de voz o foto de un representante vinculado: va al flujo del justificativo (C5 y C6).
  - Mensaje de un chat no vinculado: «No encuentro tu registro; usa el enlace que te envió el colegio».
- La aprobación de WF4 usa **Send and Wait for Response**. Según la documentación de n8n, la aprobación dentro del chat comparte el webhook del Telegram Trigger en versiones compatibles. **Hay que comprobarlo en la instancia.** Plan B: aprobación por enlace (opción del mismo nodo).

## C5 · Extracción con Gemini (WF3)

Modelo: **Gemini 3.5 Flash Lite** en el nivel gratis de AI Studio (500 llamadas al día; Gemini 3.8 Flash solo da 20), con la credencial `Gemini Portika`. Probarlo con una foto y una nota de voz antes de fijarlo.

Entrada: el texto, la transcripción de la voz o la imagen, junto con el contexto que se le pasa al modelo:
- los hijos del representante (código y curso);
- sus faltas en estado `injustificada` o `pendiente`.

Salida forzada con Structured Output Parser y este JSON Schema:

```json
{
  "type": "object",
  "required": ["estudiante_codigo", "fechas", "motivo", "resumen", "confianza"],
  "properties": {
    "estudiante_codigo": { "type": ["string", "null"], "pattern": "^EST-\\d{3}$" },
    "fechas": { "type": "array", "items": { "type": "string", "format": "date" }, "minItems": 1 },
    "motivo": { "type": "string", "enum": ["salud", "calamidad_domestica", "transporte", "tramite", "otro"] },
    "resumen": { "type": "string", "maxLength": 200 },
    "confianza": { "type": "number", "minimum": 0, "maximum": 1 },
    "tiene_documento": { "type": "boolean" }
  }
}
```

Si Gemini falla, se agota el tiempo o devuelve algo que no cumple el esquema, el justificativo queda en `revision_manual` con el mensaje original y el flujo sigue.

## C6 · Reglas deterministas (nodo Code en WF3)

Entrada: la salida de C5, el `chat_id` y `FECHA_DEMO`. Salida guardada en `justificativos.validacion`:

```json
{ "valido": true, "destino": "aprobacion", "reglas": [{ "id": "R1", "ok": true, "detalle": "…" }] }
```

| Regla | Qué comprueba | Si falla |
| --- | --- | --- |
| R1 | El estudiante pertenece al representante del chat. Si `estudiante_codigo` es `null` y hay **un solo** hijo, se usa ese | `revision_manual` |
| R2 | Cada fecha corresponde a una falta `injustificada` o `pendiente` de ese estudiante | `revision_manual` |
| R3 | Ninguna fecha es futura y todas están dentro de `plazo_dias` días hábiles (fila de `configuracion`; por defecto 3) | `rechazado`, con aviso a la familia |
| R4 | `confianza` ≥ 0,6 | `revision_manual` |

Si todas pasan, `destino = "aprobacion"` y las faltas cubiertas pasan a `pendiente`. Las reglas se prueban con `node:test` sobre el `jsCode` extraído del JSON del workflow (ver #5).

## C7 · Aprobación (WF4)

- Recibe el `id` del justificativo (subworkflow llamado por WF3 con Execute Workflow).
- Envía al chat del inspector un resumen con el estudiante, el curso, las fechas, el motivo, el resultado de cada regla y la foto si la hay. Los botones son **Aprobar** y **Rechazar**.
- **Aprobar:**
  - las faltas pasan a `justificada` y el justificativo a `aprobado`;
  - se escribe en `auditoria` (actor `inspector:<chat_id>`) y se inserta el evento `justificada`;
  - la familia recibe «Tu justificativo fue aprobado».
- **Rechazar:** las faltas vuelven a `injustificada`, el justificativo pasa a `rechazado`, se escribe en auditoría y se avisa a la familia.
- Sin respuesta en 24 h: el justificativo queda `pendiente`.
- Si un caso en `revision_manual` no tiene `estudiante_codigo` o `fechas`, al aprobar o rechazar solo se actualizan `justificativos` y `auditoria`. No se tocan las `faltas` ni se emiten eventos: el inspector corrige la falta a mano.
- Los casos en `revision_manual` también llegan al inspector, marcados como tales.

## C7b · Prueba de humo (D3)

Después de publicar, el CD hace un POST al webhook C2 con el carné `HUMO-0000000000000` y la cabecera de GitHub Secrets. Acepta `registrado` o `duplicado`, porque el segundo despliegue del día devuelve `duplicado`. Luego comprueba con la API de Supabase que existe la fila de `EST-999` en `ingresos`. Si falla, el job falla.

## C8 · Errores (WF0)

Error Trigger, configurado como workflow de error de WF1 a WF4. Envía al chat del equipo (fila `equipo_chat_id` de `configuracion`) el nombre del workflow, el nodo que falló y el enlace a la ejecución.

## C9 · Configuración y secretos

| Dónde | Nombre | Para qué |
| --- | --- | --- |
| Front (`.env`, público) | `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_N8N_BASE_URL` | Tablero y tótem |
| Dispositivo de la puerta | `PORTIKA_CLAVE_DISPOSITIVO` | Cabecera de C2 y C3; se ingresa una vez en la tablet y no va al repo |
| Credenciales de n8n | `Telegram Portika`, `Telegram Portika dev`, `Gemini Portika` y `Postgres Portika` (contraseña de la base de datos, Session pooler, SSL `Require` con el certificado CA de Supabase) | Nunca en el repo ni en los JSON exportados |
| Tabla `configuracion` (Supabase) | `fecha_demo`, `plazo_dias`, `equipo_chat_id`, `portika_clave_dispositivo`, `portika_clave_inspector`; `inspector_chat_id` la escribe n8n (C4) | Configuración de los workflows; se lee con un nodo Postgres. Se carga a mano, nunca en `seed.sql` |
| GitHub Secrets | `N8N_API_KEY`, `N8N_BASE_URL`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_PROJECT_ID`, `VERCEL_TOKEN`, `PORTIKA_CLAVE_DISPOSITIVO` | Despliegue (D1–D4) y prueba de humo |

Las Variables de n8n (`$vars`) no están en el plan Starter: la instancia muestra «Available on Pro plan». Por eso la configuración vive en `configuracion`, que `anon` no puede leer.

## C10 · Estructura del repo

```
supabase/migrations/*.sql   esquema (C1)
supabase/seed.sql           generado por scripts/seed.py
scripts/seed.py             dataset ficticio → seed.sql y tokens de carné
n8n/0N-nombre.json          un archivo por workflow, sin pinData ni credenciales
n8n/ids.json                mapa archivo → ID del workflow en la instancia (no es secreto)
src/web/                    tótem, app del inspector y tablero (Vite)
tests/                      reglas C6 y validaciones de los JSON
```

**Nombres de archivo de los workflows:**
- `00-errores.json`
- `01-ingreso.json`
- `02-ausencias.json`
- `03-justificativo.json`
- `04-aprobacion.json`
