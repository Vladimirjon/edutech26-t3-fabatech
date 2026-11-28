# Trabajo previo

Ventana oficial del evento: vie 27-nov 17:00 a sáb 28-nov 14:00 (UTC-5). Las notas están fuera del repositorio, en `../prep/`.

## Antes de las 17:00 (ideas e investigación, sin código del proyecto)

| Archivo | Última edición | Contenido | Qué se reutilizó |
| --- | --- | --- | --- |
| `00-ground-truth.md` | 27-nov 12:40 | Requisitos extraídos de la Guía oficial, la Guía del hacker y la Rúbrica | Reglas del evento de `AGENTS.md` y estructura obligatoria del repo |
| `01-arquitectura-y-forma-de-trabajo.md` | 27-nov 12:46 | Borrador de arquitectura para otra idea (agente de cobranza), con revisión cruzada de Antigravity a las 12:45 | El stack (Supabase, n8n Cloud, Gemini Flash-Lite gratis, Telegram) y el principio «la IA interpreta, las reglas deciden». El producto y sus workflows se descartaron |

## Dentro de la ventana pero fuera del repo

| Archivo | Última edición | Contenido | Qué se reutilizó |
| --- | --- | --- | --- |
| `02-entrevistas.md` | 27-nov 17:19 | Guía para preparar la entrevista (preguntas y plantilla) | Nada: la entrevista no se hizo. El problema y la evidencia del README salen del estudio del Ministerio y del dataset ficticio. |
| `03-exploracion-track-t3.md` | 27-nov 17:00-17:45 | Exploración del track T3 frente al dataset y la competencia; proponía la cobranza | Nada: el equipo cambió al problema de asistencia, con la evidencia del Ministerio |

### Investigación complementaria

- **Análisis exploratorio del dataset ficticio** (antes de las 17:00: `01` ya cita sus cifras a las 12:46) que entregó la mesa técnica (`dataset-ficticio-colegio`, CC0). Se calcularon conteos de mora, pagos tardíos, asistencia y notas con scripts de un solo uso que no forman parte de este repositorio.
- **Investigación de dominio** (Codex, 17:00-17:45, según `03`): procesos administrativos de colegios particulares en Ecuador y productos existentes.

## Librerías, plantillas y servicios de terceros

| Qué | Para qué | Licencia o condiciones |
| --- | --- | --- |
| `dataset-ficticio-colegio` | Datos sintéticos del demo | CC0 ([data/README.md](data/README.md)) |
| Simple Icons | Logos del diagrama de arquitectura | CC0 ([README.md](README.md)) |
| `segno==1.6.1` | Generación de códigos QR ([requirements.txt](requirements.txt)) | Licencia **[por confirmar]** |
| n8n Cloud Starter | Orquestación de workflows | términos del servicio |
| Supabase (plan gratis) | Base de datos | términos del servicio |
| Vercel Hobby | Alojamiento web | términos del servicio |
| Google AI Studio (nivel gratis) | Transcripción y extracción con Gemini | términos del servicio |
| Telegram Bot API | Avisos y justificativos por chat | términos del servicio |
