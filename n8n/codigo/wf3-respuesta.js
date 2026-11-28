// WF3 · Nodo «Redactar respuesta», modo «Run Once for Each Item».
const { hijos, extraccion, validacion, fecha_demo, plazo_dias } = $('Reglas C6').item.json;
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

function conFechas(fechas, redactar, maximo = 300) {
  const enPalabras = fechas.map(fechaEnPalabras);
  const lista = [enPalabras.slice(0, -1).join(', '), enPalabras.at(-1)].filter(Boolean).join(' y ');
  const mensaje = redactar(lista);
  if (mensaje.length <= maximo || fechas.length < 2) return mensaje;
  return redactar(`${enPalabras[0]} y ${fechas.length - 1} más`);
}

function dentroDelPlazo(fecha, hoy, plazo) {
  const dia = new Date(fecha + 'T00:00:00Z');
  const fin = new Date(hoy + 'T00:00:00Z');
  let habiles = 0;
  while (dia < fin && habiles <= plazo) {
    dia.setUTCDate(dia.getUTCDate() + 1);
    if (dia.getUTCDay() !== 0 && dia.getUTCDay() !== 6) habiles++;
  }
  return habiles <= plazo;
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
  const lecturaFiable = validacion.reglas.some(({ id, ok }) => id === 'R4' && ok === true);
  respuesta = `${saludo} Una persona de inspección revisará tu mensaje${persona} con calma y te responderá aquí.${lecturaFiable ? despedida : ''}`;
} else {
  const ayuda = ' Si necesitas ayuda, inspección te atiende con gusto en el colegio.';
  // R3 ya identifica las fechas que causaron el rechazo y da prioridad a las futuras.
  const detalle = validacion.reglas.find(({ id }) => id === 'R3')?.detalle ?? '';
  const fechasR3 = detalle.split(': ')[1]?.split(', ') ?? [];
  const fechas = validacion.fechas_pedidas.filter((fecha) => fechasR3.includes(fecha));
  const plazo = /^\d+$/.test(String(plazo_dias ?? '').trim()) ? Number(plazo_dias) : NaN;
  const diasHabiles = Number.isInteger(plazo) ? plazo : 3;
  const futuras = detalle.startsWith('Fechas futuras:');
  const hoy = String(fecha_demo ?? '').slice(0, 10);
  respuesta = `${saludo} No pudimos registrar este justificativo`;
  if (fechas.length) {
    const explicacion = conFechas(fechas, (lista) => {
      if (!futuras) return `para ${lista} ya pasó el plazo de ${diasHabiles} días hábiles para justificar.`;
      return fechas.length === 1
        ? `todavía no ha llegado ${lista}. Puedes escribirnos ese día.`
        : `todavía no han llegado estas fechas (${lista}). Puedes escribirnos cuando lleguen.`;
    }, 105);
    respuesta += `: ${explicacion}`;
  } else {
    respuesta += '.';
  }

  const otras = validacion.fechas_pedidas.filter((fecha) =>
    fecha <= hoy && !fechasR3.includes(fecha) && dentroDelPlazo(fecha, hoy, diasHabiles));
  if (otras.length) {
    const referencia = otras.length === 1 ? 'esa fecha' : 'esas fechas';
    respuesta += conFechas(otras, (lista) =>
      ` Si quieres justificar ${lista}, escríbenos solo ${referencia}.`, 300 - respuesta.length);
  }
  if (respuesta.length + ayuda.length <= 300) respuesta += ayuda;
}

return { json: { ...$json, respuesta } };
