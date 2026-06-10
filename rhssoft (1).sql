-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 10-06-2026 a las 01:58:25
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `rhssoft`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `candidatos`
--

CREATE TABLE `candidatos` (
  `id_candidato` int(11) NOT NULL,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `documento` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `cargo_postulado` varchar(100) DEFAULT NULL,
  `estado` enum('EN_PROCESO','APROBADO','RECHAZADO') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cargos`
--

CREATE TABLE `cargos` (
  `id_cargo` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `salario_referencia` decimal(10,2) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `cargos`
--

INSERT INTO `cargos` (`id_cargo`, `nombre`, `salario_referencia`, `descripcion`) VALUES
(1, 'Administrador', 3500000.00, 'Administrador general'),
(2, 'Analista RRHH', 2500000.00, 'Gestión humana'),
(3, 'Supervisor', 2200000.00, 'Producción'),
(4, 'Operario', 1800000.00, 'Producción'),
(5, 'Auxiliar Logístico', 1700000.00, 'Despachos'),
(6, 'Inspector Calidad', 2100000.00, 'Calidad'),
(7, 'Comprador', 2300000.00, 'Compras'),
(8, 'Analista SST', 2400000.00, 'Seguridad'),
(9, 'Programador', 3200000.00, 'Sistemas'),
(10, 'Técnico Mantenimiento', 2200000.00, 'Mantenimiento'),
(11, 'Coordinador de Proyectos', 2800000.00, 'Coordinación de proyectos internos');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cargo_dias`
--

CREATE TABLE `cargo_dias` (
  `id_cargo_dia` int(11) NOT NULL,
  `id_cargo` int(11) NOT NULL,
  `dia_semana` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contratos`
--

CREATE TABLE `contratos` (
  `id_contrato` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `tipo_contrato` varchar(100) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `estado` enum('ACTIVO','FINALIZADO') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `contratos`
--

INSERT INTO `contratos` (`id_contrato`, `id_empleado`, `tipo_contrato`, `fecha_inicio`, `fecha_fin`, `estado`) VALUES
(1, 1, 'Indefinido', '2024-01-01', '2030-01-01', 'ACTIVO'),
(2, 2, 'Indefinido', '2024-01-02', '2030-01-02', 'ACTIVO'),
(3, 3, 'Fijo', '2024-01-03', '2026-01-03', 'ACTIVO'),
(4, 4, 'Fijo', '2024-01-04', '2026-01-04', 'ACTIVO'),
(5, 5, 'Indefinido', '2024-01-05', '2030-01-05', 'ACTIVO'),
(6, 6, 'Indefinido', '2024-01-06', '2030-01-06', 'ACTIVO'),
(7, 7, 'Fijo', '2024-01-07', '2026-01-07', 'ACTIVO'),
(8, 8, 'Fijo', '2024-01-08', '2026-01-08', 'ACTIVO'),
(9, 9, 'Indefinido', '2024-01-09', '2030-01-09', 'ACTIVO'),
(10, 10, 'Indefinido', '2024-01-10', '2030-01-10', 'ACTIVO');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `id_departamento` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `departamentos`
--

INSERT INTO `departamentos` (`id_departamento`, `nombre`, `descripcion`) VALUES
(1, 'Gerencia', 'Dirección general'),
(2, 'Recursos Humanos', 'Gestión humana'),
(3, 'Producción', 'Área productiva'),
(4, 'Logística', 'Despachos'),
(5, 'Calidad', 'Control calidad'),
(6, 'Compras', 'Abastecimiento'),
(7, 'SST', 'Seguridad y salud'),
(8, 'Sistemas', 'Tecnología'),
(9, 'Contabilidad', 'Finanzas'),
(10, 'Mantenimiento', 'Equipos');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `id_departamento` int(11) NOT NULL,
  `id_cargo` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `estado` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleado`, `id_persona`, `id_departamento`, `id_cargo`, `id_usuario`, `fecha_ingreso`, `estado`) VALUES
(1, 1, 2, 2, 2, '2024-01-01', 'ACTIVO'),
(2, 2, 3, 3, 3, '2024-01-02', 'INACTIVO'),
(3, 3, 3, 4, 4, '2024-01-03', 'ACTIVO'),
(4, 4, 4, 5, 5, '2024-01-04', 'ACTIVO'),
(5, 5, 5, 6, 6, '2024-01-05', 'ACTIVO'),
(6, 6, 6, 7, 7, '2024-01-06', 'ACTIVO'),
(7, 7, 7, 8, 8, '2024-01-07', 'ACTIVO'),
(8, 8, 8, 9, 9, '2024-01-08', 'ACTIVO'),
(9, 9, 9, 10, 10, '2024-01-09', 'ACTIVO'),
(10, 10, 10, 10, 11, '2024-01-10', 'ACTIVO'),
(11, 11, 8, 9, 12, '2027-06-01', 'ACTIVO');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `permisos`
--

CREATE TABLE `permisos` (
  `id_permiso` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `estado` enum('PENDIENTE','APROBADO','RECHAZADO') DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `permisos`
--

INSERT INTO `permisos` (`id_permiso`, `id_empleado`, `motivo`, `fecha_inicio`, `fecha_fin`, `estado`) VALUES
(1, 1, 'Cita médica', '2026-06-15', '2026-06-15', 'APROBADO'),
(2, 2, 'Diligencia personal', '2026-06-20', '2026-06-20', 'PENDIENTE'),
(3, 3, 'Calamidad familiar', '2026-06-25', '2026-06-27', 'APROBADO');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `personas`
--

CREATE TABLE `personas` (
  `id_persona` int(11) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `documento` varchar(20) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `genero` enum('M','F') DEFAULT NULL,
  `foto` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `personas`
--

INSERT INTO `personas` (`id_persona`, `nombres`, `apellidos`, `documento`, `telefono`, `correo`, `direccion`, `fecha_nacimiento`, `genero`, `foto`) VALUES
(1, 'Jerson', 'ortiz', '1001', '3001111111', 'jerson@cobalsa.com', 'Calle 1', '2000-01-01', 'M', NULL),
(2, 'Cristian', 'Lopez', '1002', '3002222222', 'cristian@cobalsa.com', 'Calle 2', '1999-02-02', 'M', NULL),
(3, 'Andriu', 'Perez', '1003', '3003333333', 'andriu@cobalsa.com', 'Calle 3', '1998-03-03', 'M', NULL),
(4, 'Laura', 'Gomez', '1004', '3004444444', 'laura@cobalsa.com', 'Calle 4', '1997-04-04', 'F', NULL),
(5, 'Camila', 'Diaz', '1005', '3005555555', 'camila@cobalsa.com', 'Calle 5', '1996-05-05', 'F', NULL),
(6, 'Daniel', 'Rojas', '1006', '3006666666', 'daniel@cobalsa.com', 'Calle 6', '1995-06-06', 'M', NULL),
(7, 'Valentina', 'Ruiz', '1007', '3007777777', 'valentina@cobalsa.com', 'Calle 7', '1994-07-07', 'F', NULL),
(8, 'Miguel', 'Torres', '1008', '3008888888', 'miguel@cobalsa.com', 'Calle 8', '1993-08-08', 'M', NULL),
(9, 'Sofia', 'Moreno', '1009', '3009999999', 'sofia@cobalsa.com', 'Calle 9', '1992-09-09', 'F', NULL),
(10, 'Juan', 'Castro', '1010', '3001010101', 'juan@cobalsa.com', 'Calle 10', '1991-10-10', 'M', NULL),
(11, 'jack ', 'Sarmiento', '1121535125', '3132125130', 'jeperez098@gmail.com', 'Kr 97 # 128 B06', '2026-06-01', 'M', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registros`
--

CREATE TABLE `registros` (
  `id_registro` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora_entrada` time DEFAULT NULL,
  `hora_salida` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `registros`
--

INSERT INTO `registros` (`id_registro`, `id_empleado`, `fecha`, `hora_entrada`, `hora_salida`) VALUES
(1, 1, '2025-06-01', '07:00:00', '17:00:00'),
(2, 2, '2025-06-01', '07:00:00', '17:00:00'),
(3, 3, '2025-06-01', '07:00:00', '17:00:00'),
(4, 4, '2025-06-01', '07:00:00', '17:00:00'),
(5, 5, '2025-06-01', '07:00:00', '17:00:00'),
(6, 6, '2025-06-01', '07:00:00', '17:00:00'),
(7, 7, '2025-06-01', '07:00:00', '17:00:00'),
(8, 8, '2025-06-01', '07:00:00', '17:00:00'),
(9, 9, '2025-06-01', '07:00:00', '17:00:00'),
(10, 10, '2025-06-01', '07:00:00', '17:00:00'),
(11, 11, '2026-06-03', '14:14:10', '14:27:05'),
(12, 11, '2026-06-03', '14:20:32', '14:27:05'),
(13, 11, '2026-06-03', '14:27:03', '14:27:05'),
(14, 9, '2026-06-03', '15:02:44', '15:02:51'),
(15, 11, '2026-06-09', '16:26:08', '16:26:11'),
(16, 4, '2026-06-09', '16:31:31', '16:31:39'),
(17, 9, '2026-06-09', '16:58:30', '16:58:37'),
(18, 5, '2026-06-09', '17:15:58', '17:16:12'),
(19, 6, '2026-06-09', '17:27:31', '17:28:21');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sst_accidentes`
--

CREATE TABLE `sst_accidentes` (
  `id_accidente` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `fecha` date DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `gravedad` enum('LEVE','MODERADA','GRAVE') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('ADMIN','EMPLEADO') NOT NULL,
  `estado` enum('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `correo`, `password`, `rol`, `estado`) VALUES
(1, 'admin@cobalsa.com', '123456', 'ADMIN', 'ACTIVO'),
(2, 'empleado1@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(3, 'empleado2@cobalsa.com', '123456', 'EMPLEADO', 'INACTIVO'),
(4, 'empleado3@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(5, 'empleado4@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(6, 'empleado5@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(7, 'empleado6@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(8, 'empleado7@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(9, 'empleado8@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(10, 'empleado9@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(11, 'empleado10@cobalsa.com', '123456', 'EMPLEADO', 'ACTIVO'),
(12, 'jeperez098@gmail.com', '123456', 'EMPLEADO', 'ACTIVO');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vacaciones`
--

CREATE TABLE `vacaciones` (
  `id_vacacion` int(11) NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `dias` int(11) NOT NULL,
  `estado` enum('PENDIENTE','APROBADA','RECHAZADA') DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `vacaciones`
--

INSERT INTO `vacaciones` (`id_vacacion`, `id_empleado`, `fecha_inicio`, `fecha_fin`, `dias`, `estado`) VALUES
(1, 1, '2026-07-01', '2026-07-15', 15, 'APROBADA'),
(3, 3, '2026-09-05', '2026-09-20', 15, 'APROBADA'),
(4, 11, '2026-06-10', '2027-07-10', 28, 'APROBADA');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  ADD PRIMARY KEY (`id_candidato`);

--
-- Indices de la tabla `cargos`
--
ALTER TABLE `cargos`
  ADD PRIMARY KEY (`id_cargo`);

--
-- Indices de la tabla `cargo_dias`
--
ALTER TABLE `cargo_dias`
  ADD PRIMARY KEY (`id_cargo_dia`),
  ADD KEY `id_cargo` (`id_cargo`);

--
-- Indices de la tabla `contratos`
--
ALTER TABLE `contratos`
  ADD PRIMARY KEY (`id_contrato`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`id_departamento`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleado`),
  ADD KEY `id_persona` (`id_persona`),
  ADD KEY `id_departamento` (`id_departamento`),
  ADD KEY `id_cargo` (`id_cargo`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `permisos`
--
ALTER TABLE `permisos`
  ADD PRIMARY KEY (`id_permiso`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `personas`
--
ALTER TABLE `personas`
  ADD PRIMARY KEY (`id_persona`),
  ADD UNIQUE KEY `documento` (`documento`);

--
-- Indices de la tabla `registros`
--
ALTER TABLE `registros`
  ADD PRIMARY KEY (`id_registro`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  ADD PRIMARY KEY (`id_accidente`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- Indices de la tabla `vacaciones`
--
ALTER TABLE `vacaciones`
  ADD PRIMARY KEY (`id_vacacion`),
  ADD KEY `id_empleado` (`id_empleado`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  MODIFY `id_candidato` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cargos`
--
ALTER TABLE `cargos`
  MODIFY `id_cargo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `cargo_dias`
--
ALTER TABLE `cargo_dias`
  MODIFY `id_cargo_dia` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `contratos`
--
ALTER TABLE `contratos`
  MODIFY `id_contrato` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `id_departamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `permisos`
--
ALTER TABLE `permisos`
  MODIFY `id_permiso` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `personas`
--
ALTER TABLE `personas`
  MODIFY `id_persona` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `id_registro` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  MODIFY `id_accidente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `vacaciones`
--
ALTER TABLE `vacaciones`
  MODIFY `id_vacacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cargo_dias`
--
ALTER TABLE `cargo_dias`
  ADD CONSTRAINT `cargo_dias_ibfk_1` FOREIGN KEY (`id_cargo`) REFERENCES `cargos` (`id_cargo`);

--
-- Filtros para la tabla `contratos`
--
ALTER TABLE `contratos`
  ADD CONSTRAINT `contratos_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

--
-- Filtros para la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD CONSTRAINT `empleados_ibfk_1` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  ADD CONSTRAINT `empleados_ibfk_2` FOREIGN KEY (`id_departamento`) REFERENCES `departamentos` (`id_departamento`),
  ADD CONSTRAINT `empleados_ibfk_3` FOREIGN KEY (`id_cargo`) REFERENCES `cargos` (`id_cargo`),
  ADD CONSTRAINT `empleados_ibfk_4` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `permisos`
--
ALTER TABLE `permisos`
  ADD CONSTRAINT `permisos_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

--
-- Filtros para la tabla `registros`
--
ALTER TABLE `registros`
  ADD CONSTRAINT `registros_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

--
-- Filtros para la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  ADD CONSTRAINT `sst_accidentes_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);

--
-- Filtros para la tabla `vacaciones`
--
ALTER TABLE `vacaciones`
  ADD CONSTRAINT `vacaciones_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
