import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { test } from 'node:test';

const rutaCodigo = new URL('../n8n/codigo/c6-reglas.js', import.meta.url);
const rutaWorkflow = new URL('../n8n/03-justificativo.json', import.meta.url);
const codigo = readFileSync(rutaCodigo, 'utf8');

// Ejecuta el jsCode igual que el nodo Code de n8n: cuerpo de función con $json.
function correr(entrada) {
  return new Function('$json', codigo)(entrada).json;
}

function caso(cambios = {}, extraccion = {}) {
  return {
    extraccion: { estudiante_codigo: 'EST-014', fechas: ['2025-12-01'], motivo: 'salud', resumen: 'Fiebre', confianza: 0.9, ...extraccion },
    hijos: [{ codigo: 'EST-014', curso: '8vo EGB', paralelo: 'A' }],
    faltas: [{ estudiante_codigo: 'EST-014', fecha: '2025-12-01', estado: 'injustificada' }],
    fecha_demo: '2025-12-01',
    plazo_dias: '3',
    ...cambios,
  };
}

const regla = (validacion, id) => validacion.reglas.find((r) => r.id === id);

test('el ejemplo del #9 va a aprobación y conserva la entrada', () => {
  const salida = correr(caso({ chat_id: 123 }));
  assert.equal(salida.chat_id, 123);
  assert.equal(salida.validacion.destino, 'aprobacion');
  assert.equal(salida.validacion.valido, true);
  assert.equal(salida.validacion.estudiante_codigo, 'EST-014');
  assert.deepEqual(salida.validacion.fechas, ['2025-12-01']);
  assert.ok(salida.validacion.reglas.every((r) => r.ok));
});

test('R4: confianza 0,5 va a revisión manual', () => {
  const { validacion } = correr(caso({}, { confianza: 0.5 }));
  assert.equal(validacion.destino, 'revision_manual');
  assert.equal(regla(validacion, 'R4').ok, false);
});

test('R3: una falta elegible futura se rechaza', () => {
  const entrada = caso({ faltas: [{ estudiante_codigo: 'EST-014', fecha: '2025-12-02', estado: 'injustificada' }] }, { fechas: ['2025-12-02'] });
  const { validacion } = correr(entrada);
  assert.equal(validacion.destino, 'rechazado');
  assert.match(regla(validacion, 'R3').detalle, /futuras/);
});

test('R3: cuenta días hábiles y salta el fin de semana', () => {
  const faltas = ['2025-11-25', '2025-11-26'].map((fecha) => ({ estudiante_codigo: 'EST-014', fecha, estado: 'injustificada' }));
  // Lunes 1-dic: mié 26 está a 3 días hábiles; mar 25, a 4.
  assert.equal(correr(caso({ faltas }, { fechas: ['2025-11-26'] })).validacion.destino, 'aprobacion');
  assert.equal(correr(caso({ faltas }, { fechas: ['2025-11-25'] })).validacion.destino, 'rechazado');
  // Demo del lunes 12-ene-2026: el viernes 9 está a 1 día hábil.
  const viernes = caso({ fecha_demo: '2026-01-12', faltas: [{ estudiante_codigo: 'EST-014', fecha: '2026-01-09', estado: 'pendiente' }] }, { fechas: ['2026-01-09'] });
  assert.equal(correr(viernes).validacion.destino, 'aprobacion');
});

test('R3: plazo_dias se lee como texto o número y usa 3 si falta o no es entero decimal', () => {
  const faltas = ['2025-11-25', '2025-11-26'].map((fecha) => ({ estudiante_codigo: 'EST-014', fecha, estado: 'injustificada' }));
  assert.equal(correr(caso({ faltas, plazo_dias: 5 }, { fechas: ['2025-11-25'] })).validacion.destino, 'aprobacion');
  assert.equal(correr(caso({ faltas, plazo_dias: ' 5 ' }, { fechas: ['2025-11-25'] })).validacion.destino, 'aprobacion');
  assert.equal(correr(caso({ faltas, plazo_dias: undefined }, { fechas: ['2025-11-25'] })).validacion.destino, 'rechazado');
  assert.equal(correr(caso({ faltas, plazo_dias: '0x10' }, { fechas: ['2025-11-26'] })).validacion.destino, 'aprobacion');
  assert.equal(correr(caso({ faltas, plazo_dias: '0x10' }, { fechas: ['2025-11-25'] })).validacion.destino, 'rechazado');
});

test('R3 manda: fecha futura se rechaza aunque fallen R1, R2 o R4', () => {
  const conBajaConfianza = caso({ faltas: [{ estudiante_codigo: 'EST-014', fecha: '2025-12-02', estado: 'injustificada' }] },
    { fechas: ['2025-12-02'], confianza: 0.5 });
  assert.equal(correr(conBajaConfianza).validacion.destino, 'rechazado');
  const estudianteAjeno = caso({}, { estudiante_codigo: 'EST-099', fechas: ['2025-12-05'] });
  assert.equal(correr(estudianteAjeno).validacion.destino, 'rechazado');
});

test('R3: sin fecha_demo válida no se rechaza; decide el inspector', () => {
  const { validacion } = correr(caso({ fecha_demo: null }));
  assert.equal(validacion.destino, 'revision_manual');
  assert.match(regla(validacion, 'R3').detalle, /fecha_demo/);
});

test('R1: sin estudiante y un solo hijo, usa ese hijo', () => {
  const { validacion } = correr(caso({}, { estudiante_codigo: null }));
  assert.equal(validacion.destino, 'aprobacion');
  assert.equal(validacion.estudiante_codigo, 'EST-014');
});

test('R1: sin estudiante y dos hijos va a revisión manual', () => {
  const hijos = [{ codigo: 'EST-014', curso: '8vo EGB', paralelo: 'A' }, { codigo: 'EST-015', curso: '9no EGB', paralelo: 'B' }];
  const { validacion } = correr(caso({ hijos }, { estudiante_codigo: null }));
  assert.equal(validacion.destino, 'revision_manual');
  assert.equal(validacion.estudiante_codigo, null);
  assert.equal(regla(validacion, 'R1').ok, false);
});

test('R1: un estudiante ajeno va a revisión manual si R3 pasa', () => {
  const { validacion } = correr(caso({}, { estudiante_codigo: 'EST-099' }));
  assert.equal(validacion.destino, 'revision_manual');
  assert.equal(validacion.estudiante_codigo, null);
  assert.equal(regla(validacion, 'R1').ok, false);
});

test('R2: sin falta elegible va a revisión manual, fechas es [] y fechas_pedidas trae lo pedido', () => {
  const sinFalta = correr(caso({}, { fechas: ['2025-11-28'] })).validacion;
  assert.equal(sinFalta.destino, 'revision_manual');
  assert.deepEqual(sinFalta.fechas, []);
  assert.deepEqual(sinFalta.fechas_pedidas, ['2025-11-28']);
  const justificada = caso({ faltas: [{ estudiante_codigo: 'EST-014', fecha: '2025-12-01', estado: 'justificada' }] });
  const { validacion } = correr(justificada);
  assert.equal(validacion.destino, 'revision_manual');
  assert.deepEqual(validacion.fechas, []);
  assert.deepEqual(validacion.fechas_pedidas, ['2025-12-01']);
  assert.equal(regla(validacion, 'R2').ok, false);
});

test('R2: acepta la fecha de Postgres como marca de tiempo', () => {
  const entrada = caso({ faltas: [{ estudiante_codigo: 'EST-014', fecha: '2025-12-01T05:00:00.000Z', estado: 'pendiente' }] });
  assert.equal(correr(entrada).validacion.destino, 'aprobacion');
});

test('C5: si Gemini falla o rompe el esquema, va a revisión manual', () => {
  const base = caso().extraccion;
  const malos = [null, 'texto', { motivo: 'salud' }, ...[{ fechas: [] }, { motivo: 'viaje' }, { confianza: 2 },
    { fechas: ['2025-02-30'] }, { estudiante_codigo: 'EST-14' }, { resumen: 'x'.repeat(201) },
    { tiene_documento: 'false' }].map((c) => ({ ...base, ...c }))];
  for (const malo of malos) {
    const { validacion } = correr(caso({ extraccion: malo }));
    assert.equal(validacion.destino, 'revision_manual', JSON.stringify(malo));
    assert.equal(regla(validacion, 'C5').ok, false);
  }
  assert.equal(correr(caso({}, { tiene_documento: true })).validacion.destino, 'aprobacion');
  assert.equal(correr(caso({}, { resumen: '😀'.repeat(101) })).validacion.destino, 'aprobacion');
});

test('el nodo Reglas C6 del export usa este mismo código', (t) => {
  if (!existsSync(rutaWorkflow)) return t.skip('aún no existe n8n/03-justificativo.json');
  const workflow = JSON.parse(readFileSync(rutaWorkflow, 'utf8'));
  const nodo = workflow.nodes.find((n) => n.name === 'Reglas C6');
  assert.ok(nodo, 'falta el nodo Code «Reglas C6» en 03-justificativo.json');
  assert.equal(nodo.type, 'n8n-nodes-base.code');
  assert.equal(nodo.parameters.mode, 'runOnceForEachItem');
  assert.equal(nodo.parameters.jsCode.replace(/\r\n/g, '\n'), codigo.replace(/\r\n/g, '\n'));
});
