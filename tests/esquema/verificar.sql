begin;

do $$
begin
    if (select count(*) from estudiantes) <> 241
       or (select count(*) from representantes) <> 205
       or (select count(*) from carnes where activo) <> 241
       or (select count(*) from faltas) <> 1313 then
        raise exception 'Conteos del seed incorrectos';
    end if;
    if exists (select from configuracion)
       or exists (select from ingresos)
       or exists (select from faltas where fecha = date '2026-01-12') then
        raise exception 'El seed debe iniciar con la configuración y el día del demo vacíos';
    end if;

    insert into justificativos (
        representante_codigo, tipo_entrada, mensaje_original, extraccion, validacion, estado
    ) values ('REP-999', 'foto', null, null, null, 'revision_manual');

    insert into ingresos (estudiante_codigo, fecha, hora, origen)
        values ('EST-999', date '2026-01-12', now(), 'totem');
    begin
        insert into ingresos (estudiante_codigo, fecha, hora, origen)
            values ('EST-999', date '2026-01-12', now(), 'app');
        raise exception 'Se permitió un ingreso duplicado';
    exception when unique_violation then
        null;
    end;

    insert into ingresos (estudiante_codigo, fecha, hora, origen) values
        ('EST-001', date '2026-01-12', now(), 'totem'),
        ('EST-005', date '2026-01-12', now(), 'totem');
    insert into faltas (estudiante_codigo, fecha, estado) values
        ('EST-002', date '2026-01-12', 'injustificada'),
        ('EST-003', date '2026-01-12', 'pendiente'),
        ('EST-004', date '2026-01-12', 'justificada'),
        ('EST-005', date '2026-01-12', 'injustificada');
    begin
        insert into faltas (estudiante_codigo, fecha, estado)
            values ('EST-002', date '2026-01-12', 'justificada');
        raise exception 'Se permitió una falta duplicada';
    exception when unique_violation then
        null;
    end;

    insert into auditoria (actor, accion, entidad, entidad_id)
        values ('prueba', 'ingreso', 'ingresos', '1');
    if (select detalle from auditoria) is distinct from '{}'::jsonb then
        raise exception 'El detalle de auditoría debe iniciar como un objeto vacío';
    end if;
    begin
        update auditoria set actor = 'modificado';
        raise exception 'Se permitió modificar la auditoría';
    exception when raise_exception then
        if sqlerrm <> 'La auditoría solo admite inserciones' then
            raise;
        end if;
    end;
    begin
        delete from auditoria;
        raise exception 'Se permitió borrar la auditoría';
    exception when raise_exception then
        if sqlerrm <> 'La auditoría solo admite inserciones' then
            raise;
        end if;
    end;
end;
$$;

do $$
begin
    if (select array_agg(tablename::text order by tablename)
        from pg_publication_tables
        where pubname = 'supabase_realtime' and schemaname = 'public')
        is distinct from array['eventos_tablero'] then
        raise exception 'Publicación Realtime incorrecta';
    end if;
end;
$$;

insert into eventos_tablero (tipo, curso, paralelo) values ('ingreso', '8vo EGB', 'A');

set local role anon;

do $$
begin
    begin
        perform * from estudiantes;
        raise exception 'Se permitió leer estudiantes como anon';
    exception when insufficient_privilege then
        null;
    end;
    if (select count(*) from v_tablero_hoy) <> 12 or not exists (
        select from v_tablero_hoy
        where curso = '8vo EGB' and paralelo = 'A'
          and (presentes, ausentes, pendientes, justificadas, sin_contacto) = (2, 1, 1, 1, 1)
    ) or exists (
        select from v_tablero_hoy
        where curso = 'PRUEBA' or (
            (curso, paralelo) <> ('8vo EGB', 'A')
            and (presentes, ausentes, pendientes, justificadas, sin_contacto) <> (0, 0, 0, 0, 0)
        )
    ) then
        raise exception 'Los conteos del tablero son incorrectos';
    end if;
    if (select count(*) from eventos_tablero) <> 1 then
        raise exception 'Anon debe leer el evento del tablero';
    end if;
end;
$$;

rollback;
