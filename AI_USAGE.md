# Uso de inteligencia artificial

Usamos IA para construir. Una persona del equipo revisa cada cambio antes de fusionarlo a `main`. Esta tabla se actualiza durante el evento.

## Herramientas de desarrollo

| Herramienta | Modelo | Para qué | Quién supervisó |
| --- | --- | --- | --- |
| Claude Code (Anthropic) | Claude | Lectura de las guías, plan de arquitectura, esqueleto del repositorio y revisión de cambios | Johann |
| Codex (OpenAI) | GPT | Investigación de dominio con fuentes. Implementación del esquema, del seed y del PDF de carnés (#3) a partir de un encargo escrito | Johann |
| Codex (OpenAI) | GPT | Implementación y pruebas del CI del #5, ajustes del dictamen e integración de las pruebas de esquema del #3 | Jorge (revisión pendiente) |
| Antigravity (Google) | Gemini | Análisis exploratorio del dataset, revisión cruzada de la arquitectura y del esquema (#3) | Johann |
| Antigravity (Google) | Gemini | Implementación, despliegue en n8n Cloud, exportación y pruebas unitarias de WF2 · Ausencias (#8) | Brandon |

## IA dentro del producto

_Pendiente: qué hace la IA, qué verificamos, sus límites y qué pasa si falla._

## Criterio de uso

- La IA propone y una persona aprueba cada cambio (revisión del diff y pruebas).
- Un modelo distinto revisa los cambios sensibles del que los escribió.
- Nunca enviamos claves ni datos personales reales a ninguna herramienta.
