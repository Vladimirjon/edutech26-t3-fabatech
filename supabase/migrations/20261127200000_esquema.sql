create table public.representantes (
    codigo text primary key,
    nombre_ficticio text not null,
    telegram_chat_id bigint
);

create table public.estudiantes (
    codigo text primary key,
    nombre_ficticio text not null,
    curso text not null,
    paralelo text not null,
    representante_codigo text not null references public.representantes (codigo)
);

create table public.carnes (
    token text primary key,
    estudiante_codigo text not null references public.estudiantes (codigo),
    activo boolean not null default true
);

create table public.ingresos (
    id bigserial primary key,
    estudiante_codigo text not null references public.estudiantes (codigo),
    fecha date not null,
    hora timestamptz not null,
    origen text not null check (origen in ('totem', 'app')),
    unique (estudiante_codigo, fecha)
);

create table public.faltas (
    id bigserial primary key,
    estudiante_codigo text not null references public.estudiantes (codigo),
    fecha date not null,
    estado text not null check (estado in ('injustificada', 'pendiente', 'justificada', 'rechazada')),
    unique (estudiante_codigo, fecha)
);

create table public.justificativos (
    id bigserial primary key,
    representante_codigo text not null references public.representantes (codigo),
    estudiante_codigo text references public.estudiantes (codigo),
    tipo_entrada text not null check (tipo_entrada in ('texto', 'voz', 'foto')),
    mensaje_original text,
    foto_file_id text,
    extraccion jsonb,
    validacion jsonb,
    estado text not null check (estado in ('pendiente', 'aprobado', 'rechazado', 'revision_manual')),
    creado timestamptz not null default now()
);

create table public.auditoria (
    id bigserial primary key,
    actor text not null,
    accion text not null,
    entidad text not null,
    entidad_id text not null,
    detalle jsonb not null default '{}'::jsonb,
    creado timestamptz not null default now()
);

create table public.eventos_tablero (
    id bigserial primary key,
    tipo text not null,
    curso text not null,
    paralelo text not null,
    creado timestamptz not null default now()
);

create table public.configuracion (
    clave text primary key,
    valor text not null
);

create index on public.faltas (fecha);
create index on public.ingresos (fecha);
create index on public.justificativos (representante_codigo);

create function public.impedir_cambios_auditoria() returns trigger
language plpgsql as $$
begin
    raise exception 'La auditoría solo admite inserciones';
end;
$$;

create trigger auditoria_proteger_filas
before update or delete on public.auditoria
for each row execute function public.impedir_cambios_auditoria();

create trigger auditoria_impedir_truncate
before truncate on public.auditoria
for each statement execute function public.impedir_cambios_auditoria();
