import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const leer = (ruta) => readFileSync(new URL(ruta, import.meta.url), 'utf8');
const codigo = leer('../n8n/codigo/wf3-respuesta.js');
const redactar = new Function('$json', '$', codigo);
const validar = new Function('$json', leer('../n8n/codigo/c6-reglas.js'));

function correr({ id = '3', fechas = ['2026-01-12'], motivo = 'salud', plazo_dias, estudiante = true } = {}) {
    const entrada = validar({
        hijos: estudiante ? [{ codigo: 'EST-014', nombre_ficticio: 'Ana Lucía' }] : [],
        faltas: fechas.map((fecha) => ({ estudiante_codigo: 'EST-014', estado: 'injustificada', fecha })),
        extraccion: { estudiante_codigo: estudiante ? 'EST-014' : null, motivo, fechas, resumen: 'Aviso', confianza: 0.9 },
        fecha_demo: '2026-01-12',
        plazo_dias,
    }).json;
    return redactar({ id, destino: entrada.validacion.destino }, (nodo) => {
        assert.equal(nodo, 'Reglas C6');
        return { item: { json: entrada } };
    }).json;
}

test('el nodo Redactar respuesta usa este mismo código y conserva el id y el destino', () => {
    const exportado = JSON.parse(leer('../n8n/03-justificativo.json'));
    const nodo = exportado.nodes.find(({ name }) => name === 'Redactar respuesta');
    assert.equal(nodo.type, 'n8n-nodes-base.code');
    assert.equal(nodo.parameters.mode, 'runOnceForEachItem');
    assert.equal(nodo.parameters.jsCode.replace(/\r\n/g, '\n'), codigo.replace(/\r\n/g, '\n'));
    assert.equal(correr().id, '3');
    assert.equal(correr().destino, 'aprobacion');
});

test('aprobación por salud personaliza con el primer nombre, la fecha y un cierre', () => {
    const { respuesta } = correr();
    assert.match(respuesta, /Ana faltó el lunes 12 de enero por salud/);
    assert.match(respuesta, /¡Que se mejore pronto! 💙$/);
});

test('revisión manual sin estudiante evita un nombre inventado y conserva el cierre', () => {
    const { destino, respuesta } = correr({ id: '4', estudiante: false, motivo: 'calamidad_domestica' });
    assert.equal(destino, 'revision_manual');
    assert.match(respuesta, /revisará tu mensaje con calma y te responderá aquí/);
    assert.match(respuesta, /Lamentamos mucho lo que están pasando/);
});

test('rechazo por plazo explica la fecha tardía con el plazo configurado o el de 3 días', () => {
    for (const [plazo_dias, plazo] of [[undefined, 3], ['2', 2]]) {
        const { destino, respuesta } = correr({ fechas: ['2026-01-05', '2026-01-12'], plazo_dias });
        assert.equal(destino, 'rechazado');
        assert.ok(respuesta.includes(`el lunes 5 de enero ya pasó el plazo de ${plazo} días hábiles`));
        assert.doesNotMatch(respuesta, /12 de enero/);
    }
});

test('rechazo por fecha futura respeta la prioridad de R3 si también hay fechas tardías', () => {
    const { destino, respuesta } = correr({ fechas: ['2026-01-05', '2026-01-13'] });
    assert.equal(destino, 'rechazado');
    assert.match(respuesta, /Todavía no ha llegado el martes 13 de enero; puedes escribirnos ese día/);
    assert.doesNotMatch(respuesta, /5 de enero/);
});

test('enumera dos fechas con y, y abrevia una lista larga para no superar 300 caracteres', () => {
    const dos = correr({ fechas: ['2026-01-09', '2026-01-12'], motivo: 'transporte' });
    assert.match(dos.respuesta, /el viernes 9 de enero y el lunes 12 de enero por un problema de transporte/);
    const fechas = Array.from({ length: 12 }, (_, i) => `2026-01-${String(i + 1).padStart(2, '0')}`);
    const muchas = correr({ fechas, plazo_dias: 20, motivo: 'calamidad_domestica' });
    assert.ok(muchas.respuesta.length <= 300);
    assert.match(muchas.respuesta, /el jueves 1 de enero y 11 más/);
    assert.match(muchas.respuesta, /🤍$/u);
});

test('el id elige un saludo distinto de forma determinista', () => {
    assert.match(correr({ id: '3' }).respuesta, /^Gracias por avisarnos 🙏/);
    assert.match(correr({ id: '4' }).respuesta, /^Gracias por contarnos 🙏/);
    assert.match(correr({ id: '5' }).respuesta, /^Recibimos tu mensaje, gracias por escribir 🙏/);
});
