import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { test } from 'node:test';

const leer = (ruta) => readFileSync(new URL(ruta, import.meta.url), 'utf8');
const workflow = JSON.parse(leer('../n8n/03-justificativo.json'));
const nodosDeTipo = (tipo) => workflow.nodes.filter(({ type }) => type.endsWith(`.${tipo}`));
const nodo = (nombre) => workflow.nodes.find(({ name }) => name === nombre);
const evaluar = (expresion, json, resolver) => new Function('$json', '$',
    `return (${expresion.slice(3, -2)});`)(json, resolver);

test('WF3 tiene un solo Telegram Trigger para el bot del demo y conserva las ejecuciones fallidas', () => {
    assert.equal(workflow.name, 'WF3 · Justificativo');
    assert.equal(nodosDeTipo('telegramTrigger').length, 1);
    const [trigger] = nodosDeTipo('telegramTrigger');
    assert.deepEqual(trigger.parameters.updates, ['message']);
    for (const telegram of [trigger, ...nodosDeTipo('telegram')]) {
        assert.deepEqual(telegram.credentials, { telegramApi: { id: 'uCJxcnNOFfvYnRgN', name: 'Telegram Portika' } });
    }
    assert.equal(workflow.settings.saveDataErrorExecution, 'all');
    assert.equal(workflow.settings.saveDataSuccessExecution, 'none');
    assert.doesNotMatch(JSON.stringify(workflow), /"pinData"\s*:/);
});

test('WF3 separa los comandos, los justificativos y los formatos no admitidos', () => {
    const { output } = nodo('Clasificar mensaje').parameters;
    for (const [mensaje, salida] of [
        [{ text: '/start REP-014' }, 0],
        [{ text: '/start' }, 0],
        [{ text: '/start REP-14' }, 0],
        [{ text: '/start INSPECTOR-x' }, 1],
        [{ text: 'Faltó ayer' }, 2],
        [{ voice: { file_id: 'voz' } }, 2],
        [{ photo: [{ file_id: 'foto' }] }, 2],
        [{ text: '/ayuda' }, 3],
        [{ document: { file_id: 'documento' } }, 3],
    ]) {
        assert.equal(evaluar(output, { message: mensaje }), salida);
    }
    const { main } = workflow.connections['Clasificar mensaje'];
    assert.deepEqual(main.map(([{ node }]) => node), [
        'Vincular representante', 'Vincular inspector', 'Contexto', 'Formato no admitido',
    ]);
    assert.equal(nodo('Formato no admitido').parameters.text, 'Por ahora puedo recibir textos, notas de voz o fotos 🙂 ¿Nos cuentas por ahí?');
    assert.equal(workflow.connections['Formato no admitido'], undefined);
});

test('WF3 mantiene las consultas parametrizadas en archivos SQL', () => {
    const consultas = {
        'Vincular representante': 'wf3_vincular_representante.sql',
        'Vincular inspector': 'wf3_vincular_inspector.sql',
        Contexto: 'wf3_contexto.sql',
        Guardar: 'wf3_guardar.sql',
    };
    const archivos = readdirSync(new URL('./esquema/', import.meta.url))
        .filter((archivo) => /^wf3_.*\.sql$/.test(archivo));
    assert.deepEqual(archivos.sort(), Object.values(consultas).sort());
    const postgres = nodosDeTipo('postgres');
    assert.deepEqual(postgres.map(({ name }) => name).sort(), Object.keys(consultas).sort());
    for (const { name, parameters, typeVersion } of postgres) {
        assert.equal(typeVersion, 2.8);
        assert.equal(parameters.operation, 'executeQuery');
        assert.equal(parameters.query, leer(`./esquema/${consultas[name]}`));
        assert.doesNotMatch(parameters.query, /\{\{/);
        assert.match(parameters.options.queryReplacement, /^=\{\{ \[/);
    }
    const { query } = nodo('Vincular inspector').parameters;
    assert.match(query, /clave = 'portika_clave_inspector' and valor = \$1 and \$1 <> ''/);
    assert.match(query, /returning 1\s*\)\s*select exists \(select 1 from vinculo\) as vinculado;/i);

    const vincular = nodo('Vincular representante').parameters.options.queryReplacement;
    for (const [text, codigo] of [['/start', ''], ['/start REP-14', 'REP-14'], ['/start REP-014', 'REP-014']]) {
        const trigger = () => ({ first: () => ({ json: { message: { text, chat: { id: 42 } } } }) });
        assert.deepEqual(evaluar(vincular, {}, trigger), ['42', codigo]);
    }
    const guardar = nodo('Guardar').parameters.options.queryReplacement;
    assert.deepEqual(evaluar(guardar, {
        representante_codigo: 'REP-014', tipo_entrada: 'voz', foto_file_id: null, extraccion: null,
        validacion: { destino: 'revision_manual' },
    }), ['REP-014', 'voz', '', '', '', '{"destino":"revision_manual"}']);
});

test('WF3 copia los prompts y comparte el parser C5 y el modelo entre las cadenas', () => {
    const c5 = leer('../docs/contratos.md').split('## C5')[1].split('## C6')[0];
    const [, esquema] = c5.match(/```json\r?\n([\s\S]+?)\r?\n```/);
    assert.equal(nodosDeTipo('outputParserStructured').length, 1);
    const [parser] = nodosDeTipo('outputParserStructured');
    assert.equal(parser.parameters.schemaType, 'manual');
    assert.deepEqual(JSON.parse(parser.parameters.inputSchema), JSON.parse(esquema));

    const prompts = leer('../docs/prompts-wf3.md').replace(/\r\n/g, '\n');
    const [transcripcion, sistema, usuario] = Array.from(prompts.matchAll(/```text\n([\s\S]+?)\n```/g), (match) => match[1]);
    assert.equal(nodo('Transcribir voz').parameters.text, transcripcion);
    const cadenas = nodosDeTipo('chainLlm');
    assert.equal(cadenas.length, 2);
    for (const { parameters, onError } of cadenas) {
        assert.equal(onError, 'continueRegularOutput');
        assert.equal(parameters.hasOutputParser, true);
        assert.equal(parameters.text, `=${usuario}`);
        assert.equal(parameters.messages.messageValues[0].message, sistema);
    }
    for (const nombre of ['Descargar voz', 'Descargar foto', 'Transcribir voz']) {
        assert.equal(nodo(nombre).onError, 'continueRegularOutput');
    }
    assert.equal(nodo('Extraer foto').parameters.messages.messageValues[1].messageType, 'imageBinary');

    assert.equal(nodosDeTipo('lmChatGoogleGemini').length, 1);
    const [modelo] = nodosDeTipo('lmChatGoogleGemini');
    for (const gemini of [nodo('Transcribir voz'), modelo]) {
        assert.deepEqual(gemini.credentials, { googlePalmApi: { id: 'gdVTa7TydNuDeKj1', name: 'Gemini Portika' } });
    }
    for (const [nombre, tipo] of [[modelo.name, 'ai_languageModel'], [parser.name, 'ai_outputParser']]) {
        assert.deepEqual(workflow.connections[nombre][tipo].flat().map(({ node }) => node),
            cadenas.map(({ name }) => name));
    }
});

test('WF3 conecta nodos existentes y deja desactivado el envío a WF4', () => {
    for (const [origen, salidas] of Object.entries(workflow.connections)) {
        assert.ok(nodo(origen), origen);
        for (const { node } of Object.values(salidas).flat(2)) {
            assert.ok(nodo(node), node);
        }
    }
    assert.equal(nodosDeTipo('executeWorkflow').length, 1);
    const [wf4] = nodosDeTipo('executeWorkflow');
    assert.equal(wf4.type, 'n8n-nodes-base.executeWorkflow');
    assert.equal(wf4.disabled, true);
    assert.match(wf4.notes, /\bWF4\b/);
    const salidas = (origen) => workflow.connections[origen].main.map((salida) => salida.map(({ node }) => node));
    assert.deepEqual(salidas('Guardar'), [['Redactar respuesta']]);
    assert.deepEqual(salidas('Redactar respuesta'), [['Destino']]);
    assert.deepEqual(salidas('Destino'), [['Responder justificativo'], ['Responder justificativo', wf4.name]]);
    const { output } = nodo('Destino').parameters;
    assert.equal(evaluar(output, { destino: 'rechazado' }), 0);
    for (const destino of ['aprobacion', 'revision_manual']) {
        assert.equal(evaluar(output, { destino }), 1);
    }
    assert.equal(nodo('Responder justificativo').parameters.text, '={{ $json.respuesta }}');
});

test('WF3 conserva el contexto y envía fallas de medios o Gemini a C6 sin extracción', () => {
    const ejecutar = (nombre, item, anteriores) => {
        const resolver = (paso) => ({ first: () => ({ json: anteriores[paso] }) });
        return new Function('$json', '$input', '$', nodo(nombre).parameters.jsCode)(item.json, { item }, resolver);
    };
    const contexto = { representante_codigo: 'REP-001', hijos: [], faltas: [], fecha_demo: '2026-01-12', plazo_dias: null };
    const mensaje = { chat: { id: 10 }, photo: [{ file_id: 'pequena' }, { file_id: 'grande' }], caption: 'Constancia' };
    const { json: foto } = ejecutar('Preparar entrada', { json: contexto }, { 'Telegram Trigger': { message: mensaje } });
    assert.equal(foto.foto_file_id, 'grande');
    assert.equal(foto.mensaje_original, 'Constancia');

    const binario = { data: { mimeType: 'image/jpeg' } };
    const error = { error: 'Fallo de prueba' };
    const voz = { ...foto, tipo_entrada: 'voz', mensaje_original: '', foto_file_id: null };
    const transcripcion = { finishReason: 'STOP', content: { parts: [{ text: 'Faltó ayer' }] } };
    for (const [entrada, item, fuente, original] of [
        [foto, { json: {}, binary: binario }, 'foto', 'Constancia'],
        [foto, { json: error }, 'fallo', 'Constancia'],
        [voz, { json: transcripcion }, 'texto', 'Faltó ayer'],
        [voz, { json: { ...transcripcion, content: { parts: [{ text: '[inaudible]' }] } } }, 'fallo', '[inaudible]'],
        [voz, { json: error }, 'fallo', ''],
    ]) {
        const preparado = ejecutar('Preparar extracción', item, { 'Preparar entrada': entrada });
        assert.equal(preparado.json.fuente, fuente);
        if (fuente === 'foto') assert.equal(preparado.binary, binario);
        else assert.equal(Object.hasOwn(preparado, 'binary'), false);
        const { json } = ejecutar('Recuperar contexto', { json: error }, { 'Preparar extracción': preparado.json });
        assert.deepEqual(json, { ...entrada, mensaje_original: original, extraccion: null });
    }
    const salida = { estudiante_codigo: 'EST-014', fechas: ['2026-01-12'], motivo: 'salud', resumen: 'Consulta', confianza: 0.9 };
    const { json } = ejecutar('Recuperar contexto', { json: { output: salida } }, {
        'Preparar extracción': { ...foto, fuente: 'foto' },
    });
    assert.deepEqual(json, { ...foto, extraccion: salida });
});
