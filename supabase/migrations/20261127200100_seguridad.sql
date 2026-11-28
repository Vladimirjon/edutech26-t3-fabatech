alter table public.representantes enable row level security;
alter table public.estudiantes enable row level security;
alter table public.carnes enable row level security;
alter table public.ingresos enable row level security;
alter table public.faltas enable row level security;
alter table public.justificativos enable row level security;
alter table public.auditoria enable row level security;
alter table public.eventos_tablero enable row level security;
alter table public.configuracion enable row level security;

revoke all on all tables in schema public from anon, authenticated;
revoke all on all sequences in schema public from anon, authenticated;
alter default privileges in schema public revoke all on tables from anon, authenticated;
alter default privileges in schema public revoke all on sequences from anon, authenticated;
alter default privileges revoke execute on functions from public;
revoke execute on function public.impedir_cambios_auditoria() from public, anon, authenticated;

create view public.v_tablero_hoy as
with demo as (
    -- FECHA_DEMO de C0; se cambia con una migración
    select date '2026-01-12' as fecha
)
select e.curso, e.paralelo,
       count(i.id) as presentes,
       -- El ingreso tiene prioridad sobre la falta; sin_contacto es un subconjunto de ausentes.
       count(*) filter (where i.id is null and f.estado in ('injustificada', 'rechazada')) as ausentes,
       count(*) filter (where i.id is null and f.estado = 'pendiente') as pendientes,
       count(*) filter (where i.id is null and f.estado = 'justificada') as justificadas,
       count(*) filter (
           where i.id is null and f.estado = 'injustificada' and r.telegram_chat_id is null
       ) as sin_contacto
from public.estudiantes e
join public.representantes r on r.codigo = e.representante_codigo
cross join demo
left join public.ingresos i on i.estudiante_codigo = e.codigo and i.fecha = demo.fecha
left join public.faltas f on f.estudiante_codigo = e.codigo and f.fecha = demo.fecha
where e.curso <> 'PRUEBA'
group by e.curso, e.paralelo;

grant select on public.v_tablero_hoy, public.eventos_tablero to anon, authenticated;
create policy eventos_tablero_lectura on public.eventos_tablero
for select to anon, authenticated using (true);

alter publication supabase_realtime add table public.eventos_tablero;
