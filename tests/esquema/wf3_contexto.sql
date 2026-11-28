with representante as (
    select codigo
    from public.representantes
    where telegram_chat_id = $1::bigint
    order by codigo
    limit 1
), hijos as (
    select codigo, nombre_ficticio, curso, paralelo
    from public.estudiantes
    where representante_codigo = (select codigo from representante)
)
select
    (select codigo from representante) as representante_codigo,
    coalesce((select jsonb_agg(h order by h.codigo) from hijos h), '[]'::jsonb) as hijos,
    coalesce((
        select jsonb_agg(jsonb_build_object(
            'estudiante_codigo', f.estudiante_codigo, 'fecha', f.fecha::text, 'estado', f.estado
        ) order by f.estudiante_codigo, f.fecha)
        from public.faltas f
        join hijos h on h.codigo = f.estudiante_codigo
        where f.estado in ('injustificada', 'pendiente')
    ), '[]'::jsonb) as faltas,
    (select valor from public.configuracion where clave = 'fecha_demo') as fecha_demo,
    (select valor from public.configuracion where clave = 'plazo_dias') as plazo_dias;
