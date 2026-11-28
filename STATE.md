# STATE.md · Dónde está el trabajo

_Última actualización: vie 27-nov-2026 18:20 (UTC-5)._

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
