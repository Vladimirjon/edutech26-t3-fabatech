import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const leer = (ruta) => readFileSync(new URL(ruta, import.meta.url), 'utf8');
const contenidoCrudo = leer('../n8n/04-aprobacion.json');
const workflow = JSON.parse(contenidoCrudo);
const nodosDeTipo = (tipo) => workflow.nodes.filter(({ type }) => type === `n8n-nodes-base.${tipo}`);
const nodoPorNombre = (nombre) => workflow.nodes.find(({ name }) => name === nombre);

test('WF4 exporta metadata, settings y trigger subworkflow sin Telegram Trigger ni pinData', () => {
  assert.equal(workflow.name, 'WF4 · Aprobación');
  assert.equal(workflow.settings.timezone, 'America/Guayaquil');
  assert.equal(workflow.settings.executionOrder, 'v1');
  assert.equal(workflow.settings.saveDataErrorExecution, 'all');
  assert.equal(workflow.settings.saveDataSuccessExecution, 'none');
  assert.equal(workflow.settings.callerPolicy, 'workflowsFromSameOwner');
  assert.ok(!Object.hasOwn(workflow, 'pinData'));
  assert.doesNotMatch(contenidoCrudo, /"pinData"\s*:/);

  assert.equal(nodosDeTipo('telegramTrigger').length, 0);
  assert.equal(nodosDeTipo('executeWorkflowTrigger').length, 1);
  const [trigger] = nodosDeTipo('executeWorkflowTrigger');
  assert.equal(trigger.name, 'Cuando lo llame WF3');
  assert.equal(trigger.parameters.inputSource, 'workflowInputs');
  assert.deepEqual(trigger.parameters.workflowInputs.values, [{ name: 'id', type: 'any' }]);
});

test('WF4 usa solo credenciales de referencia permitidas y configura Telegram sin reintentos y con espera de 24 h', () => {
  assert.doesNotMatch(contenidoCrudo, /duIeqLZEdhdKH4TJ/);
  assert.doesNotMatch(contenidoCrudo, /Telegram Portika dev/);

  const credNodes = workflow.nodes.filter(({ credentials }) => credentials).map(({ name }) => name).sort();
  assert.deepEqual(credNodes, [
    'Aplicar decisión',
    'Avisar familia',
    'Cargar contexto',
    'Enviar foto',
    'Pedir aprobación',
  ]);

  for (const nombre of ['Cargar contexto', 'Aplicar decisión']) {
    const nodo = nodoPorNombre(nombre);
    assert.deepEqual(nodo.credentials, {
      postgres: { id: 'L7pCp0sFwXKrC2OB', name: 'Postgres Portika' },
    });
  }

  for (const nombre of ['Enviar foto', 'Pedir aprobación', 'Avisar familia']) {
    const nodo = nodoPorNombre(nombre);
    assert.deepEqual(nodo.credentials, {
      telegramApi: { id: 'uCJxcnNOFfvYnRgN', name: 'Telegram Portika' },
    });
    assert.equal(nodo.onError, 'continueRegularOutput');
    assert.ok(!nodo.retryOnFail);
  }

  assert.equal(nodoPorNombre('Enviar foto').parameters.additionalFields.appendAttribution, false);
  assert.equal(nodoPorNombre('Avisar familia').parameters.additionalFields.appendAttribution, false);

  const pedir = nodoPorNombre('Pedir aprobación');
  assert.equal(pedir.parameters.resource, 'message');
  assert.equal(pedir.parameters.operation, 'sendAndWait');
  assert.equal(pedir.parameters.responseType, 'approval');
  assert.equal(pedir.parameters.approvalOptions.values.approvalType, 'double');
  assert.equal(pedir.parameters.chatApproval, true);
  assert.equal(pedir.parameters.options.appendAttribution, false);
  assert.deepEqual(pedir.parameters.options.limitWaitTime.values, {
    limitType: 'afterTimeInterval',
    resumeAmount: 24,
    resumeUnit: 'hours',
  });
});

test('WF4 mantiene SQL parametrizado sincronizado y un único CTE idempotente con auditoría y eventos', () => {
  const postgres = nodosDeTipo('postgres');
  assert.equal(postgres.length, 2);

  const contexto = nodoPorNombre('Cargar contexto');
  const decision = nodoPorNombre('Aplicar decisión');

  for (const nodo of postgres) {
    assert.equal(nodo.typeVersion, 2.8);
    assert.equal(nodo.parameters.operation, 'executeQuery');
    assert.doesNotMatch(nodo.parameters.query, /\{\{/);
    assert.match(nodo.parameters.options.queryReplacement, /^=\{\{ \[/);
  }

  assert.equal(contexto.parameters.query, leer('./esquema/wf4_contexto.sql'));
  assert.equal(decision.parameters.query, leer('./esquema/wf4_decision.sql'));

  const qCtx = contexto.parameters.query;
  assert.match(qCtx, /\$1::text ~ '\^\\d\+\$'/);
  assert.match(qCtx, /clave = 'inspector_chat_id'/);
  assert.match(qCtx, /telegram_chat_id::text/);

  const qDec = decision.parameters.query;
  assert.match(qDec, /for update of j/i);
  assert.match(qDec, /estado in \('pendiente',\s*'revision_manual'\)/i);
  assert.match(qDec, /update public\.justificativos/i);
  assert.match(qDec, /update public\.faltas/i);
  assert.match(qDec, /insert into public\.eventos_tablero\s*\(tipo,\s*curso,\s*paralelo\)/i);
  assert.match(qDec, /insert into public\.auditoria\s*\(actor,\s*accion,\s*entidad,\s*entidad_id,\s*detalle\)/i);
  assert.match(qDec, /'inspector:' \|\|/i);
  assert.match(qDec, /from \(values \(1\)\)/i);
});

test('WF4 conecta nodos existentes, converge en Pedir aprobación y protege timeout/doble clic', () => {
  const nombres = new Set(workflow.nodes.map(({ name }) => name));
  for (const [origen, salidas] of Object.entries(workflow.connections)) {
    assert.ok(nombres.has(origen), origen);
    for (const { node } of Object.values(salidas).flat(2)) {
      assert.ok(nombres.has(node), node);
    }
  }

  const salidas = (origen) => workflow.connections[origen].main.map((rama) => rama.map(({ node }) => node));
  assert.deepEqual(salidas('Cuando lo llame WF3'), [['Cargar contexto']]);
  assert.deepEqual(salidas('Cargar contexto'), [['Listo para revisar?']]);
  assert.deepEqual(salidas('Listo para revisar?'), [['Preparar mensaje inspector']]);
  assert.deepEqual(salidas('Preparar mensaje inspector'), [['Tiene foto?']]);
  assert.deepEqual(salidas('Tiene foto?'), [['Enviar foto'], ['Pedir aprobación']]);
  assert.deepEqual(salidas('Enviar foto'), [['Pedir aprobación']]);
  assert.deepEqual(salidas('Pedir aprobación'), [['Decisión recibida?']]);
  assert.deepEqual(salidas('Decisión recibida?'), [['Aplicar decisión']]);
  assert.deepEqual(salidas('Aplicar decisión'), [['Avisar familia?']]);
  assert.deepEqual(salidas('Avisar familia?'), [['Preparar aviso familia']]);
  assert.deepEqual(salidas('Preparar aviso familia'), [['Avisar familia']]);

  const decisionIf = nodoPorNombre('Decisión recibida?');
  assert.match(
    decisionIf.parameters.conditions.conditions[0].leftValue,
    /typeof \$json\.data\?\.approved === 'boolean'/,
  );

  const avisarIf = nodoPorNombre('Avisar familia?');
  assert.match(
    avisarIf.parameters.conditions.conditions[0].leftValue,
    /aplicado === true && Boolean\(/,
  );
});

test('Preparar mensaje inspector formatea resumen, revisión manual, foto y escapa Markdown v1', () => {
  const nodo = nodoPorNombre('Preparar mensaje inspector');
  assert.equal(nodo.parameters.mode, 'runOnceForEachItem');
  const correr = (json) => new Function('$json', nodo.parameters.jsCode)(json).json;

  const conFoto = correr({
    id: '42',
    estado: 'pendiente',
    foto_file_id: 'FILE_123',
    inspector_chat_id: '777001',
    estudiante_codigo: 'EST-014',
    estudiante_nombre: 'Luciana Vásconez',
    curso: '8vo EGB',
    paralelo: 'A',
    extraccion: { motivo: 'salud', resumen: 'Consulta pediátrica' },
    validacion: {
      fechas: ['2026-01-12'],
      reglas: [
        { id: 'R1', ok: true, detalle: 'EST-014 es hijo del representante' },
        { id: 'R4', ok: true, detalle: 'Confianza 0.92 (mínimo 0.6)' },
      ],
    },
  });
  assert.equal(conFoto.tiene_foto, true);
  assert.equal(conFoto.es_revision_manual, false);
  assert.doesNotMatch(conFoto.mensaje, /REVISIÓN MANUAL/);
  assert.match(conFoto.mensaje, /Luciana Vásconez \(EST-014\)/);
  assert.match(conFoto.mensaje, /8vo EGB A/);
  assert.match(conFoto.mensaje, /2026-01-12/);
  assert.match(conFoto.mensaje, /Salud — Consulta pediátrica/);
  assert.match(conFoto.mensaje, /Foto adjunta: Sí/);
  assert.match(conFoto.mensaje, /✅ R1: EST-014 es hijo del representante/);

  const sinFoto = correr({
    id: '43',
    estado: 'pendiente',
    foto_file_id: null,
    inspector_chat_id: '777001',
    estudiante_codigo: 'EST-015',
    estudiante_nombre: 'Emilio Navarrete',
    curso: '9no EGB',
    paralelo: 'B',
    extraccion: { motivo: 'tramite', resumen: 'Trámite consular' },
    validacion: { fechas: ['2026-01-12'], reglas: [] },
  });
  assert.equal(sinFoto.tiene_foto, false);
  assert.match(sinFoto.mensaje, /Foto adjunta: No/);

  const revisionSinDatos = correr({
    id: '44',
    estado: 'revision_manual',
    foto_file_id: '',
    inspector_chat_id: '777001',
    estudiante_codigo: null,
    estudiante_nombre: null,
    curso: null,
    paralelo: null,
    mensaje_original: 'Faltó_ayer *urgente* `[ver]`',
    extraccion: null,
    validacion: {
      fechas: [],
      fechas_pedidas: [],
      reglas: [{ id: 'C5', ok: false, detalle: 'estudiante_codigo_invalido' }],
    },
  });
  assert.equal(revisionSinDatos.es_revision_manual, true);
  assert.equal(revisionSinDatos.tiene_foto, false);
  assert.match(revisionSinDatos.mensaje, /⚠️ \*REVISIÓN MANUAL\*/);
  assert.match(revisionSinDatos.mensaje, /Estudiante: No identificado/);
  assert.match(revisionSinDatos.mensaje, /Curso: No identificado/);
  assert.match(revisionSinDatos.mensaje, /Fechas: Sin fechas/);
  assert.match(revisionSinDatos.mensaje, /Faltó\\_ayer \\\*urgente\\\* \\`\\\[ver\]/);
  assert.match(revisionSinDatos.mensaje, /❌ C5: estudiante\\_codigo\\_invalido/);
});

test('Preparar aviso familia emite texto exacto en aprobación y mensaje cálido <=300 chars en rechazo', () => {
  const nodo = nodoPorNombre('Preparar aviso familia');
  assert.equal(nodo.parameters.mode, 'runOnceForEachItem');
  const correr = (json) => new Function('$json', nodo.parameters.jsCode)(json).json;

  const aprobado = correr({
    aplicado: true,
    decision: 'aprobado',
    telegram_chat_id: '888014',
    estudiante_nombre: 'Luciana Vásconez',
    fechas: ['2026-01-12'],
    motivo: 'salud',
  });
  assert.equal(aprobado.telegram_chat_id, '888014');
  assert.equal(aprobado.mensaje, 'Tu justificativo fue aprobado');

  const rechazado = correr({
    aplicado: true,
    decision: 'rechazado',
    telegram_chat_id: '888015',
    estudiante_nombre: 'Emilio Navarrete',
    fechas: ['2026-01-12'],
    motivo: 'otro',
  });
  assert.ok(rechazado.mensaje.length <= 300);
  assert.match(rechazado.mensaje, /Emilio/);
  assert.match(rechazado.mensaje, /lunes 12 de enero/);
  assert.match(rechazado.mensaje, /inspección te atiende con gusto/i);

  const rechazadoVarias = correr({
    aplicado: true,
    decision: 'rechazado',
    telegram_chat_id: '888015',
    estudiante_nombre: 'Emilio Navarrete',
    fechas: ['2026-01-05', '2026-01-06', '2026-01-07', '2026-01-08', '2026-01-09', '2026-01-12', '2026-01-13'],
    motivo: 'otro',
  });
  assert.ok(rechazadoVarias.mensaje.length <= 300);
  assert.match(rechazadoVarias.mensaje, /y 6 más/);

  const rechazadoSinDatos = correr({
    aplicado: true,
    decision: 'rechazado',
    telegram_chat_id: '888016',
    estudiante_nombre: null,
    fechas: [],
    motivo: null,
  });
  assert.ok(rechazadoSinDatos.mensaje.length <= 300);
  assert.doesNotMatch(rechazadoSinDatos.mensaje, /null|undefined/);
});
