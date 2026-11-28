# Contratos de Pórtika

Los acuerdos que conectan las piezas. Si alguien necesita cambiar uno, lo propone en un PR que toque este archivo **antes** de cambiar el código. Con esto cada persona construye su parte contra datos de prueba sin esperar a las demás.

Nombre del producto: **Pórtika** (la app web y el bot de Telegram).

## C0 · Convenciones

- Zona horaria: `America/Guayaquil`. Fechas `AAAA-MM-DD`; marcas de tiempo ISO 8601 con zona (`2026-01-12T07:14:03-05:00`).
- Códigos del dataset: estudiante `EST-###`, representante `REP-###`, curso `"8vo EGB"`, paralelo `"A"`.
- Fecha del demo: variable `FECHA_DEMO`. Por ejemplo `2026-01-12`, dentro del rango del dataset ficticio y en día hábil.
- Todo es sintético. Los únicos `chat_id` reales son los de los teléfonos del equipo y del jurado en el demo, y se borran después.

## C1 · Base de datos (Supabase Postgres)

Migraciones en `supabase/migrations/`. El seed se genera con `scripts/seed.py` desde el dataset ficticio y se guarda en `supabase/seed.sql`.

| Tabla | Columnas | Reglas |
| --- | --- | --- |
| `representantes` | `codigo text pk`, `nombre_ficticio text`, `telegram_chat_id bigint null` | `chat_id` se llena al vincular el bot (C4) |
| `estudiantes` | `codigo text pk`, `nombre_ficticio text`, `curso text`, `paralelo text`, `representante_codigo text fk` | Del dataset |
| `carnes` | `token text pk`, `estudiante_codigo text fk`, `activo boolean default true` | El QR del carné contiene **solo el token** (aleatorio, 16 caracteres o más); nunca el código del estudiante |
| `ingresos` | `id bigserial pk`, `estudiante_codigo text fk`, `fecha date`, `hora timestamptz`, `origen text check (origen in ('totem','app'))` | `unique (estudiante_codigo, fecha)`: un ingreso por día |
| `faltas` | `id bigserial pk`, `estudiante_codigo text fk`, `fecha date`, `estado text check (estado in ('injustificada','pendiente','justificada','rechazada'))` | `unique (estudiante_codigo, fecha)` |
| `justificativos` | `id bigserial pk`, `representante_codigo text fk`, `estudiante_codigo text fk null`, `tipo_entrada text check (tipo_entrada in ('texto','voz','foto'))`, `extraccion jsonb`, `validacion jsonb`, `estado text check (estado in ('pendiente','aprobado','rechazado','revision_manual'))`, `creado timestamptz default now()` | `extraccion` guarda la salida de C5 y `validacion` la de C6 |
| `auditoria` | `id bigserial pk`, `actor text`, `accion text`, `entidad text`, `entidad_id text`, `detalle jsonb`, `creado timestamptz default now()` | Solo inserción. Actor: `inspector:<chat_id>`, `sistema:WF1`… |
| `eventos_tablero` | `id bigserial pk`, `tipo text`, `curso text`, `paralelo text`, `creado timestamptz default now()` | **Sin datos personales.** Es lo único que el navegador escucha en tiempo real |

**Vista** `v_tablero_hoy` (curso, paralelo, presentes, ausentes, pendientes, justificadas) calculada para `FECHA_DEMO`.

**Seguridad:**
- RLS activado en todas las tablas.
- El rol `anon` (navegador) solo puede leer `v_tablero_hoy` y `eventos_tablero`.
- n8n usa la clave de servicio, que nunca sale de las credenciales de n8n.
- El tablero se suscribe a `eventos_tablero` y, ante cada evento, vuelve a leer `v_tablero_hoy`. Así ningún dato personal viaja al navegador.

**Realtime:** publicar solo `eventos_tablero` en `supabase_realtime`.

## C2 · Webhook de ingreso (tótem y app → WF1)

`POST {N8N_BASE_URL}/webhook/portika/ingreso`

Cabecera `X-Portika-Clave: <PORTIKA_CLAVE_DISPOSITIVO>`. Es un secreto compartido de los dispositivos de la puerta; si no coincide, la respuesta es 401.

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
  - `/start INSPECTOR-<clave>`: registra el chat del inspector en la variable `INSPECTOR_CHAT_ID` de n8n.
  - Texto, nota de voz o foto de un representante vinculado: va al flujo del justificativo (C5 y C6).
  - Mensaje de un chat no vinculado: «No encuentro tu registro; usa el enlace que te envió el colegio».
- La aprobación de WF4 usa **Send and Wait for Response**. Según la documentación de n8n, la aprobación dentro del chat comparte el webhook del Telegram Trigger en versiones compatibles. **Hay que comprobarlo en la instancia.** Plan B: aprobación por enlace (opción del mismo nodo).

## C5 · Extracción con Gemini (WF3)

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
| R3 | Ninguna fecha es futura y todas están dentro de `PLAZO_DIAS` hábiles (por defecto 3) | `rechazado`, con aviso a la familia |
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
- Los casos en `revision_manual` también llegan al inspector, marcados como tales.

## C8 · Errores (WF0)

Error Trigger, configurado como workflow de error de WF1 a WF4. Envía al chat del equipo (`EQUIPO_CHAT_ID`) el nombre del workflow, el nodo que falló y el enlace a la ejecución.

## C9 · Variables y secretos

| Dónde | Nombre | Para qué |
| --- | --- | --- |
| Front (`.env`, público) | `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_N8N_BASE_URL` | Tablero y tótem |
| Dispositivo de la puerta | `PORTIKA_CLAVE_DISPOSITIVO` | Cabecera de C2 y C3; se ingresa una vez en la tablet y no va al repo |
| Credenciales de n8n | Telegram, Gemini y Postgres de Supabase (clave de servicio) | Nunca en el repo ni en los JSON exportados |
| Variables de n8n | `FECHA_DEMO`, `PLAZO_DIAS`, `INSPECTOR_CHAT_ID`, `EQUIPO_CHAT_ID`, `PORTIKA_CLAVE_DISPOSITIVO` | Configuración de los workflows |
| GitHub Secrets | `N8N_API_KEY`, `N8N_BASE_URL`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_PROJECT_ID`, `VERCEL_TOKEN` | Despliegue (D1–D4) |

## C10 · Estructura del repo

```
supabase/migrations/*.sql   esquema (C1)
supabase/seed.sql           generado por scripts/seed.py
scripts/seed.py             dataset ficticio → seed.sql y tokens de carné
n8n/0N-nombre.json          un archivo por workflow, sin pinData ni credenciales
src/web/                    tótem, app del inspector y tablero (Vite)
tests/                      reglas C6 y validaciones de los JSON
```

**Nombres de archivo de los workflows:**
- `00-errores.json`
- `01-ingreso.json`
- `02-ausencias.json`
- `03-justificativo.json`
- `04-aprobacion.json`
