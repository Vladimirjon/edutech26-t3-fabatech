with vinculacion as (
    update public.representantes
    set telegram_chat_id = case when codigo = $2::text then $1::bigint end
    where (codigo = $2::text or telegram_chat_id = $1::bigint)
      and exists (select 1 from public.representantes where codigo = $2::text)
    returning codigo
)
select exists (select 1 from vinculacion where codigo = $2::text) as vinculado;
