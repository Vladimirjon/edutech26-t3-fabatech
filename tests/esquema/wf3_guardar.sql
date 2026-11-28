with entrada as (
    select $1::text as representante_codigo, $2::text as tipo_entrada,
           nullif($3, '') as mensaje_original, nullif($4, '') as foto_file_id,
           nullif($5, '')::jsonb as extraccion, $6::jsonb as validacion
), justificativo as (
    insert into public.justificativos (
        representante_codigo, estudiante_codigo, tipo_entrada, mensaje_original,
        foto_file_id, extraccion, validacion, estado
    )
    select representante_codigo, validacion->>'estudiante_codigo', tipo_entrada, mensaje_original,
           foto_file_id, extraccion, validacion,
           case validacion->>'destino'
               when 'aprobacion' then 'pendiente'
               when 'rechazado' then 'rechazado'
               else 'revision_manual'
           end
    from entrada
    returning id, estudiante_codigo, validacion
), faltas_pendientes as (
    update public.faltas f
    set estado = 'pendiente'
    from justificativo j
    where j.validacion->>'destino' = 'aprobacion'
      and f.estudiante_codigo = j.estudiante_codigo
      and f.fecha in (select fecha::date from jsonb_array_elements_text(j.validacion->'fechas') as fechas(fecha))
      and f.estado in ('injustificada', 'pendiente')
    returning f.estudiante_codigo
), evento as (
    insert into public.eventos_tablero (tipo, curso, paralelo)
    select 'pendiente', e.curso, e.paralelo
    from public.estudiantes e
    where e.codigo = (select estudiante_codigo from justificativo)
      and exists (select 1 from faltas_pendientes)
)
select id, validacion->>'destino' as destino from justificativo;
