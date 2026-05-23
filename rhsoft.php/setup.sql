-- ============================================================
--  setup.sql — Script unificado del sistema web
--  Incluye todas las tablas + datos de ejemplo
-- ============================================================

CREATE DATABASE IF NOT EXISTS gestion_empleados CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gestion_empleados;

SET FOREIGN_KEY_CHECKS = 0;

-- ── Tabla PERSONAS ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS PERSONAS (
    ID_Persona        INT          NOT NULL AUTO_INCREMENT,
    Numero_Documento  VARCHAR(50)  NOT NULL,
    Nombres           VARCHAR(150) NOT NULL,
    Apellidos         VARCHAR(150) NOT NULL,
    Email             VARCHAR(150),
    Telefono          VARCHAR(30),
    Fecha_Nacimiento  DATE,
    PRIMARY KEY (ID_Persona),
    UNIQUE KEY UK_Numero_Documento (Numero_Documento)
);

-- ── Tabla DEPARTAMENTOS ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS DEPARTAMENTOS (
    ID_Departamento     INT          NOT NULL AUTO_INCREMENT,
    Nombre_Departamento VARCHAR(150) NOT NULL,
    PRIMARY KEY (ID_Departamento)
);

-- ── Tabla CARGOS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS CARGOS (
    ID_Cargo              INT           NOT NULL AUTO_INCREMENT,
    ID_Departamento       INT           NOT NULL,
    Nombre_Cargo          VARCHAR(150)  NOT NULL,
    Descripcion_Funciones VARCHAR(500),
    Salario_Base          DECIMAL(15,2),
    Hora_Inicio_Jornada   TIME,
    Hora_Fin_Jornada      TIME,
    PRIMARY KEY (ID_Cargo),
    CONSTRAINT FK_Cargo_Departamento FOREIGN KEY (ID_Departamento)
        REFERENCES DEPARTAMENTOS (ID_Departamento)
);

-- ── Tabla CARGO_DIAS (R17) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS CARGO_DIAS (
    ID_Cargo   INT         NOT NULL,
    Dia_Semana VARCHAR(20) NOT NULL,
    PRIMARY KEY (ID_Cargo, Dia_Semana),
    CONSTRAINT FK_CargoDias_Cargo FOREIGN KEY (ID_Cargo)
        REFERENCES CARGOS (ID_Cargo)
);

-- ── Tabla EMPLEADOS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS EMPLEADOS (
    ID_Empleado     INT         NOT NULL AUTO_INCREMENT,
    ID_Persona      INT         NOT NULL,
    ID_Cargo        INT         NOT NULL,
    PIN             CHAR(6)     NOT NULL,
    Rol             VARCHAR(20) NOT NULL DEFAULT 'empleado', -- 'empleado' o 'admin'
    Fecha_Ingreso   DATE,
    Fecha_Retiro    DATE        NULL,
    Estado_Empleado VARCHAR(50) DEFAULT 'Activo',
    PRIMARY KEY (ID_Empleado),
    UNIQUE KEY UK_PIN (PIN),
    CONSTRAINT FK_Empleado_Persona FOREIGN KEY (ID_Persona)
        REFERENCES PERSONAS (ID_Persona),
    CONSTRAINT FK_Empleado_Cargo FOREIGN KEY (ID_Cargo)
        REFERENCES CARGOS (ID_Cargo)
);

-- ── Tabla CONTRATOS (R13) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS CONTRATOS (
    ID_Contrato     INT           NOT NULL AUTO_INCREMENT,
    ID_Empleado     INT           NOT NULL,
    ID_Cargo        INT           NOT NULL,
    Tipo_Contrato   VARCHAR(100)  DEFAULT NULL,
    Salario_Pactado DECIMAL(15,2) DEFAULT NULL,
    Fecha_Inicio    DATE          DEFAULT NULL,
    Fecha_Fin       DATE          DEFAULT NULL,
    Estado_Contrato VARCHAR(50)   DEFAULT 'Vigente',
    PRIMARY KEY (ID_Contrato),
    CONSTRAINT FK_Contrato_Empleado FOREIGN KEY (ID_Empleado)
        REFERENCES EMPLEADOS (ID_Empleado),
    CONSTRAINT FK_Contrato_Cargo FOREIGN KEY (ID_Cargo)
        REFERENCES CARGOS (ID_Cargo)
);

-- ── Tabla REGISTROS (marcaciones) ───────────────────────────
CREATE TABLE IF NOT EXISTS REGISTROS (
    ID_Registro INT         NOT NULL AUTO_INCREMENT,
    ID_Empleado INT         NOT NULL,
    Fecha       DATE        NOT NULL,
    Hora_Entrada TIME       NOT NULL,
    Hora_Salida  TIME       NULL,
    Tipo        VARCHAR(80) DEFAULT 'Normal',
    Observacion VARCHAR(300),
    PRIMARY KEY (ID_Registro),
    CONSTRAINT FK_Registro_Empleado FOREIGN KEY (ID_Empleado)
        REFERENCES EMPLEADOS (ID_Empleado)
);

-- ── Tabla SST_ACCIDENTES (R14) ───────────────────────────────
CREATE TABLE IF NOT EXISTS SST_ACCIDENTES (
    ID_Accidente     INT          NOT NULL AUTO_INCREMENT,
    ID_Empleado      INT          NOT NULL,
    Fecha_Accidente  DATE         DEFAULT NULL,
    Tipo_Accidente   VARCHAR(100) DEFAULT NULL,
    Descripcion      VARCHAR(500) DEFAULT NULL,
    Accion_Inmediata VARCHAR(500) DEFAULT NULL,
    Fecha_Reporte    DATE         DEFAULT NULL,
    PRIMARY KEY (ID_Accidente),
    CONSTRAINT FK_Accidente_Empleado FOREIGN KEY (ID_Empleado)
        REFERENCES EMPLEADOS (ID_Empleado)
);

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
--  Datos de ejemplo
-- ============================================================

INSERT IGNORE INTO DEPARTAMENTOS (Nombre_Departamento) VALUES
    ('Recursos Humanos'),
    ('Tecnología'),
    ('Contabilidad'),
    ('Producción'),
    ('SST');

INSERT IGNORE INTO CARGOS (ID_Departamento, Nombre_Cargo, Salario_Base, Hora_Inicio_Jornada, Hora_Fin_Jornada) VALUES
    (1, 'Coordinador RRHH',  3500000, '08:00:00', '17:00:00'),
    (2, 'Desarrollador',     4500000, '08:00:00', '17:00:00'),
    (3, 'Contador',          3200000, '08:00:00', '17:00:00'),
    (4, 'Operario',          1800000, '06:00:00', '14:00:00'),
    (5, 'Inspector SST',     2800000, '07:00:00', '16:00:00');

-- Días laborales por cargo (R17)
INSERT IGNORE INTO CARGO_DIAS (ID_Cargo, Dia_Semana) VALUES
    (1, 'Lunes'), (1, 'Martes'), (1, 'Miércoles'), (1, 'Jueves'), (1, 'Viernes'),
    (2, 'Lunes'), (2, 'Martes'), (2, 'Miércoles'), (2, 'Jueves'), (2, 'Viernes'),
    (3, 'Lunes'), (3, 'Martes'), (3, 'Miércoles'), (3, 'Jueves'), (3, 'Viernes'),
    (4, 'Lunes'), (4, 'Martes'), (4, 'Miércoles'), (4, 'Jueves'), (4, 'Viernes'), (4, 'Sábado'),
    (5, 'Lunes'), (5, 'Martes'), (5, 'Miércoles'), (5, 'Jueves'), (5, 'Viernes');

-- Personas de ejemplo
INSERT IGNORE INTO PERSONAS (Numero_Documento, Nombres, Apellidos, Email, Telefono, Fecha_Nacimiento)
VALUES ('1000000001', 'Carlos', 'Administrador', 'admin@empresa.com', '3001234567', '1985-06-15');

INSERT IGNORE INTO PERSONAS (Numero_Documento, Nombres, Apellidos, Email, Telefono, Fecha_Nacimiento)
VALUES ('1000000002', 'María', 'González', 'maria@empresa.com', '3109876543', '1992-03-22');

-- Empleados de ejemplo
INSERT IGNORE INTO EMPLEADOS (ID_Persona, ID_Cargo, PIN, Rol, Fecha_Ingreso, Estado_Empleado)
VALUES (1, 1, '999999', 'admin', '2020-01-15', 'Activo');

INSERT IGNORE INTO EMPLEADOS (ID_Persona, ID_Cargo, PIN, Rol, Fecha_Ingreso, Estado_Empleado)
VALUES (2, 2, '123456', 'empleado', '2022-05-10', 'Activo');

-- Contratos de ejemplo (R13)
INSERT IGNORE INTO CONTRATOS (ID_Empleado, ID_Cargo, Tipo_Contrato, Salario_Pactado, Fecha_Inicio, Fecha_Fin, Estado_Contrato)
VALUES (1, 1, 'Indefinido', 3500000, '2020-01-15', NULL, 'Vigente');

INSERT IGNORE INTO CONTRATOS (ID_Empleado, ID_Cargo, Tipo_Contrato, Salario_Pactado, Fecha_Inicio, Fecha_Fin, Estado_Contrato)
VALUES (2, 2, 'Temporal', 4500000, '2022-05-10', '2023-05-10', 'Vigente');
