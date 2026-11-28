# Uso de inteligencia artificial

Usamos IA para construir. Cada resultado lo revisó una persona del equipo antes de entrar al repositorio. Esta tabla se actualiza durante el evento.

## Herramientas de desarrollo

| Herramienta | Modelo | Para qué | Quién supervisó |
| --- | --- | --- | --- |
| Claude Code (Anthropic) | Claude | Lectura de las guías, plan de arquitectura, esqueleto del repositorio y revisión de cambios | Johann |
| Codex (OpenAI) | GPT | Investigación de dominio con fuentes. Implementación del esquema, del seed y del PDF de carnés (#3) a partir de un encargo escrito | Johann |
| Antigravity (Google) | Gemini | Análisis exploratorio del dataset, revisión cruzada de la arquitectura y del esquema (#3) | Johann |

## IA dentro del producto

_Pendiente: qué hace la IA, qué verificamos, sus límites y qué pasa si falla._

## Criterio de uso

- La IA propone y una persona aprueba cada cambio (revisión del diff y pruebas).
- Un modelo distinto revisa los cambios sensibles del que los escribió.
- Nunca enviamos claves ni datos personales reales a ninguna herramienta.
