# Estimación de ahorro

## Fórmula

`horas ahorradas = (min manual − min con Pórtika) × unidades ÷ 60`

Se aplica la fórmula a cada bloque con su propia unidad. En cada bloque, ambos tiempos cubren los mismos pasos. El total semanal del colegio (docente tutor e inspección) es **A + B**, con las listas y faltas gestionadas de esa semana.

## [Contexto del Ministerio]

La sección Evidencia del [README](../README.md#evidencia) cita la **Estrategia «Tiempo para Ser Docente», Ministerio de Educación, 2025**. [PDF oficial](https://educacion.gob.ec/wp-content/uploads/downloads/2025/08/estrategia-tiempo-para-ser-docente.pdf)

- «encuesta a 9.957 docentes»
- «alrededor de 15 horas semanales» de tareas fuera de clase dentro del plantel.
- «Las tareas que demandan mayor cantidad de tiempo son: el "Traslado de los estudiantes a las instituciones educativas" y el "Registro de asistencia", con el 44,44% cada una».

## [Medición cronometrada]

Ninguna. Medición pendiente: cronometrar el proceso real en un colegio piloto.

## [Hipótesis] Desglose por pasos

### Bloque A · Asistencia

Unidad **una lista de un curso en un día**.

| Paso | Min manual supuestos | Min con Pórtika supuestos | Qué hace Pórtika en ese paso |
| --- | ---: | ---: | --- |
| Pasar lista | 2 | 0,5 | El tótem (WF1) registra los ingresos. |
| Consolidar ausencias | 2 | 0,5 | El cierre (WF2) consolida las ausencias. |
| **Total por lista** | **4** | **1** | |

**[Hipótesis]** Horas del bloque A = (4 − 1) × listas de cursos en la semana ÷ 60. La cantidad de listas queda como variable.

### Bloque B · Seguimiento de la falta

Unidad **una falta gestionada**, desde el aviso hasta el registro del justificativo.

| Paso | Min manual supuestos | Min con Pórtika supuestos | Qué hace Pórtika en ese paso |
| --- | ---: | ---: | --- |
| Avisar a la familia | 4 | 1,5 | WF2 avisa automáticamente solo a familias con `telegram_chat_id` (C3). Las faltas «sin contacto» requieren aviso manual. |
| Recibir y registrar el justificativo | 6 | 2,5 | El bot (WF3) extrae los datos (C5) y aplica las reglas (C6). El inspector revisa y decide en WF4, por lo que queda tiempo humano. |
| **Total por falta** | **10** | **4** | |

#### Ejemplo

**[Hipótesis]** Con 5 faltas sintéticas en una semana, (10 − 4) × 5 ÷ 60 = **0,5 h**.

#### [Simulación] Proyección con el seed

Simulación sobre datos ficticios, no un ahorro real.

El [README](../README.md#evidencia) reporta «706 faltas injustificadas» para «septiembre a diciembre de 2025». Si cada falta se gestionara con los tiempos supuestos, (10 − 4) × 706 ÷ 60 = **70,6 h** en todo septiembre-diciembre 2025, no es un ahorro semanal.

## Lado del sistema (prototipo)

- Tótem. Meta de «menos de 2 s» según [C2](contratos.md#c2--webhook-de-ingreso-tótem-y-app--wf1), pendiente de medir en el prototipo.
- Tiempo de respuesta del bot, pendiente de medir en el prototipo.

Al medirlos, usar el rótulo «medido en el prototipo, no en un colegio». Las latencias del sistema se reportan por separado del tiempo humano ahorrado.

## Para el tablero (#11)

**Estimación** · A + B, con `horas ahorradas = (min manual − min con Pórtika) × unidades ÷ 60` en cada bloque.\
**Unidades** · A: una lista de un curso en un día. B: una falta gestionada.\
**Período** · una semana
