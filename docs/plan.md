# Plan de construcción y entrega de Pórtika

Del vie 27-nov 19:00 al sáb 28-nov 14:00 (UTC-5). Cada fila es un issue en GitHub con dueño e hito (issue de GitHub = número de la fila + 2; el ensayo es el #16). Los formatos entre piezas están en [`contratos.md`](contratos.md): con ellos casi todo avanza en paralelo. Hitos: **CP2 · sáb 12:30** (demo de punta a punta desplegada) y **Entrega · sáb 14:00**.

## Orden de construcción

Primero el camino crítico del demo y después lo demás.

| # | Issue | Dueño | Depende de | Hito | Hecho cuando |
| --- | --- | --- | --- | --- | --- |
| 1 | Esquema Supabase, migraciones y seed sintético (carnés, representantes, chat de Telegram de prueba; cada chat del seed inicia el bot de demo con /start) | Johann | — | CP2 | `supabase db push` crea las tablas y el seed carga 240 estudiantes |
| 2 | Instancia n8n: proyecto de equipo, API key y prueba de publicación por API | Brandon | — | CP2 | Un workflow de prueba se publica por `POST /publish` |
| 3 | CI/CD: gitleaks, validación de JSON de n8n, pruebas; al fusionar: primero `supabase db push`, después publicación de n8n por API y prueba de humo | Jorge | 1, 2 | CP2 | Un merge a `main` publica los workflows y la prueba de humo pasa |
| 4 | App de la puerta: primero lector QR USB (teclado); después cámara. Envía al webhook de WF1 (C2) | Jorge | C2 (se integra con 5) | CP2 | Escanear un carné crea una fila en `ingresos` |
| 5 | WF1 · Ingreso: valida el carné, evita duplicados y registra «presente» | Brandon | 1 | CP2 | Un webhook con un carné válido inserta el ingreso; uno inválido se rechaza |
| 6 | WF2 · Ausencias: cruza lista del curso con ingresos y escribe a cada familia (C3) | Brandon | 1, 5 | CP2 | Los ausentes del seed reciben el mensaje en el bot de prueba |
| 7 | WF3 · Justificativo: primero texto; después voz y foto → Gemini (C5) → reglas deterministas (C6) | Johann (prompts y reglas), Brandon (flujo) | 1 (faltas del seed) y el bot | CP2 | Las 3 entradas producen un JSON válido; un caso inválido va a revisión manual |
| 8 | WF4 · Aprobación con Send and Wait y auditoría (C7) | Brandon | C6 (se prueba con un JSON fijo; se integra con 7) | CP2 | Aprobar en Telegram cambia la falta a justificada y deja auditoría |
| 9 | Tablero en vivo con Supabase Realtime y horas ahorradas (C1) | Jorge | 1 | CP2 | Un escaneo aparece en el tablero sin recargar |
| 10 | WF0 · Errores con Error Trigger (C8) | Brandon | 2 | Entrega | Un fallo forzado avisa al equipo |
| 11 | Spec de ahorro (C5), `AI_USAGE.md` y `PRIOR_WORK.md` finales | Johann | — | Entrega | Fórmula con fuente y supuestos marcados |
| 12 | Pitch: guion de 3 minutos, `docs/pitch.pdf`, video de respaldo de 60 s y 2 ensayos | Johann | Guion: ninguna; video: 8 y 9 | Entrega | Ensayo cronometrado en 3:00 o menos |
| 13 | Entrega: tag `entrega` (13:30–13:40) y formulario con las 3 declaraciones | Johann | todo | Entrega | Llega el correo con el hash evaluado |
| 14 | Ensayo integral en producción antes de las 10:00: QR, cierre, aviso, respuesta, aprobación y cambio en el tablero | Jorge (con todo el equipo) | 3–9 | CP2 | El flujo completo corre en producción sin intervención manual |

## Camino crítico

**1 → 5 → 6 → 8 → 14.** Si una de estas se atrasa, se atrasa el demo. Lo demás corre en paralelo, en tres carriles:

- **Johann:** 1 (primero, desbloquea a todos) → prompts y reglas de 7 → 11 → guion de 12 → 13.
- **Brandon:** 2 → 5 → 6 → 8 → 10.
- **Jorge:** CI de 3 → 4 contra C2 → 9 → CD de 3 → 14.

## Cronograma

| Bloque | Meta |
| --- | --- |
| Vie 19:00–21:00 | Issues 1, 2 y 5. CI básico (3) en verde |
| Vie 21:00–01:00 | **Corte vertical:** 4 (cámara), 6, 7 (solo texto) y 8. **Meta: un justificativo en texto llega al inspector y se aprueba** |
| Sáb 08:00–10:00 | Voz y foto (7), modo tótem (4), tablero (9) y CD completo (3). **09:30: ensayo integral (14)** |
| Sáb 10:00–12:30 | Mentoría 2, correcciones. **CP2 12:30: demo de punta a punta desplegada** |
| Sáb 12:30–13:30 | Issues 10, 11 y 12. Solo correcciones de errores |
| Sáb 13:30–13:45 | Issue 13 |

## Reglas

- Rama por issue (`feat/NN-…`), PR con `Closes #NN` y CI en verde.
- Un dueño por workflow de n8n.
- Bot de Telegram de prueba distinto del de demo: un webhook por bot.
- Desde las 12:30 del sábado no entra ninguna función nueva.
