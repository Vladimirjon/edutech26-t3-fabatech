with entrada as (
    select case
        when $1::text ~ '^\d+$' then $1::bigint
        else null::bigint
    end as id
)
select
    j.id::text as id,
    j.estado,
    j.validacion,
    j.extraccion,
    j.foto_file_id,
    j.mensaje_original,
    j.estudiante_codigo,
    e.nombre_ficticio as estudiante_nombre,
    e.curso,
    e.paralelo,
    r.telegram_chat_id::text as telegram_chat_id,
    (
        select nullif(trim(valor), '')
        from public.configuracion
        where clave = 'inspector_chat_id'
    ) as inspector_chat_id
from (values (1)) as base(fila)
left join entrada en on true
left join public.justificativos j on j.id = en.id
left join public.estudiantes e on e.codigo = j.estudiante_codigo
left join public.representantes r on r.codigo = j.representante_codigo;
