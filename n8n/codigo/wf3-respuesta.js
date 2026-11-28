// WF3 · Nodo «Redactar respuesta», modo «Run Once for Each Item».
const { hijos, extraccion, validacion, plazo_dias } = $('Reglas C6').item.json;
const { id, destino } = $json;

const dias = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
  'septiembre', 'octubre', 'noviembre', 'diciembre'];
const saludos = ['Gracias por avisarnos 🙏', 'Gracias por contarnos 🙏',
  'Recibimos tu mensaje, gracias por escribir 🙏'];
const motivos = {
  salud: ['por salud', '¡Que se mejore pronto! 💙'],
  calamidad_domestica: ['por una calamidad doméstica', 'Lamentamos mucho lo que están pasando; cuenten con nosotros 🤍'],
  transporte: ['por un problema de transporte'],
  tramite: ['por un trámite'],
};

function fechaEnPalabras(fecha) {
  const dia = new Date(fecha + 'T00:00:00Z');
  return `el ${dias[dia.getUTCDay()]} ${dia.getUTCDate()} de ${meses[dia.getUTCMonth()]}`;
}

function conFechas(fechas, redactar) {
  const enPalabras = fechas.map(fechaEnPalabras);
  const lista = [enPalabras.slice(0, -1).join(', '), enPalabras.at(-1)].filter(Boolean).join(' y ');
  const mensaje = redactar(lista);
  if (mensaje.length <= 300 || fechas.length < 2) return mensaje;
  return redactar(`${enPalabras[0]} y ${fechas.length - 1} más`);
}

const saludo = saludos[Number(BigInt(id) % BigInt(saludos.length))];
const hijo = hijos.find(({ codigo }) => codigo === validacion.estudiante_codigo);
const nombre = hijo?.nombre_ficticio?.trim().split(/\s+/)[0].slice(0, 40);
const claveMotivo = extraccion?.motivo;
const [motivo, cierre] = Object.hasOwn(motivos, claveMotivo) ? motivos[claveMotivo] : [];
const despedida = cierre ? ` ${cierre}` : '';

let respuesta;
if (destino === 'aprobacion') {
  const motivoTexto = motivo ? ` ${motivo}` : '';
  respuesta = conFechas(validacion.fechas, (fechas) =>
    `${saludo} Registramos que ${nombre || 'tu hijo o hija'} faltó ${fechas}${motivoTexto}. Inspección lo revisará y te confirmaremos aquí.${despedida}`);
} else if (destino === 'revision_manual') {
  const persona = nombre ? `, sobre ${nombre},` : '';
  respuesta = `${saludo} Una persona de inspección revisará tu mensaje${persona} con calma y te responderá aquí.${despedida}`;
} else {
  const ayuda = 'Si necesitas ayuda, inspección te atiende con gusto en el colegio.';
  // R3 ya identifica las fechas que causaron el rechazo y da prioridad a las futuras.
  const detalle = validacion.reglas.find(({ id }) => id === 'R3')?.detalle ?? '';
  const fechasR3 = detalle.split(': ')[1]?.split(', ') ?? [];
  const fechas = validacion.fechas_pedidas.filter((fecha) => fechasR3.includes(fecha));
  if (fechas.length === 0) {
    respuesta = `${saludo} Por ahora no podemos registrar el justificativo. ${ayuda}`;
  } else if (detalle.startsWith('Fechas futuras:')) {
    respuesta = conFechas(fechas, (lista) => fechas.length === 1
      ? `${saludo} Todavía no ha llegado ${lista}; puedes escribirnos ese día. ${ayuda}`
      : `${saludo} Todavía no han llegado las fechas (${lista}). Puedes escribirnos cuando llegue cada una. ${ayuda}`);
  } else {
    const plazo = /^\d+$/.test(String(plazo_dias ?? '').trim()) ? Number(plazo_dias) : NaN;
    const diasHabiles = Number.isInteger(plazo) ? plazo : 3;
    respuesta = conFechas(fechas, (lista) =>
      `${saludo} Para ${lista} ya pasó el plazo de ${diasHabiles} días hábiles para justificar. ${ayuda}`);
  }
}

return { json: { ...$json, respuesta } };
