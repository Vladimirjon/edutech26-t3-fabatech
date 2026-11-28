with auth as materialized (
    select 1
    from public.configuracion
    where clave = 'portika_clave_dispositivo' and valor = $1 and $1 <> ''
), carne as materialized (
    select e.codigo, e.nombre_ficticio, e.curso, e.paralelo,
           nullif($3::text, '') as escaneado_en
    from public.carnes c
    join public.estudiantes e on e.codigo = c.estudiante_codigo
    where exists (select 1 from auth)
      and c.token = nullif($2, '') and c.activo
), ingreso as (
    insert into public.ingresos (estudiante_codigo, fecha, hora, origen)
    select carne.codigo,
           coalesce(
               (select valor::date from public.configuracion where clave = 'fecha_demo'),
               (escaneo.hora at time zone 'America/Guayaquil')::date
           ),
           escaneo.hora,
           case when $4 in ('totem', 'app') then $4 else 'app' end
    from carne
    cross join lateral (
        select coalesce(case
            when length(escaneado_en) <= 128 and left(escaneado_en, 4) <> '0000'
             and escaneado_en ~ '^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9]([.][0-9]+)?)?(Z|[+-](0[0-9]|1[0-5]):?[0-5][0-9])$'
            then case when substring(escaneado_en from 9 for 2)::int <= extract(day from (
                make_date(left(escaneado_en, 4)::int, substring(escaneado_en from 6 for 2)::int, 1)
                + interval '1 month' - interval '1 day'
            )) then escaneado_en::timestamptz end
        end, now()) as hora
    ) escaneo
    on conflict (estudiante_codigo, fecha) do update set hora = ingresos.hora
    returning id, hora, (xmax = 0) as insertado
), evento as (
    insert into public.eventos_tablero (tipo, curso, paralelo)
    select 'ingreso', carne.curso, carne.paralelo
    from carne cross join ingreso
    where ingreso.insertado
), auditoria as (
    insert into public.auditoria (actor, accion, entidad, entidad_id)
    select 'sistema:WF1', 'ingreso', 'ingresos', id::text
    from ingreso
    where insertado
)
select case
           when not exists (select 1 from auth) then 'no_autorizado'
           when carne.codigo is null then 'carne_desconocido'
           when ingreso.insertado then 'registrado'
           else 'duplicado'
       end as estado,
       case when carne.codigo is not null then jsonb_build_object(
           'codigo', carne.codigo, 'nombre_ficticio', carne.nombre_ficticio,
           'curso', carne.curso, 'paralelo', carne.paralelo
       ) end as estudiante,
       to_char(ingreso.hora at time zone 'America/Guayaquil', 'YYYY-MM-DD"T"HH24:MI:SS"-05:00"') as hora
from (values (1)) as respuesta(fila)
left join carne on true
left join ingreso on true;
