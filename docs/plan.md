# Plan de construcción y entrega

Del vie 27-nov 19:00 al sáb 28-nov 14:00 (UTC-5). Cada fila es un issue en GitHub con dueño e hito (issue de GitHub = número de la fila + 2; el ensayo es el #16). Hitos: **CP2 · sáb 12:30** (demo de punta a punta desplegada) y **Entrega · sáb 14:00**.

## Orden de construcción

Primero el camino crítico del demo y después lo demás.

| # | Issue | Dueño | Depende de | Hito | Hecho cuando |
| --- | --- | --- | --- | --- | --- |
| 1 | Esquema Supabase, migraciones y seed sintético (carnés, representantes, chat de Telegram de prueba; cada chat del seed inicia el bot de demo con /start) | Johann | — | CP2 | `supabase db push` crea las tablas y el seed carga 240 estudiantes |
| 2 | Instancia n8n: proyecto de equipo, API key y prueba de publicación por API | Brandon | — | CP2 | Un workflow de prueba se publica por `POST /publish` |
| 3 | CI/CD: gitleaks, validación de JSON de n8n, pruebas; al fusionar: primero `supabase db push`, después publicación de n8n por API y prueba de humo | Jorge | 1, 2 | CP2 | Un merge a `main` publica los workflows y la prueba de humo pasa |
| 4 | App de la puerta: primero escaneo con cámara; después **modo tótem** (escaneo continuo o lector QR USB). Envía al webhook de WF1 | Jorge | 5 | CP2 | Escanear un carné crea una fila en `ingresos` |
| 5 | WF1 · Ingreso: valida el carné, evita duplicados y registra «presente» | Brandon | 1 | CP2 | Un webhook con un carné válido inserta el ingreso; uno inválido se rechaza |
| 6 | WF2 · Ausencias: cruza lista del curso con ingresos y escribe a cada familia | Brandon | 5 | CP2 | Los ausentes del seed reciben el mensaje en el bot de prueba |
| 7 | WF3 · Justificativo: primero texto; después voz y foto → Gemini con JSON de esquema → reglas deterministas | Johann (prompts y reglas), Brandon (flujo) | 6 | CP2 | Las 3 entradas producen un JSON válido; un caso inválido va a revisión manual |
| 8 | WF4 · Aprobación con Send and Wait y auditoría | Brandon | 7 | CP2 | Aprobar en Telegram cambia la falta a justificada y deja auditoría |
| 9 | Tablero en vivo con Supabase Realtime y horas ahorradas | Jorge | 1 | CP2 | Un escaneo aparece en el tablero sin recargar |
| 10 | WF0 · Errores con Error Trigger | Brandon | 5 | Entrega | Un fallo forzado avisa al equipo |
| 11 | Spec de ahorro (C5), `AI_USAGE.md` y `PRIOR_WORK.md` finales | Johann | — | Entrega | Fórmula con fuente y supuestos marcados |
| 12 | Pitch: guion de 3 minutos, `docs/pitch.pdf`, video de respaldo de 60 s y 2 ensayos | Johann | 8, 9 | Entrega | Ensayo cronometrado en 3:00 o menos |
| 13 | Entrega: tag `entrega` (13:30–13:40) y formulario con las 3 declaraciones | Johann | todo | Entrega | Llega el correo con el hash evaluado |
| 14 | Ensayo integral en producción antes de las 10:00: QR, cierre, aviso, respuesta, aprobación y cambio en el tablero | Jorge (con todo el equipo) | 3–9 | CP2 | El flujo completo corre en producción sin intervención manual |

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
