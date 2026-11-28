with entrada as (
    select
        case
            when $1::text ~ '^\d+$' then $1::bigint
            else null::bigint
        end as id,
        case
            when $2::text in ('aprobado', 'rechazado') then $2::text
            else null::text
        end as decision,
        coalesce(nullif(trim($3::text), ''), 'desconocido') as inspector_chat_id
), objetivo as materialized (
    select
        j.id,
        j.representante_codigo,
        j.estudiante_codigo,
        j.validacion,
        j.extraccion,
        j.estado as estado_previo,
        en.decision,
        en.inspector_chat_id
    from entrada en
    join public.justificativos j on j.id = en.id
    where en.decision is not null
      and j.estado in ('pendiente', 'revision_manual')
    for update of j
), actualizado as materialized (
    update public.justificativos j
    set estado = o.decision
    from objetivo o
    where j.id = o.id
      and j.estado in ('pendiente', 'revision_manual')
    returning
        j.id,
        j.representante_codigo,
        j.estudiante_codigo,
        j.validacion,
        j.extraccion,
        o.estado_previo,
        j.estado as decision,
        o.inspector_chat_id
), fechas_objetivo as materialized (
    select distinct v.fecha_valida as fecha
    from actualizado a
    cross join lateral jsonb_array_elements_text(
        case
            when a.estudiante_codigo is not null
             and jsonb_typeof(a.validacion->'fechas') = 'array'
             and jsonb_array_length(a.validacion->'fechas') > 0
            then a.validacion->'fechas'
            else '[]'::jsonb
        end
    ) as f(fecha_txt)
    cross join lateral (
        select case
            when f.fecha_txt ~ '^\d{4}-\d{2}-\d{2}$'
             and to_char(to_date(f.fecha_txt, 'YYYY-MM-DD'), 'YYYY-MM-DD') = f.fecha_txt
            then to_date(f.fecha_txt, 'YYYY-MM-DD')
            else null::date
        end as fecha_valida
    ) as v
    where v.fecha_valida is not null
), faltas_actualizadas as materialized (
    update public.faltas f
    set estado = case
        when a.decision = 'aprobado' then 'justificada'
        else 'injustificada'
    end
    from actualizado a
    where a.estudiante_codigo is not null
      and exists (select 1 from fechas_objetivo)
      and f.estudiante_codigo = a.estudiante_codigo
      and f.fecha in (select fecha from fechas_objetivo)
      and (
          (a.decision = 'aprobado' and f.estado in ('injustificada', 'pendiente'))
          or (a.decision = 'rechazado' and f.estado = 'pendiente')
      )
    returning f.id, f.fecha::text as fecha
), evento as (
    insert into public.eventos_tablero (tipo, curso, paralelo)
    select 'justificada', e.curso, e.paralelo
    from actualizado a
    join public.estudiantes e on e.codigo = a.estudiante_codigo
    where a.decision = 'aprobado'
      and exists (select 1 from fechas_objetivo)
      and exists (select 1 from faltas_actualizadas)
), auditoria_insert as (
    insert into public.auditoria (actor, accion, entidad, entidad_id, detalle)
    select
        'inspector:' || a.inspector_chat_id,
        a.decision,
        'justificativos',
        a.id::text,
        jsonb_build_object(
            'estado_previo', a.estado_previo,
            'decision', a.decision,
            'estudiante_codigo', a.estudiante_codigo,
            'faltas_actualizadas', (select count(*) from faltas_actualizadas),
            'fechas', coalesce((select jsonb_agg(fecha::text order by fecha) from fechas_objetivo), '[]'::jsonb)
        )
    from actualizado a
)
select
    (a.id is not null) as aplicado,
    a.decision,
    r.telegram_chat_id::text as telegram_chat_id,
    e.nombre_ficticio as estudiante_nombre,
    coalesce((select jsonb_agg(fecha::text order by fecha) from fechas_objetivo), '[]'::jsonb) as fechas,
    a.extraccion->>'motivo' as motivo,
    case
        when a.id is not null then (select count(*)::int from faltas_actualizadas)
        else 0
    end as faltas_actualizadas
from (values (1)) as base(fila)
left join actualizado a on true
left join public.estudiantes e on e.codigo = a.estudiante_codigo
left join public.representantes r on r.codigo = a.representante_codigo;
