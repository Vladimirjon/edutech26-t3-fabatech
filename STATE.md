# STATE.md · Dónde está el trabajo

_Última actualización: sáb 28-nov-2026 10:00 (UTC-5)._

## Hecho

- Repo creado a las 18:02 con la estructura obligatoria de la Guía del hacker §4.2 y un CI de estructura. Colaboradores invitados.
- Lectura de las guías, de la rúbrica y del dataset ficticio. Las notas están fuera del repo (`../prep/`) y se declaran en `PRIOR_WORK.md`.
- Decisión del equipo: **track T3**, sin marco legal en el producto.

## En curso

- Investigación verificada (con fuentes) de problemas institucionales graves en Ecuador, para elegir el problema.
- Verificación en la documentación oficial de la arquitectura: n8n Cloud Starter, CI/CD de workflows, Supabase y Gemini.

## Pendiente inmediato

- **Checkpoint 1, vie 19:00**: README con problema, usuario, evidencia y arquitectura, más `docs/arquitectura.png`.

## Al 27-nov 20:10

- El producto se llama **Pórtika** (app y bot).
- Contratos entre piezas en `docs/contratos.md`.
- Issues #3 a #16 redactados a fondo (Codex), revisados (Antigravity) y verificados (Claude). Nuevo #19: aprovisionamiento.
- Lección: Antigravity inventó URLs en una investigación web; sus fuentes se verifican siempre antes de usarlas.

## Al 27-nov 21:00 · #3 listo en local, sin commit

- Rama `feat/03-esquema-seed` con el esquema (2 migraciones), `scripts/seed.py`, `supabase/seed.sql`, `data/carnes_demo.pdf` y `scripts/probar_esquema.py`. **Sin commit**: se sube en un solo commit y un PR con squash.
- Probado: `python scripts/probar_esquema.py` pasa en Postgres 15.8 con roles simulados (conteos, duplicados, auditoría solo de inserción, `anon` sin acceso a tablas, vista con datos, Realtime). El seed y el PDF salen idénticos al regenerarlos.
- **Aplicado en Supabase real** (proyecto `portika`, ref `odbmgadayskuaqyvluyp`, us-east-2, plan Free) con `npx supabase@2.122.1 db push --linked --include-seed`. Verificado por la API REST: 241 estudiantes, 205 representantes, 241 carnés, 1313 faltas, 0 ingresos y `configuracion` vacía. `anon` recibe 401 en las tablas y lee `v_tablero_hoy` (12 filas) y `eventos_tablero`. La publicación de Realtime se aplicó sin error; falta probarla desde el tablero (#11).
- El proyecto se creó con «Grant API access to new tables» y «RLS automático» activados. La migración quita los permisos a `anon` y `authenticated`; `service_role` los conserva, y la prueba de humo (C7b) los necesita.
- El linter de Supabase avisará de que `v_tablero_hoy` corre con los permisos del dueño: es intencional.
- Contrato C1: `v_tablero_hoy` suma `sin_contacto`; si hay ingreso, la falta del mismo día no cuenta.
- El dataset no está en el repo: el zip va en `--dataset` (ver `data/README.md`).

## Decisiones tomadas

| Decisión | Motivo |
| --- | --- |
| Repo en la cuenta `Vladimirjon` | Instrucción verbal de la organización (vie ~18:00). La guía escrita decía organización `eight-academy-hackathon` |
| n8n Cloud Starter, una sola cuenta del equipo | Código promocional de la organización (correo del vie 17:26: "activen UNA sola cuenta por equipo") |
| Tag único `entrega` | Guía del hacker §6 |
| `main` protegida: PR obligatorio, CI `estructura` en verde, sin force push ni borrado, también para admins; 0 aprobaciones | El repo es público, así que GitHub Free lo permite. 0 aprobaciones para que el dueño del PR pueda fusionar sin esperar a nadie |

## Aprendido

- La API pública de n8n no existe en la prueba gratis de Cloud, pero sí en Starter (docs.n8n.io/api).
- Telegram admite un solo webhook por bot: las URL de prueba y producción se pisan.

## Al 28-nov 06:45 · instancia, credenciales y WF1

Hecho:
- #4 cerrado por Brandon con evidencia (comentario de cierre): publicación por API (PUT y publish con 200). `tmp-smoke-test` ya está borrado.
- Credenciales en el proyecto Portika de n8n: `Postgres Portika` (Session pooler, SSL con el certificado CA de Supabase; conexión probada), `Gemini Portika` (AI Studio, nivel gratis, sin facturación), `Telegram Portika` y `Telegram Portika dev`.
- Las Variables de n8n son solo del plan Pro: la configuración vive en la tabla `configuracion` (C9). Cargadas `fecha_demo`, `plazo_dias` y las dos claves (generadas en la base); `inspector_chat_id` la escribe WF3. La clave del dispositivo se rotó el 28-nov tras exponerse en el chat.
- GitHub Secrets: `N8N_API_KEY`, `N8N_BASE_URL`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_PROJECT_ID` y `PORTIKA_CLAVE_DISPOSITIVO` (valor rotado). `PORTIKA_CLAVE_INSPECTOR` se borró porque nada lo usa. `VERCEL_TOKEN` no hace falta.
- Vercel: proyecto `portika` (Hobby) conectado al repo, con las 3 variables `VITE_*` (la clave de Supabase es la publishable) y dominio `https://portika.vercel.app`. Sus builds fallan hasta que exista `src/web`; decisión: no usar "Ignored Build Step", se ajusta con Jorge cuando suba el front (cambiar la carpeta raíz a `src/web`).
- #7 WF1 · Ingreso publicado (id `2n7b6lYPCNvRyc7e`, PR #24). Consulta probada en Postgres 15.8 (401 y 404 sin escrituras, registrado, duplicado, 6 escaneos simultáneos → una sola fila) y en producción con el carné de humo (`duplicado`, hora con `-05:00`).
- #9, parte de Johann (PR #23): reglas C6 en `n8n/codigo/c6-reglas.js` (se pegan en el nodo Code «Reglas C6»), pruebas en `tests/c6-reglas.test.mjs` y prompts en `docs/prompts-wf3.md`. R3 manda (fecha futura o fuera de plazo → `rechazado`, como C6) y si R2 falla `fechas` sale vacía para que C7 no reabra faltas justificadas. Prompts probados en AI Studio con texto, foto y voz.
- Issues #5, #6 y #19 actualizados con estos cambios; comentarios de estado en #9 y #19.

Reparto hasta el ensayo de las 10:00:
- Brandon: WF2 (#8) → WF4 (#10) → WF0 (#12), con WF1 como modelo de estilo.
- Jorge: parte de CI del PR #20 (hoy las pruebas `node --test` solo corren en local) → puerta (#6) contra WF1 → tablero (#11).
- Johann: flujo de WF3 en n8n (#9) → ahorro y AI_USAGE (#13) → guion (#14).

Pendiente o sin verificar:
- CORS de WF1 desde `portika.vercel.app` y la meta de menos de 2 s (se prueba con #6).
- WF2, WF4 y WF0 sin terminar; front sin empezar.
- Probar un mensaje de cada bot y pasar los workflows a Pórtika antes de #16 (#19).
- `AI_USAGE.md` sin lo del 28-nov (#13).
- R3 no descuenta feriados (atajo anotado en el código; suficiente para el demo del 12-ene).

## Al 28-nov 09:40 · WF3 publicado (#9, rama `feat/09-wf3-flujo`)

Hecho:
- WF3 · Justificativo publicado (id `GhRiOqysx7IGKjK4`). Telegram Trigger → vínculo de representante e inspector (C4) → contexto en una consulta → texto, voz (transcripción con Gemini) o foto → extracción con Gemini 3.5 Flash Lite y Parser C5 → «Reglas C6» → guardado con una sola sentencia CTE → «Redactar respuesta» → respuesta a la familia. «Enviar a WF4» queda desactivado.
- Probado: `node --test` 39/39; las 4 consultas en Postgres 15.8 con migraciones y seed (vínculos, clave del inspector, contexto, guardado con aprobación, rechazo y revisión manual, evento `pendiente`); y en producción desde un teléfono con REP-999 (vínculo de ambos roles, texto, voz, foto y rechazo). Datos de prueba borrados después; el chat de Johann queda como `inspector_chat_id`.
- Mensajes cálidos y personalizados sin IA (`n8n/codigo/wf3-respuesta.js`): nombre del hijo, fecha en palabras, motivo y saludo variable. Textos fijos en C4.
- Cuando C6 da `destino = aprobacion` (WF3 no aprueba: eso lo hace WF4), WF3 pasa las faltas a `pendiente` e inserta un evento `pendiente` (curso y paralelo) para refrescar el tablero (C6).
- Clave del inspector rotada en la base (quedó visible en una captura del chat).

Decisiones:
- Un chat = un representante: el último `/start REP-###` gana.
- **Credenciales de Telegram:** el id `uCJxcnNOFfvYnRgN` tiene el token del bot del demo (@portika_edutech_bot) y Johann la renombró a «Telegram Portika». WF3 ya usa el bot del demo; Pórtika dev queda sin uso y nadie sabe qué token tiene `duIeqLZEdhdKH4TJ` («Telegram Portika dev»). Las descripciones de ambas siguen cruzadas. **WF2 y WF4 deben usar «Telegram Portika»** para que la familia responda en el mismo chat.
- Ajustes del export: n8n omite los valores por defecto y, sin workflow destino, descarta el mapeo de «Enviar a WF4». Al integrar WF4: activar el nodo, elegir WF4 y mapear `id = {{ $json.id }}`.

Pendiente:
- Integrar WF4 (#10) y cerrar #9.
- Durante el demo nadie pulsa «Execute workflow» en WF3: el modo prueba saca el webhook del bot y hay que volver a publicar.
- Sin probar: la compatibilidad de Gemini con el Parser C5 en todos los casos (si falla, va a `revision_manual`) y un chat no vinculado desde otro teléfono (probado solo en SQL).

### Aprendido (28-nov, WF3)

- Al importar un archivo en un workflow existente, n8n no trae los `settings`: hay que fijar a mano «no guardar ejecuciones exitosas».
- `setNodeParameter` del MCP de n8n con `/notes` escribe un parámetro, no la nota del nodo.
- El MCP de n8n no carga en `codex exec`: las consultas a la instancia las hace Claude.

### Aprendido (28-nov)

- Las Variables de n8n (`$vars`) no existen en Cloud Starter y no se escriben desde un workflow.
- n8n Cloud llega a Supabase por el Session pooler (la conexión directa es solo IPv6) y pide el certificado CA de Supabase con SSL `Require`.
- GitHub nunca muestra el valor de un secreto: no sirve para compartir claves.
- Vincular facturación en AI Studio pasa la cuenta a pago, y el crédito de prueba de Google Cloud no cubre la API de Gemini.

## Al 28-nov 10:00 · Ahorro y declaraciones (#13, rama `docs/13-ahorro-declaraciones`)

Hecho:
- `docs/ahorro.md`: fórmula en dos bloques. A · asistencia, por lista de un curso en un día. B · seguimiento, por falta gestionada. El período es una semana y se mide el tiempo del colegio. Las citas salen solo del README. Todos los minutos son [Hipótesis] y la proyección con las 706 faltas es [Simulación] (70,6 h en sep-dic, no semanal). Medición pendiente: cronometrar en un colegio piloto.
- `AI_USAGE.md`: filas del 28-nov (WF1, WF3, #13) y la sección «IA dentro del producto».
- `PRIOR_WORK.md`: notas de `../prep/` separadas en «antes de las 17:00» y «dentro de la ventana, fuera del repo», y tabla de terceros.
- Verificado: el ejemplo da 0,5 h, cada cita aparece en el README o en los contratos y `node --test` pasa 44/44.

Pendiente:
- Declaraciones de Brandon y Jorge cargadas en `AI_USAGE.md` según lo que Johann confirmó el 28-nov. PR #28 con «Closes #13»: listo para fusionar.
- Latencia del tótem (< 2 s) y del bot sin medir. Al medirlas se rotulan «medido en el prototipo, no en un colegio».

Aprendido:
- Las notas `01` y `03` de `prep/` eran para la idea de cobranza, que se descartó. De ahí solo quedaron el stack y el principio «la IA interpreta, las reglas deciden».
- No hubo entrevistas. La evidencia es el estudio del Ministerio (README) y el dataset ficticio.
- Un encargo sin `-Worktree` no se puede reanudar. Para iterar con el mismo agente, el primer encargo se lanza con `-Worktree`.
