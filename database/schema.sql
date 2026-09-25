-- ============================================================
-- MI BOTIQUIN
-- Esquema inicial de base de datos
-- PostgreSQL
-- ============================================================


-- ============================================================
-- 1. USUARIOS
-- ============================================================

CREATE TABLE usuarios (
    id_usuario BIGSERIAL PRIMARY KEY,
    google_sub VARCHAR(255) UNIQUE NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    foto_perfil TEXT,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);


-- ============================================================
-- 2. MEDICAMENTOS
-- ============================================================

CREATE TABLE medicamentos (
    id_medicamento BIGSERIAL PRIMARY KEY,
    nombre_comercial VARCHAR(150) NOT NULL,
    forma_farmaceutica VARCHAR(80),
    via_administracion VARCHAR(80),
    laboratorio VARCHAR(150),
    descripcion TEXT,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 3. PRINCIPIOS ACTIVOS
-- ============================================================

CREATE TABLE principios_activos (
    id_principio_activo BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL,
    descripcion TEXT
);


-- ============================================================
-- 4. MEDICAMENTO - PRINCIPIO ACTIVO
-- ============================================================

CREATE TABLE medicamento_principio_activo (
    id_medicamento BIGINT NOT NULL,
    id_principio_activo BIGINT NOT NULL,
    concentracion VARCHAR(100),

    PRIMARY KEY (id_medicamento, id_principio_activo),

    CONSTRAINT fk_mpa_medicamento
        FOREIGN KEY (id_medicamento)
        REFERENCES medicamentos(id_medicamento)
        ON DELETE CASCADE,

    CONSTRAINT fk_mpa_principio
        FOREIGN KEY (id_principio_activo)
        REFERENCES principios_activos(id_principio_activo)
        ON DELETE CASCADE
);


-- ============================================================
-- 5. INVENTARIO
-- ============================================================

CREATE TABLE inventario (
    id_inventario BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    id_medicamento BIGINT NOT NULL,

    lote VARCHAR(100),
    fecha_caducidad DATE,

    cantidad_envases INTEGER NOT NULL DEFAULT 1,
    tipo_envase VARCHAR(50),

    contenido_por_envase NUMERIC(10,2) NOT NULL,
    unidad_contenido VARCHAR(30) NOT NULL,
    contenido_actual NUMERIC(10,2) NOT NULL,

    nivel_minimo NUMERIC(10,2) NOT NULL DEFAULT 0,

    fecha_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    imagen TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_cantidad_envases
        CHECK (cantidad_envases >= 0),

    CONSTRAINT chk_contenido_envase
        CHECK (contenido_por_envase > 0),

    CONSTRAINT chk_contenido_actual
        CHECK (contenido_actual >= 0),

    CONSTRAINT chk_nivel_minimo
        CHECK (nivel_minimo >= 0),

    CONSTRAINT fk_inventario_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    CONSTRAINT fk_inventario_medicamento
        FOREIGN KEY (id_medicamento)
        REFERENCES medicamentos(id_medicamento)
);


-- ============================================================
-- 6. RECETAS
-- ============================================================

CREATE TABLE recetas (
    id_receta BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    imagen TEXT,
    texto_extraido TEXT,
    fecha_captura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_receta_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
);


-- ============================================================
-- 7. TRATAMIENTOS
-- ============================================================

CREATE TABLE tratamientos (
    id_tratamiento BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    id_receta BIGINT,

    nombre VARCHAR(150) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    indicaciones TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_fechas_tratamiento
        CHECK (
            fecha_fin IS NULL
            OR fecha_fin >= fecha_inicio
        ),

    CONSTRAINT chk_estado_tratamiento
        CHECK (
            estado IN (
                'ACTIVO',
                'FINALIZADO',
                'CANCELADO'
            )
        ),

    CONSTRAINT fk_tratamiento_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    CONSTRAINT fk_tratamiento_receta
        FOREIGN KEY (id_receta)
        REFERENCES recetas(id_receta)
        ON DELETE SET NULL
);


-- ============================================================
-- 8. MEDICAMENTOS DEL TRATAMIENTO
-- ============================================================

CREATE TABLE tratamiento_medicamentos (
    id_tratamiento_medicamento BIGSERIAL PRIMARY KEY,
    id_tratamiento BIGINT NOT NULL,
    id_medicamento BIGINT NOT NULL,

    cantidad_dosis NUMERIC(10,2) NOT NULL,
    unidad_dosis VARCHAR(30) NOT NULL,
    frecuencia VARCHAR(100),
    duracion_dias INTEGER,
    indicaciones TEXT,

    CONSTRAINT chk_cantidad_dosis
        CHECK (cantidad_dosis > 0),

    CONSTRAINT chk_duracion
        CHECK (
            duracion_dias IS NULL
            OR duracion_dias > 0
        ),

    CONSTRAINT fk_tm_tratamiento
        FOREIGN KEY (id_tratamiento)
        REFERENCES tratamientos(id_tratamiento)
        ON DELETE CASCADE,

    CONSTRAINT fk_tm_medicamento
        FOREIGN KEY (id_medicamento)
        REFERENCES medicamentos(id_medicamento)
);


-- ============================================================
-- 9. HORARIOS DE TOMA
-- ============================================================

CREATE TABLE horarios_toma (
    id_horario BIGSERIAL PRIMARY KEY,
    id_tratamiento_medicamento BIGINT NOT NULL,
    hora TIME NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_horario_tratamiento_medicamento
        FOREIGN KEY (id_tratamiento_medicamento)
        REFERENCES tratamiento_medicamentos(id_tratamiento_medicamento)
        ON DELETE CASCADE,

    CONSTRAINT uq_horario
        UNIQUE (id_tratamiento_medicamento, hora)
);


-- ============================================================
-- 10. HISTORIAL DE TOMAS
-- ============================================================

CREATE TABLE historial_tomas (
    id_toma BIGSERIAL PRIMARY KEY,
    id_horario BIGINT NOT NULL,

    fecha_programada TIMESTAMP NOT NULL,
    fecha_tomada TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',

    cantidad_consumida NUMERIC(10,2),
    unidad_consumida VARCHAR(30),

    observaciones TEXT,

    CONSTRAINT chk_estado_toma
        CHECK (
            estado IN (
                'PENDIENTE',
                'TOMADA',
                'OMITIDA'
            )
        ),

    CONSTRAINT chk_cantidad_consumida
        CHECK (
            cantidad_consumida IS NULL
            OR cantidad_consumida > 0
        ),

    CONSTRAINT fk_historial_horario
        FOREIGN KEY (id_horario)
        REFERENCES horarios_toma(id_horario)
);


-- ============================================================
-- 11. ALERTAS
-- ============================================================

CREATE TABLE alertas (
    id_alerta BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    id_inventario BIGINT,

    tipo VARCHAR(30) NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,

    fecha_generacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    leida BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT chk_tipo_alerta
        CHECK (
            tipo IN (
                'CADUCIDAD',
                'CADUCADO',
                'STOCK_BAJO',
                'MEDICAMENTO_SIMILAR'
            )
        ),

    CONSTRAINT fk_alerta_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    CONSTRAINT fk_alerta_inventario
        FOREIGN KEY (id_inventario)
        REFERENCES inventario(id_inventario)
        ON DELETE SET NULL
);
