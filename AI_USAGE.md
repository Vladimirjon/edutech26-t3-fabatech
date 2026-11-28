# Uso de inteligencia artificial

Usamos IA para construir. Una persona del equipo revisa cada cambio antes de fusionarlo a `main`. Esta tabla se actualiza durante el evento.

## Herramientas de desarrollo

| Herramienta | Modelo | Para qué | Quién supervisó |
| --- | --- | --- | --- |
| Claude Code (Anthropic) | Claude | Lectura de las guías, plan de arquitectura, esqueleto del repositorio y revisión de cambios | Johann |
| Codex (OpenAI) | GPT | Investigación de dominio con fuentes. Implementación del esquema, del seed y del PDF de carnés (#3) a partir de un encargo escrito | Johann |
| Codex (OpenAI) | GPT | Implementación y pruebas del CI del #5, ajustes del dictamen e integración de las pruebas de esquema del #3 | Jorge |
| Antigravity (Google) | Gemini | Análisis exploratorio del dataset, revisión cruzada de la arquitectura y del esquema (#3) | Johann |
| Codex (OpenAI) y Claude Code (Anthropic) | GPT y Claude | 28-nov · WF1 · Ingreso (#7, PR #24). Codex implementó WF1. Claude Code revisó y probó la consulta en Postgres 15.8 y en producción. Hubo una revisión cruzada con 6 hallazgos aplicados | Johann |
| Codex (OpenAI), Antigravity (Google) y Claude Code (Anthropic) | GPT, Gemini y Claude | 28-nov · WF3 · Justificativo (#9). Codex implementó el flujo y los arreglos. Antigravity hizo 2 revisiones cruzadas. Claude Code orquestó, revisó, probó el SQL y consultó la instancia de n8n por MCP | Johann |
| Codex (OpenAI) y Antigravity (Google) | GPT y Gemini | 28-nov · #13. Codex redactó la estimación de ahorro y actualizó las declaraciones. Antigravity hizo la revisión cruzada | Johann |
| Antigravity (Google), con agentes | Claude Sonnet 5.5 | 28-nov · Implementación en todos sus issues y PR | Brandon: revisó y aprobó cada diff |
| Codex (OpenAI) y Antigravity (Google) | GPT-6.2 Sol y Gemini 4 Hydrogen | 28-nov · Implementación en todos sus issues y PR | Jorge: revisó y aprobó cada diff |
| Codex (OpenAI) y Claude Code (Anthropic) | GPT y Claude | 28-nov · Revisión del PR #27 (WF2). Codex hizo la revisión cruzada. Claude Code probó el CTE en Postgres 15.8, aplicó los arreglos, publicó WF2 en n8n por MCP y borró los datos de prueba de producción | Johann |

## IA dentro del producto

- Gemini 3.5 Flash Lite (AI Studio) transcribe la voz y extrae los datos de [C5](docs/contratos.md#c5--extracción-con-gemini-wf3) de texto, voz o foto.
- Las reglas C6 son deterministas y deciden el destino del caso. El inspector decide en WF4 y la IA no aprueba justificativos.
- La respuesta a la familia sale de plantillas, sin IA.
- Si Gemini falla, se agota el tiempo o la salida incumple el esquema, el caso pasa a `revision_manual`.
- Se verificaron las reglas C6 con `node --test` y se probaron los [prompts de WF3](docs/prompts-wf3.md) en AI Studio con texto, foto y voz.
- AI Studio usa el nivel gratis, con 500 llamadas al día según el cupo que el equipo vio el 28-nov ([C5](docs/contratos.md#c5--extracción-con-gemini-wf3)). Solo se usan datos sintéticos.

## Criterio de uso

- La IA propone y una persona aprueba cada cambio (revisión del diff y pruebas).
- Un modelo distinto revisa los cambios sensibles del que los escribió.
- Nunca enviamos claves ni datos personales reales a ninguna herramienta.
