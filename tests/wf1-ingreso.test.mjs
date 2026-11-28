import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const workflow = JSON.parse(readFileSync(new URL('../n8n/01-ingreso.json', import.meta.url), 'utf8'));
const nodosDeTipo = (tipo) => workflow.nodes.filter(({ type }) => type === `n8n-nodes-base.${tipo}`);

test('WF1 exporta un webhook POST con el CORS de Pórtika', () => {
    assert.equal(workflow.name, 'WF1 · Ingreso');
    assert.equal(nodosDeTipo('webhook').length, 1);
    const { parameters } = nodosDeTipo('webhook')[0];
    assert.equal(parameters.httpMethod, 'POST');
    assert.equal(parameters.path, 'portika/ingreso');
    assert.equal(parameters.responseMode, 'responseNode');
    assert.equal(parameters.options.allowedOrigins, 'https://portika.vercel.app');
});

test('WF1 usa un único Postgres con una referencia y parámetros del request', () => {
    assert.equal(nodosDeTipo('postgres').length, 1);
    const [postgres] = nodosDeTipo('postgres');
    assert.deepEqual(workflow.nodes.filter(({ credentials }) => credentials), [postgres]);
    assert.deepEqual(Object.keys(postgres.credentials), ['postgres']);
    const credencial = postgres.credentials.postgres;
    assert.deepEqual(Object.keys(credencial).sort(), ['id', 'name']);
    assert.equal(typeof credencial.id, 'string');
    assert.ok(credencial.id.trim());
    assert.equal(credencial.name, 'Postgres Portika');
    assert.doesNotMatch(JSON.stringify(workflow), /"pinData"\s*:/);

    const { operation, query, options } = postgres.parameters;
    assert.equal(operation, 'executeQuery');
    assert.equal(query, readFileSync(new URL('./esquema/wf1_ingreso.sql', import.meta.url), 'utf8'));
    assert.match(query, /clave = 'portika_clave_dispositivo' and valor = \$1\b/);
    assert.match(query, /\$2\b/);
    assert.doesNotMatch(query, /\{\{/);
    const parametros = [
        "String($json.headers?.['x-portika-clave'] ?? '')",
        "String($json.body?.carne_token ?? '')",
        "String($json.body?.escaneado_en ?? '')",
        "String($json.body?.origen ?? '')",
    ];
    assert.equal(options.queryReplacement, `={{ [ ${parametros.join(', ')} ] }}`);
});

test('WF1 conecta cuatro respuestas con los códigos de C2', () => {
    const respuestas = nodosDeTipo('respondToWebhook');
    assert.deepEqual(respuestas.map(({ name, parameters }) => [
        name, parameters.options.responseCode,
    ]), [
        ['no_autorizado', 401],
        ['carne_desconocido', 404],
        ['registrado', 200],
        ['duplicado', 200],
    ]);

    const nombres = new Set(workflow.nodes.map(({ name }) => name));
    for (const [origen, salidas] of Object.entries(workflow.connections)) {
        assert.ok(nombres.has(origen), origen);
        for (const { node } of Object.values(salidas).flat(2)) {
            assert.ok(nombres.has(node), node);
        }
    }
    const [webhook] = nodosDeTipo('webhook');
    const [postgres] = nodosDeTipo('postgres');
    const [selector] = nodosDeTipo('switch');
    assert.deepEqual(workflow.connections[webhook.name].main, [[{ node: postgres.name, type: 'main', index: 0 }]]);
    assert.deepEqual(workflow.connections[postgres.name].main, [[{ node: selector.name, type: 'main', index: 0 }]]);
    const estados = ['no_autorizado', 'carne_desconocido', 'registrado', 'duplicado'];
    assert.equal(selector.parameters.output, `={{ ${JSON.stringify(estados)}.indexOf($json.estado) }}`);
    assert.deepEqual(workflow.connections[selector.name].main.map(([{ node }]) => node),
        estados);

    const [, , registrado, duplicado] = respuestas;
    assert.match(registrado.parameters.responseBody, /\bhora: \$json\.hora\b/);
    assert.doesNotMatch(registrado.parameters.responseBody, /\bhora_original\b/);
    assert.match(duplicado.parameters.responseBody, /\bhora_original: \$json\.hora\b/);
    assert.doesNotMatch(duplicado.parameters.responseBody, /\bhora:/);
});

test('WF1 guarda las ejecuciones fallidas y omite las exitosas', () => {
    assert.equal(workflow.settings.saveDataErrorExecution, 'all');
    assert.equal(workflow.settings.saveDataSuccessExecution, 'none');
});
