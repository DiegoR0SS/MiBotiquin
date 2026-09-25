-- ============================================================
-- MI BOTIQUIN
-- Datos de prueba
-- PostgreSQL
-- ============================================================


-- ============================================================
-- 1. USUARIO DE PRUEBA
-- ============================================================

INSERT INTO usuarios (
    google_sub,
    correo,
    nombre,
    apellido
)
VALUES (
    'google_test_001',
    'usuario.prueba@example.com',
    'Usuario',
    'Prueba'
);


-- ============================================================
-- 2. MEDICAMENTOS
-- ============================================================

INSERT INTO medicamentos (
    nombre_comercial,
    forma_farmaceutica,
    via_administracion,
    laboratorio,
    descripcion
)
VALUES
(
    'Paracetamol 500',
    'Tableta',
    'Oral',
    'Laboratorio de prueba',
    'Medicamento de prueba en tabletas'
),
(
    'Jarabe Compuesto',
    'Jarabe',
    'Oral',
    'Laboratorio de prueba',
    'Medicamento de prueba con dos principios activos'
);


-- ============================================================
-- 3. PRINCIPIOS ACTIVOS
-- ============================================================

INSERT INTO principios_activos (nombre)
VALUES
    ('Paracetamol'),
    ('Dextrometorfano');


-- ============================================================
-- 4. RELACIONAR MEDICAMENTOS CON PRINCIPIOS ACTIVOS
-- ============================================================

-- Paracetamol 500 -> Paracetamol
INSERT INTO medicamento_principio_activo (
    id_medicamento,
    id_principio_activo,
    concentracion
)
VALUES (
    (SELECT id_medicamento
     FROM medicamentos
     WHERE nombre_comercial = 'Paracetamol 500'),

    (SELECT id_principio_activo
     FROM principios_activos
     WHERE nombre = 'Paracetamol'),

    '500 mg'
);


-- Jarabe Compuesto -> Paracetamol
INSERT INTO medicamento_principio_activo (
    id_medicamento,
    id_principio_activo,
    concentracion
)
VALUES (
    (SELECT id_medicamento
     FROM medicamentos
     WHERE nombre_comercial = 'Jarabe Compuesto'),

    (SELECT id_principio_activo
     FROM principios_activos
     WHERE nombre = 'Paracetamol'),

    '160 mg / 5 ml'
);


-- Jarabe Compuesto -> Dextrometorfano
INSERT INTO medicamento_principio_activo (
    id_medicamento,
    id_principio_activo,
    concentracion
)
VALUES (
    (SELECT id_medicamento
     FROM medicamentos
     WHERE nombre_comercial = 'Jarabe Compuesto'),

    (SELECT id_principio_activo
     FROM principios_activos
     WHERE nombre = 'Dextrometorfano'),

    '7.5 mg / 5 ml'
);


-- ============================================================
-- 5. INVENTARIO
-- ============================================================

-- Dos cajas de 20 tabletas = 40 tabletas
INSERT INTO inventario (
    id_usuario,
    id_medicamento,
    lote,
    fecha_caducidad,
    cantidad_envases,
    tipo_envase,
    contenido_por_envase,
    unidad_contenido,
    contenido_actual,
    nivel_minimo
)
VALUES (
    (SELECT id_usuario
     FROM usuarios
     WHERE correo = 'usuario.prueba@example.com'),

    (SELECT id_medicamento
     FROM medicamentos
     WHERE nombre_comercial = 'Paracetamol 500'),

    'PARA-001',
    '2027-12-31',
    2,
    'CAJA',
    20,
    'TABLETA',
    40,
    5
);


-- Un frasco de 120 ml
INSERT INTO inventario (
    id_usuario,
    id_medicamento,
    lote,
    fecha_caducidad,
    cantidad_envases,
    tipo_envase,
    contenido_por_envase,
    unidad_contenido,
    contenido_actual,
    nivel_minimo
)
VALUES (
    (SELECT id_usuario
     FROM usuarios
     WHERE correo = 'usuario.prueba@example.com'),

    (SELECT id_medicamento
     FROM medicamentos
     WHERE nombre_comercial = 'Jarabe Compuesto'),

    'JAR-001',
    '2027-08-31',
    1,
    'FRASCO',
    120,
    'ML',
    120,
    20
);


-- ============================================================
-- 6. TRATAMIENTO
-- ============================================================

INSERT INTO tratamientos (
    id_usuario,
    nombre,
    fecha_inicio,
    fecha_fin,
    indicaciones
)
VALUES (
    (SELECT id_usuario
     FROM usuarios
     WHERE correo = 'usuario.prueba@example.com'),

    'Tratamiento de prueba',
    CURRENT_DATE,
    CURRENT_DATE + 6,
    'Tratamiento utilizado únicamente para pruebas del sistema'
);


-- ============================================================
-- 7. MEDICAMENTO DEL TRATAMIENTO
-- ============================================================

INSERT INTO tratamiento_medicamentos (
    id_tratamiento,
    id_medicamento,
    cantidad_dosis,
    unidad_dosis,
    frecuencia,
    duracion_dias,
    indicaciones
)
VALUES (
    (
        SELECT id_tratamiento
        FROM tratamientos
        WHERE nombre = 'Tratamiento de prueba'
    ),

    (
        SELECT id_medicamento
        FROM medicamentos
        WHERE nombre_comercial = 'Jarabe Compuesto'
    ),

    10,
    'ML',
    'Cada 8 horas',
    7,
    'Tomar la cantidad registrada en los horarios establecidos'
);


-- ============================================================
-- 8. HORARIOS
-- ============================================================

INSERT INTO horarios_toma (
    id_tratamiento_medicamento,
    hora
)
VALUES
(
    (
        SELECT tm.id_tratamiento_medicamento
        FROM tratamiento_medicamentos tm
        JOIN tratamientos t
            ON t.id_tratamiento = tm.id_tratamiento
        JOIN medicamentos m
            ON m.id_medicamento = tm.id_medicamento
        WHERE t.nombre = 'Tratamiento de prueba'
          AND m.nombre_comercial = 'Jarabe Compuesto'
    ),
    '08:00'
),
(
    (
        SELECT tm.id_tratamiento_medicamento
        FROM tratamiento_medicamentos tm
        JOIN tratamientos t
            ON t.id_tratamiento = tm.id_tratamiento
        JOIN medicamentos m
            ON m.id_medicamento = tm.id_medicamento
        WHERE t.nombre = 'Tratamiento de prueba'
          AND m.nombre_comercial = 'Jarabe Compuesto'
    ),
    '16:00'
),
(
    (
        SELECT tm.id_tratamiento_medicamento
        FROM tratamiento_medicamentos tm
        JOIN tratamientos t
            ON t.id_tratamiento = tm.id_tratamiento
        JOIN medicamentos m
            ON m.id_medicamento = tm.id_medicamento
        WHERE t.nombre = 'Tratamiento de prueba'
          AND m.nombre_comercial = 'Jarabe Compuesto'
    ),
    '00:00'
);
