import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmdirSync, unlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const directorioN8n = fileURLToPath(new URL('../n8n/', import.meta.url));
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
  assert.ok(!contenido.startsWith('\uFEFF'), `${archivo}: guarda el JSON en UTF-8 sin BOM.`);
  try {
    return JSON.parse(contenido);
  } catch {
    // El error de JSON.parse puede contener datos del archivo.
    throw new Error(`${archivo}: JSON inválido.`);
  }
}

function validarIds(contenido, exportsPresentes) {
  const datos = leerJson('ids.json', contenido);
  assert.ok(esObjeto(datos), 'ids.json: se esperaba un mapa de workflows a IDs.');

  const ids = new Set();
  for (const [nombre, id] of Object.entries(datos)) {
    assert.ok(nombresWorkflow.has(nombre), 'ids.json: nombre de workflow fuera de C10.');
    assert.ok(exportsPresentes.includes(nombre), `ids.json: falta el export ${nombre}.`);
    assert.ok(typeof id === 'string' && id && id === id.trim(), `ids.json: ID inválido para ${nombre}.`);
    assert.ok(!ids.has(id), `ids.json: ID repetido en ${nombre}.`);
    ids.add(id);
  }
}

function validarExport(archivo, contenido) {
  assert.ok(nombresWorkflow.has(archivo), `${archivo}: nombre de workflow fuera de C10.`);
  const datos = leerJson(archivo, contenido);
  assert.ok(esObjeto(datos), `${archivo}: se esperaba un objeto de workflow.`);
  assert.ok(!Object.hasOwn(datos, 'pinData'), `${archivo}: elimina pinData antes de versionar el workflow.`);
  assert.ok(typeof datos.name === 'string' && datos.name.trim(), `${archivo}: el workflow requiere name.`);
  assert.ok(Array.isArray(datos.nodes) && datos.nodes.length > 0, `${archivo}: el workflow requiere nodes.`);
  assert.ok(esObjeto(datos.connections), `${archivo}: el workflow requiere connections.`);

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

function listarJson(directorio) {
  return readdirSync(directorio, { withFileTypes: true, recursive: true })
    .filter((entrada) => entrada.name.toLowerCase().endsWith('.json'))
    .map((entrada) => {
      const ruta = relative(directorio, join(entrada.parentPath, entrada.name));
      assert.ok(entrada.isFile() && dirname(ruta) === '.', `${ruta}: guarda el JSON directamente en n8n/.`);
      return entrada.name;
    });
}

const workflow = { name: 'Ingreso', nodes: [{}], connections: {} };

test('n8n acepta un workflow con referencias y un mapa de IDs válido', () => {
  validarExport('01-ingreso.json', JSON.stringify({
    ...workflow,
    nodes: [{ credentials: { postgres: { id: 'ejemplo', name: 'Postgres de prueba' } } }],
  }));
  validarIds('{"01-ingreso.json":"ejemplo"}', ['01-ingreso.json']);
});

test('n8n rechaza JSON inválido e indica el archivo', () => {
  assert.throws(() => validarExport('01-ingreso.json', '{'), /01-ingreso\.json: JSON inválido/);
});

test('n8n rechaza nombres fuera de C10 y exports incompletos', () => {
  assert.throws(() => validarExport('ingreso.json', '{}'), /nombre.*fuera de C10/);
  assert.throws(() => validarExport('01-ingreso.json', '{"nodes":[]}'), /requiere name/);
  assert.throws(() => validarExport('01-ingreso.json', '{"name":"Ingreso","nodes":[]}'), /requiere nodes/);
  assert.throws(() => validarExport('01-ingreso.json', '{"name":"Ingreso","nodes":[{}]}'), /requiere connections/);
});

test('n8n rechaza pinData incluso cuando está vacío', () => {
  assert.throws(() => validarExport('01-ingreso.json', '{"nodes":[],"pinData":{}}'), /elimina pinData/);
});

test('n8n rechaza datos de credenciales en lugar de referencias', () => {
  const contenido = JSON.stringify({
    ...workflow,
    nodes: [{ credentials: { postgres: { id: 'ejemplo', data: {} } } }],
  });
  assert.throws(() => validarExport('01-ingreso.json', contenido), /solo puede tener id y name/);
});

test('n8n rechaza IDs repetidos o asignados a un export ausente', () => {
  const mapa = '{"01-ingreso.json":"ejemplo","02-ausencias.json":"ejemplo"}';
  assert.throws(() => validarIds(mapa, ['01-ingreso.json', '02-ausencias.json']), /ID repetido/);
  assert.throws(() => validarIds(mapa, ['01-ingreso.json']), /falta el export 02-ausencias\.json/);
});

test('n8n identifica el BOM y rechaza exports en subdirectorios', (t) => {
  assert.throws(() => validarExport('01-ingreso.json', '\uFEFF{}'), /UTF-8 sin BOM/);

  const directorio = mkdtempSync(join(tmpdir(), 'portika-n8n-'));
  const carpeta = mkdirSync(join(directorio, 'prueba'), { recursive: true });
  const archivo = join(carpeta, '01-ingreso.json');
  writeFileSync(archivo, JSON.stringify(workflow));
  t.after(() => {
    unlinkSync(archivo);
    rmdirSync(carpeta);
    rmdirSync(directorio);
  });
  assert.throws(() => listarJson(directorio), /directamente en n8n/);
});

test('n8n valida los JSON versionados del repositorio', (t) => {
  const archivos = listarJson(directorioN8n);
  const exportsPresentes = archivos.filter((archivo) => archivo !== 'ids.json');
  if (exportsPresentes.length === 0) {
    t.diagnostic('Todavía no hay workflows exportados. Se ejecutaron los casos de prueba sintéticos.');
  }
  for (const archivo of exportsPresentes) {
    validarExport(archivo, readFileSync(join(directorioN8n, archivo), 'utf8'));
  }
  if (archivos.includes('ids.json')) {
    validarIds(readFileSync(join(directorioN8n, 'ids.json'), 'utf8'), exportsPresentes);
  }
});
