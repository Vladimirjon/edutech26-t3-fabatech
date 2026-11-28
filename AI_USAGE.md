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
| Codex (OpenAI) y Claude Code (Anthropic) | GPT y Claude | 28-nov · Revisión del PR #27 (WF2). Codex hizo la revisión cruzada. Claude Code probó el CTE en Postgres 15.8, aplicó los arreglos, publicó WF2 en n8n por MCP y borró los datos de prueba de producción | Johann |

## IA dentro del producto

_Pendiente: qué hace la IA, qué verificamos, sus límites y qué pasa si falla._

## Criterio de uso

- La IA propone y una persona aprueba cada cambio (revisión del diff y pruebas).
- Un modelo distinto revisa los cambios sensibles del que los escribió.
- Nunca enviamos claves ni datos personales reales a ninguna herramienta.
