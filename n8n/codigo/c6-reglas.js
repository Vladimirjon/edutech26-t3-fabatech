// C6 · Reglas deterministas de WF3. Nodo Code «Reglas C6», modo «Run Once for Each Item».
// Este archivo es la fuente: se pega tal cual en el nodo, y tests/c6-reglas.test.mjs
// comprueba que el jsCode exportado en n8n/03-justificativo.json no se desvíe.
//
// Entrada ($json), la arma el flujo antes de este nodo:
//   extraccion  salida de Gemini (C5), o null si Gemini falló o se agotó el tiempo
//   hijos       [{ codigo, nombre_ficticio, curso, paralelo }] del representante del chat
//   faltas      [{ estudiante_codigo, fecha: 'AAAA-MM-DD', estado }] de esos hijos
//   fecha_demo  'AAAA-MM-DD' (fila fecha_demo de configuracion)
//   plazo_dias  número o texto (fila plazo_dias; 3 si falta)
//   fechas de Postgres: pedirlas como texto (`fecha::text`)
// Salida: el mismo $json más `validacion` (C6), con estudiante_codigo y fechas ya resueltos
// para la sentencia SQL que marca justificativo y faltas.

const MOTIVOS = ['salud', 'calamidad_domestica', 'transporte', 'tramite', 'otro'];
const ESTADOS_ELEGIBLES = ['injustificada', 'pendiente'];
const PLAZO_POR_DEFECTO = 3;
const CONFIANZA_MINIMA = 0.6;

function esFecha(texto) {
  if (typeof texto !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(texto)) return false;
  const dia = new Date(texto + 'T00:00:00Z');
  return !Number.isNaN(dia.getTime()) && dia.toISOString().slice(0, 10) === texto;
}

// Postgres puede entregar la fecha como '2025-12-01T05:00:00.000Z'; los 10 primeros caracteres son el día.
function soloDia(valor) {
  return String(valor ?? '').slice(0, 10);
}

// Días hábiles en (desde, hasta]: 0 si es el mismo día.
// shortcut: solo descuenta sábados y domingos, no feriados; basta para el demo del 12-ene-2026.
function diasHabilesEntre(desde, hasta) {
  const dia = new Date(desde + 'T00:00:00Z');
  const fin = new Date(hasta + 'T00:00:00Z');
  let habiles = 0;
  while (dia < fin) {
    dia.setUTCDate(dia.getUTCDate() + 1);
    const semana = dia.getUTCDay();
    if (semana !== 0 && semana !== 6) habiles++;
  }
  return habiles;
}

function leerPlazo(valor) {
  if (typeof valor === 'number') return Number.isInteger(valor) && valor >= 0 ? valor : PLAZO_POR_DEFECTO;
  if (typeof valor === 'string' && /^\d+$/.test(valor.trim())) {
    const n = Number(valor.trim());
    return Number.isInteger(n) ? n : PLAZO_POR_DEFECTO;
  }
  return PLAZO_POR_DEFECTO;
}

// La salida del LLM no es de fiar: se revisa contra el esquema de C5 aunque venga del parser.
function errorDeEsquema(ex) {
  if (ex === null || typeof ex !== 'object' || Array.isArray(ex)) return 'Gemini no devolvió una extracción';
  const codigo = ex.estudiante_codigo;
  if (codigo !== null && !(typeof codigo === 'string' && /^EST-\d{3}$/.test(codigo))) return 'estudiante_codigo inválido';
  if (!Array.isArray(ex.fechas) || ex.fechas.length === 0 || !ex.fechas.every(esFecha)) return 'fechas inválidas';
  if (!MOTIVOS.includes(ex.motivo)) return 'motivo inválido';
  if (typeof ex.resumen !== 'string' || [...ex.resumen].length > 200) return 'resumen inválido';
  if (typeof ex.confianza !== 'number' || !(ex.confianza >= 0 && ex.confianza <= 1)) return 'confianza inválida';
  if (ex.tiene_documento !== undefined && typeof ex.tiene_documento !== 'boolean') return 'tiene_documento inválido';
  return null;
}

function validar(entrada) {
  const ex = entrada.extraccion;
  const error = errorDeEsquema(ex);
  if (error) {
    return { valido: false, destino: 'revision_manual', estudiante_codigo: null, fechas: [], fechas_pedidas: [],
      reglas: [{ id: 'C5', ok: false, detalle: error }] };
  }

  const hijos = Array.isArray(entrada.hijos) ? entrada.hijos : [];
  const faltas = Array.isArray(entrada.faltas) ? entrada.faltas : [];
  const fechas = [...new Set(ex.fechas)].sort();
  const fechaDemo = soloDia(entrada.fecha_demo);
  const plazo = leerPlazo(entrada.plazo_dias);

  // R1: el estudiante es hijo del representante; si viene null y hay un solo hijo, se usa ese.
  let codigo = ex.estudiante_codigo;
  if (codigo === null && hijos.length === 1) codigo = hijos[0].codigo;
  const r1 = codigo !== null && hijos.some((hijo) => hijo.codigo === codigo);
  const r1Detalle = r1 ? `${codigo} es hijo del representante`
    : codigo === null ? `No se indicó el estudiante y el representante tiene ${hijos.length} hijos`
    : `${codigo} no es hijo del representante`;

  // R2: cada fecha tiene una falta injustificada o pendiente de ese estudiante.
  const sinFalta = fechas.filter((fecha) => !faltas.some((falta) =>
    falta.estudiante_codigo === codigo && soloDia(falta.fecha) === fecha && ESTADOS_ELEGIBLES.includes(falta.estado)));
  const r2 = r1 && sinFalta.length === 0;
  const r2Detalle = !r1 ? 'Sin estudiante válido'
    : r2 ? 'Todas las fechas tienen una falta elegible' : `Sin falta elegible: ${sinFalta.join(', ')}`;

  // R3: ninguna fecha es futura y todas caben en el plazo de días hábiles.
  const r3Evaluable = esFecha(fechaDemo);
  const futuras = r3Evaluable ? fechas.filter((fecha) => fecha > fechaDemo) : [];
  const tardias = r3Evaluable ? fechas.filter((fecha) => fecha <= fechaDemo && diasHabilesEntre(fecha, fechaDemo) > plazo) : [];
  const r3 = r3Evaluable && futuras.length === 0 && tardias.length === 0;
  const r3Detalle = !r3Evaluable ? 'fecha_demo no es válida en configuracion'
    : futuras.length ? `Fechas futuras: ${futuras.join(', ')}`
    : tardias.length ? `Fuera del plazo de ${plazo} días hábiles: ${tardias.join(', ')}`
    : `Dentro del plazo de ${plazo} días hábiles`;

  // R4: confianza suficiente.
  const r4 = ex.confianza >= CONFIANZA_MINIMA;
  const r4Detalle = `Confianza ${ex.confianza} (mínimo ${CONFIANZA_MINIMA})`;

  // R3 manda: una fecha futura o fuera de plazo se rechaza (C6)
  const destino = r1 && r2 && r3 && r4 ? 'aprobacion'
    : r3Evaluable && !r3 ? 'rechazado'
    : 'revision_manual';

  return {
    valido: destino === 'aprobacion',
    destino,
    estudiante_codigo: r1 ? codigo : null,
    fechas: r2 ? fechas : [],
    fechas_pedidas: fechas,
    reglas: [
      { id: 'R1', ok: r1, detalle: r1Detalle },
      { id: 'R2', ok: r2, detalle: r2Detalle },
      { id: 'R3', ok: r3, detalle: r3Detalle },
      { id: 'R4', ok: r4, detalle: r4Detalle },
    ],
  };
}

return { json: { ...$json, validacion: validar($json) } };
