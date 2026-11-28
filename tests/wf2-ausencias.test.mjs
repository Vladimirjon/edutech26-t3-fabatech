import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const contenidoCrudo = readFileSync(new URL('../n8n/02-ausencias.json', import.meta.url), 'utf8');
const workflow = JSON.parse(contenidoCrudo);
const nodosDeTipo = (tipo) => workflow.nodes.filter(({ type }) => type === `n8n-nodes-base.${tipo}`);
const nodoPorNombre = (nombre) => workflow.nodes.find(({ name }) => name === nombre);

test('WF2 exporta metadata, settings y disparadores conforme a C0 y C3', () => {
  assert.equal(workflow.name, 'WF2 · Ausencias');
  assert.equal(workflow.settings.timezone, 'America/Guayaquil');
  assert.equal(workflow.settings.executionOrder, 'v1');
  assert.equal(workflow.settings.saveDataErrorExecution, 'all');
  assert.equal(workflow.settings.saveDataSuccessExecution, 'all');
  assert.ok(!Object.hasOwn(workflow, 'pinData'));
  assert.doesNotMatch(contenidoCrudo, /"pinData"\s*:/);

  assert.equal(nodosDeTipo('webhook').length, 1);
  const [webhook] = nodosDeTipo('webhook');
  assert.equal(webhook.parameters.httpMethod, 'POST');
  assert.equal(webhook.parameters.path, 'portika/cierre');
  assert.equal(webhook.parameters.responseMode, 'responseNode');
  assert.equal(webhook.parameters.options.allowedOrigins, 'https://portika.vercel.app');

  assert.equal(nodosDeTipo('scheduleTrigger').length, 1);
  const [schedule] = nodosDeTipo('scheduleTrigger');
  assert.deepEqual(schedule.parameters.rule.interval, [
    { field: 'cronExpression', expression: '30 7 * * 1-5' },
  ]);
});

test('WF2 usa credenciales de referencia y un único CTE atómico en Postgres', () => {
  assert.equal(nodosDeTipo('postgres').length, 1);
  assert.equal(nodosDeTipo('telegram').length, 1);
  const [postgres] = nodosDeTipo('postgres');
  const [telegram] = nodosDeTipo('telegram');

  assert.deepEqual(
    workflow.nodes.filter(({ credentials }) => credentials).map(({ name }) => name).sort(),
    ['Postgres', 'Telegram'],
  );

  assert.deepEqual(Object.keys(postgres.credentials), ['postgres']);
  assert.deepEqual(Object.keys(postgres.credentials.postgres).sort(), ['id', 'name']);
  assert.equal(postgres.credentials.postgres.name, 'Postgres Portika');
  assert.ok(postgres.credentials.postgres.id.trim());

  assert.deepEqual(Object.keys(telegram.credentials), ['telegramApi']);
  assert.deepEqual(Object.keys(telegram.credentials.telegramApi).sort(), ['id', 'name']);
  assert.equal(telegram.credentials.telegramApi.name, 'Telegram Portika dev');
  assert.ok(telegram.credentials.telegramApi.id.trim());
  assert.equal(telegram.parameters.resource, 'message');
  assert.equal(telegram.parameters.operation, 'sendMessage');
  assert.equal(telegram.parameters.additionalFields.appendAttribution, false);

  const { operation, query, options } = postgres.parameters;
  assert.equal(operation, 'executeQuery');
  assert.equal(options.queryReplacement, '={{ [ $json.clave, $json.fecha, $json.es_webhook ] }}');
  assert.match(query, /clave = 'portika_clave_dispositivo'/);
  assert.match(query, /not \$3::boolean/);
  assert.match(query, /e\.codigo <> 'EST-999'/);
  assert.match(query, /e\.curso <> 'PRUEBA'/);
  assert.doesNotMatch(query, /e\.activo/);
  assert.match(query, /insert into public\.faltas\s*\(estudiante_codigo,\s*fecha,\s*estado\)/);
  assert.match(query, /on conflict \(estudiante_codigo,\s*fecha\) do nothing/);
  assert.match(query, /insert into public\.eventos_tablero\s*\(tipo,\s*curso,\s*paralelo\)/);
  assert.match(query, /insert into public\.auditoria\s*\(actor,\s*accion,\s*entidad,\s*entidad_id\)/);
  assert.match(query, /'sistema:WF2'/);
  assert.match(query, /from \(values \(1\)\)/);
  assert.doesNotMatch(query, /\{\{/);
});

test('WF2 conecta ramas de autorización, Telegram y respuesta condicional sin doble serialización', () => {
  const nombres = new Set(workflow.nodes.map(({ name }) => name));
  for (const [origen, salidas] of Object.entries(workflow.connections)) {
    assert.ok(nombres.has(origen), origen);
    for (const { node } of Object.values(salidas).flat(2)) {
      assert.ok(nombres.has(node), node);
    }
  }

  assert.deepEqual(workflow.connections.Webhook.main, [[{ node: 'Entrada', type: 'main', index: 0 }]]);
  assert.deepEqual(workflow.connections['Schedule Trigger'].main, [[{ node: 'Entrada', type: 'main', index: 0 }]]);
  assert.deepEqual(workflow.connections.Entrada.main, [[{ node: 'Postgres', type: 'main', index: 0 }]]);
  assert.deepEqual(workflow.connections.Postgres.main, [[{ node: 'Autorizado?', type: 'main', index: 0 }]]);
  assert.deepEqual(workflow.connections['Autorizado?'].main, [
    [{ node: 'No autorizado', type: 'main', index: 0 }],
    [{ node: 'Agrupar Familias', type: 'main', index: 0 }],
  ]);
  assert.deepEqual(workflow.connections['Agrupar Familias'].main, [[
    { node: 'Split Out', type: 'main', index: 0 },
    { node: 'Es Webhook?', type: 'main', index: 0 },
  ]]);
  assert.deepEqual(workflow.connections['Split Out'].main, [[{ node: 'Telegram', type: 'main', index: 0 }]]);
  assert.deepEqual(workflow.connections['Es Webhook?'].main, [[{ node: 'Responder cierre', type: 'main', index: 0 }]]);

  const splitOut = nodoPorNombre('Split Out');
  assert.equal(splitOut.parameters.fieldToSplitOut, 'envios');
  assert.equal(splitOut.parameters.include, 'noOtherFields');

  const noAutorizado = nodoPorNombre('No autorizado');
  assert.equal(noAutorizado.parameters.respondWith, 'json');
  assert.equal(noAutorizado.parameters.options.responseCode, 401);
  assert.doesNotMatch(String(noAutorizado.parameters.responseBody), /JSON\.stringify/);

  const responderCierre = nodoPorNombre('Responder cierre');
  assert.equal(responderCierre.parameters.respondWith, 'json');
  assert.equal(responderCierre.parameters.options.responseCode, 200);
  assert.doesNotMatch(String(responderCierre.parameters.responseBody), /JSON\.stringify/);
});

test('Entrada distingue Webhook vs Schedule y valida fecha AAAA-MM-DD', () => {
  const entrada = nodoPorNombre('Entrada');
  assert.equal(entrada.parameters.mode, 'runOnceForEachItem');
  const correrEntrada = (json) => new Function('$json', entrada.parameters.jsCode)(json).json;

  assert.deepEqual(
    correrEntrada({ headers: { 'X-Portika-Clave': 'secreto' }, body: { fecha: '2026-01-12' } }),
    { es_webhook: true, fecha: '2026-01-12', clave: 'secreto' },
  );
  assert.deepEqual(
    correrEntrada({ headers: { 'x-portika-clave': 's2' }, body: { fecha: '2026-02-30' } }),
    { es_webhook: true, fecha: null, clave: 's2' },
  );
  assert.deepEqual(
    correrEntrada({ headers: {}, body: {} }),
    { es_webhook: true, fecha: null, clave: '' },
  );

  const sched = correrEntrada({ timestamp: '2026-01-12T12:30:00Z' });
  assert.equal(sched.es_webhook, false);
  assert.equal(sched.clave, '');
  assert.match(sched.fecha, /^\d{4}-\d{2}-\d{2}$/);
});

test('Agrupar Familias agrupa hermanos, cuenta sin_contacto y formatea C3', () => {
  const agrupar = nodoPorNombre('Agrupar Familias');
  assert.equal(agrupar.parameters.mode, 'runOnceForAllItems');

  const correrAgrupar = (filas, es_webhook = true) => {
    const $input = { all: () => filas.map((json) => ({ json })) };
    const $ = (nombre) => {
      assert.equal(nombre, 'Entrada');
      return { first: () => ({ json: { es_webhook } }) };
    };
    return new Function('$input', '$', agrupar.parameters.jsCode)($input, $)[0].json;
  };

  assert.deepEqual(
    correrAgrupar([{ autorizado: true, estudiante_codigo: null, fecha: null, representante_codigo: null, telegram_chat_id: null }], true),
    { es_webhook: true, faltas_creadas: 0, mensajes_enviados: 0, sin_contacto: 0, envios: [] },
  );

  const ejemploC3 = correrAgrupar([
    { autorizado: true, estudiante_codigo: 'EST-014', fecha: '2026-01-12', representante_codigo: 'REP-014', telegram_chat_id: '999001' },
  ]);
  assert.equal(ejemploC3.faltas_creadas, 1);
  assert.equal(ejemploC3.mensajes_enviados, 1);
  assert.equal(ejemploC3.sin_contacto, 0);
  assert.equal(
    ejemploC3.envios[0].mensaje,
    'Hola, en Pórtika no registramos el ingreso de EST-014 hoy 12 de enero. Si faltó por un motivo, respóndenos aquí con un texto, una nota de voz o la foto del justificativo.',
  );

  const hermanosYSinContacto = correrAgrupar([
    { autorizado: true, estudiante_codigo: 'EST-007', fecha: '2026-01-05', representante_codigo: 'REP-006', telegram_chat_id: '999006' },
    { autorizado: true, estudiante_codigo: 'EST-006', fecha: '2026-01-05', representante_codigo: 'REP-006', telegram_chat_id: '999006' },
    { autorizado: true, estudiante_codigo: 'EST-010', fecha: '2026-01-05', representante_codigo: 'REP-010', telegram_chat_id: null },
  ], false);
  assert.equal(hermanosYSinContacto.es_webhook, false);
  assert.equal(hermanosYSinContacto.faltas_creadas, 3);
  assert.equal(hermanosYSinContacto.mensajes_enviados, 1);
  assert.equal(hermanosYSinContacto.sin_contacto, 1);
  assert.equal(
    hermanosYSinContacto.envios[0].mensaje,
    'Hola, en Pórtika no registramos el ingreso de EST-006 y EST-007 hoy 5 de enero. Si faltó por un motivo, respóndenos aquí con un texto, una nota de voz o la foto del justificativo.',
  );
});
