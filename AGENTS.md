# AGENTS.md · Reglas para personas y agentes de IA en el repo de Pórtika

Aplica a los tres integrantes y a cualquier agente (Claude Code, Codex, Antigravity, Copilot). Lee primero `STATE.md`, `TASKS.md` y [`docs/contratos.md`](docs/contratos.md): ningún cambio rompe un contrato sin un PR que lo modifique primero.

## Reglas del evento (no negociables)

- Todo el código se escribe entre el **vie 27-nov 17:00 y el sáb 28-nov 14:00 (UTC-5)**. Lo previo va en `PRIOR_WORK.md`.
- **Prohibidos los datos personales reales.** Solo datos sintéticos, declarados en `data/README.md`.
- **Todo uso de IA se declara en `AI_USAGE.md`.** Ocultarlo descalifica.
- Lo que no esté en el tag `entrega` no existe para el jurado. El tag se crea una sola vez, el sábado entre 13:30 y 13:40.

## Datos y afirmaciones

- **Ninguna cifra sin fuente.** Cada dato del README, del pitch o de la spec lleva URL y una cita textual, o se marca como **hipótesis**.
- Separar siempre lo **probado**, lo **simulado** y lo **pendiente**.

## Git

- Ramas `tipo/NN-descripcion` (`feat/`, `fix/`, `docs/`, `chore/`), donde NN es el número de issue o tarea.
- Conventional Commits en español: `feat: …`, `fix: …`, `docs: …`.
- Commits pequeños y frecuentes, **cada persona con su propia identidad de Git** (el correo debe coincidir con su cuenta de GitHub).
- Nada de push directo a `main` después del esqueleto: siempre PR con CI en verde.
- `git add` archivo por archivo; nunca `git add .`.
- Nunca subir `.env`, claves ni tokens.
- Sin trailers de coautoría de IA. La declaración vive en `AI_USAGE.md`.

## n8n

- Cada workflow tiene **un solo dueño**: los JSON no se fusionan bien.
- Workflow exportado = `n8n/NN-nombre.json`, sin `pinData` y sin credenciales (solo referencias).
- La IA propone y las reglas deterministas deciden. Cada flujo con IA tiene un camino de falla definido.

## Agentes de IA

- Cada encargo de código lleva el criterio de "hecho" verificable y el estilo del cambio más pequeño posible.
- Quien implementa no se revisa a sí mismo: un modelo de otro proveedor revisa los cambios sensibles.
- Un humano revisa el diff y corre las pruebas antes de cada merge.
