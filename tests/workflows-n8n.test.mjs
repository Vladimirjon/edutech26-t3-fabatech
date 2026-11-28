import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { test } from 'node:test';

const directorioN8n = new URL('../n8n/', import.meta.url);
const nombresWorkflow = new Set([
  '00-errores.json',
  '01-ingreso.json',
  '02-ausencias.json',
  '03-justificativo.json',
  '04-aprobacion.json',
]);

function esObjeto(valor) {
  return valor !== null && typeof valor === 'object' && !Array.isArray(valor);
}

function leerJson(archivo, contenido) {
  try {
    return JSON.parse(contenido);
  } catch {
    // El error de JSON.parse puede contener datos del archivo.
    throw new Error(`${archivo}: JSON inválido.`);
  }
}

function validarExport(archivo, contenido) {
  const datos = leerJson(archivo, contenido);

  if (archivo === 'ids.json') {
    assert.ok(esObjeto(datos), `${archivo}: se esperaba un mapa de workflows a IDs.`);
    for (const [nombre, id] of Object.entries(datos)) {
      assert.ok(nombresWorkflow.has(nombre), `${archivo}: nombre de workflow fuera de C10.`);
      assert.ok(typeof id === 'string' && id.trim(), `${archivo}: ID inválido para ${nombre}.`);
    }
    return;
  }

  assert.ok(nombresWorkflow.has(archivo), `${archivo}: nombre de workflow fuera de C10.`);
  assert.ok(esObjeto(datos) && Array.isArray(datos.nodes), `${archivo}: se esperaba un export con nodes.`);
  assert.ok(!Object.hasOwn(datos, 'pinData'), `${archivo}: elimina pinData antes de versionar el workflow.`);

  for (const [indice, nodo] of datos.nodes.entries()) {
    const ubicacion = `${archivo}, nodo ${indice + 1}`;
    assert.ok(esObjeto(nodo), `${ubicacion}: el nodo debe ser un objeto.`);
    if (!Object.hasOwn(nodo, 'credentials')) continue;

    assert.ok(esObjeto(nodo.credentials), `${ubicacion}: credentials debe contener referencias.`);
    for (const referencia of Object.values(nodo.credentials)) {
      assert.ok(esObjeto(referencia), `${ubicacion}: referencia de credencial inválida.`);
      const campos = Object.entries(referencia);
      assert.ok(
        campos.length > 0 && campos.every(([campo, valor]) =>
          (campo === 'id' || campo === 'name') && typeof valor === 'string' && valor.trim()),
        `${ubicacion}: la credencial solo puede tener id y name de referencia.`,
      );
    }
  }
}

test('n8n acepta un workflow con referencias y un mapa de IDs válido', () => {
  validarExport('01-ingreso.json', JSON.stringify({
    nodes: [{ credentials: { postgres: { id: 'ejemplo', name: 'Postgres de prueba' } } }],
  }));
  validarExport('ids.json', JSON.stringify({ '01-ingreso.json': 'ejemplo' }));
});

test('n8n rechaza JSON inválido e indica el archivo', () => {
  assert.throws(() => validarExport('01-ingreso.json', '{'), /01-ingreso\.json: JSON inválido/);
});

test('n8n rechaza nombres fuera de C10 y exports sin nodes', () => {
  assert.throws(() => validarExport('ingreso.json', '{"nodes":[]}'), /nombre.*fuera de C10/);
  assert.throws(() => validarExport('01-ingreso.json', '{}'), /export con nodes/);
});

test('n8n rechaza pinData incluso cuando está vacío', () => {
  assert.throws(() => validarExport('01-ingreso.json', '{"nodes":[],"pinData":{}}'), /elimina pinData/);
});

test('n8n rechaza datos de credenciales en lugar de referencias', () => {
  const contenido = JSON.stringify({
    nodes: [{ credentials: { postgres: { id: 'ejemplo', data: {} } } }],
  });
  assert.throws(() => validarExport('01-ingreso.json', contenido), /solo puede tener id y name/);
});

test('n8n valida los JSON versionados del repositorio', (t) => {
  const archivos = readdirSync(directorioN8n).filter((archivo) => archivo.toLowerCase().endsWith('.json'));
  if (!archivos.some((archivo) => archivo !== 'ids.json')) {
    t.diagnostic('Todavía no hay workflows exportados. Se ejecutaron los casos de prueba sintéticos.');
  }
  for (const archivo of archivos) {
    validarExport(archivo, readFileSync(new URL(archivo, directorioN8n), 'utf8'));
  }
});
