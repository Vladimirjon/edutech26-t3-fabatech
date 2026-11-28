with vinculo as (
    insert into public.configuracion (clave, valor)
    select 'inspector_chat_id', $2::text
    from public.configuracion
    where clave = 'portika_clave_inspector' and valor = $1 and $1 <> ''
    on conflict (clave) do update set valor = excluded.valor
    returning 1
)
select exists (select 1 from vinculo) as vinculado;
