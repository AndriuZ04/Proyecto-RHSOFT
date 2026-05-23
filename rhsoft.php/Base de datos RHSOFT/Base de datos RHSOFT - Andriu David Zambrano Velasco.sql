-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 09-04-2026 a las 17:14:50
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
-- Base de datos: `rhsoft`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `candidatos`
--

CREATE TABLE `candidatos` (
  `ID_Candidato` int(11) NOT NULL,
  `ID_Persona` int(11) NOT NULL,
  `ID_Cargo` int(11) NOT NULL,
  `Fecha_Postulacion` date DEFAULT NULL,
  `Estado_Candidato` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `candidatos`
--

INSERT INTO `candidatos` (`ID_Candidato`, `ID_Persona`, `ID_Cargo`, `Fecha_Postulacion`, `Estado_Candidato`) VALUES
(1, 1, 1, '2025-02-15', 'En proceso'),
(2, 2, 2, '2025-02-17', 'Aprobado'),
(3, 3, 3, '2025-02-20', 'Rechazado'),
(4, 4, 1, '2025-02-23', 'Contratado'),
(5, 5, 2, '2025-02-25', 'En proceso'),
(6, 6, 3, '2025-02-27', 'Aprobado'),
(7, 7, 1, '2025-03-02', 'Rechazado'),
(8, 8, 2, '2025-03-05', 'En proceso'),
(9, 9, 3, '2025-03-09', 'Contratado'),
(10, 10, 1, '2025-03-13', 'Aprobado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cargos`
--

CREATE TABLE `cargos` (
  `ID_Cargo` int(11) NOT NULL,
  `ID_Departamento` int(11) NOT NULL,
  `Nombre_Cargo` varchar(150) NOT NULL,
  `Descripcion_Funciones` varchar(500) DEFAULT NULL,
  `Salario_Base` decimal(15,2) DEFAULT NULL,
  `Hora_Inicio_Jornada` time DEFAULT NULL,
  `Hora_Fin_Jornada` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cargos`
--

INSERT INTO `cargos` (`ID_Cargo`, `ID_Departamento`, `Nombre_Cargo`, `Descripcion_Funciones`, `Salario_Base`, `Hora_Inicio_Jornada`, `Hora_Fin_Jornada`) VALUES
(1, 1, 'Administrativa', 'Funciones del cargo', 2000000.00, '07:00:00', '16:00:00'),
(2, 3, 'Produccion', 'Funciones del cargo', 2000000.00, '07:00:00', '16:00:00'),
(3, 4, 'calidad y seguridad', 'Funciones del cargo', 2000000.00, '07:00:00', '16:00:00'),
(4, 2, 'Comercial', 'Funciones del cargo', 2000000.00, '07:00:00', '16:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cargo_dias`
--

CREATE TABLE `cargo_dias` (
  `ID_Cargo` int(11) NOT NULL,
  `Dia_Semana` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contratos`
--

CREATE TABLE `contratos` (
  `ID_Contrato` int(11) NOT NULL,
  `ID_Empleado` int(11) DEFAULT NULL,
  `ID_Cargo` int(11) NOT NULL,
  `Tipo_Contrato` varchar(100) DEFAULT NULL,
  `Salario_Pactado` decimal(15,2) DEFAULT NULL,
  `Fecha_Inicio` date DEFAULT NULL,
  `Fecha_Fin` date DEFAULT NULL,
  `Estado_Contrato` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `contratos`
--

INSERT INTO `contratos` (`ID_Contrato`, `ID_Empleado`, `ID_Cargo`, `Tipo_Contrato`, `Salario_Pactado`, `Fecha_Inicio`, `Fecha_Fin`, `Estado_Contrato`) VALUES
(1, 1, 1, 'Indefinido', 2500.00, '2025-03-01', NULL, 'Vigente'),
(2, 2, 2, 'Temporal', 1800.00, '2025-03-10', '2025-08-31', 'Vigente'),
(3, 3, 3, 'Prácticas', 1200.00, '2025-03-29', '2025-09-30', 'Vigente'),
(4, 4, 1, 'Indefinido', 2600.00, '2025-04-12', NULL, 'Vigente'),
(5, 5, 2, 'Temporal', 1700.00, '2025-04-29', '2025-10-31', 'Vigente'),
(6, 6, 3, 'Indefinido', 3000.00, '2025-05-08', NULL, 'Vigente'),
(7, 7, 1, 'Temporal', 2000.00, '2025-05-29', '2025-11-30', 'Suspendido'),
(8, 8, 2, 'Indefinido', 2800.00, '2025-06-12', NULL, 'Vigente'),
(9, 9, 3, 'Prácticas', 1300.00, '2025-06-29', '2025-12-31', 'Vigente'),
(10, 10, 1, 'Indefinido', 3100.00, '2025-07-08', NULL, 'Terminado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `ID_Departamento` int(11) NOT NULL,
  `Nombre_Departamento` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `departamentos`
--

INSERT INTO `departamentos` (`ID_Departamento`, `Nombre_Departamento`) VALUES
(1, 'administrativo'),
(2, 'Financiero'),
(3, 'produccion y empaquetamiento'),
(4, 'calidad');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `ID_Empleado` int(11) NOT NULL,
  `ID_Persona` int(11) NOT NULL,
  `ID_Cargo` int(11) NOT NULL,
  `Fecha_Ingreso` date DEFAULT NULL,
  `Fecha_Retiro` date DEFAULT NULL,
  `Estado_Empleado` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`ID_Empleado`, `ID_Persona`, `ID_Cargo`, `Fecha_Ingreso`, `Fecha_Retiro`, `Estado_Empleado`) VALUES
(1, 1, 2, '2022-01-01', NULL, 'Activo'),
(2, 2, 3, '2022-01-01', NULL, 'Activo'),
(3, 3, 4, '2022-01-01', NULL, 'Activo'),
(4, 4, 1, '2022-01-01', NULL, 'Activo'),
(5, 5, 1, '2022-01-01', NULL, 'Activo'),
(6, 6, 4, '2022-01-01', NULL, 'Activo'),
(7, 7, 4, '2022-01-01', NULL, 'Activo'),
(8, 8, 3, '2022-01-01', NULL, 'Activo'),
(9, 9, 3, '2022-01-01', NULL, 'Activo'),
(10, 10, 2, '2022-01-01', NULL, 'Activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `personas`
--

CREATE TABLE `personas` (
  `ID_Persona` int(11) NOT NULL,
  `Numero_Documento` varchar(50) NOT NULL,
  `Nombres` varchar(150) NOT NULL,
  `Apellidos` varchar(150) NOT NULL,
  `Email` varchar(150) DEFAULT NULL,
  `Telefono` varchar(30) DEFAULT NULL,
  `Fecha_Nacimiento` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `personas`
--

INSERT INTO `personas` (`ID_Persona`, `Numero_Documento`, `Nombres`, `Apellidos`, `Email`, `Telefono`, `Fecha_Nacimiento`) VALUES
(1, '1001', 'cristian', 'Escobar', 'crisesa@gmail.com', '300000001', '1994-11-10'),
(2, '1002', 'jack', 'Perez', 'jperez@mail.com', '300000002', '1995-10-11'),
(3, '1003', 'alejandro', 'Zapata', 'Azapa12@gmail.com', '300000003', '1995-10-20'),
(4, '1004', 'mateo', 'Rodrigues', 'user4@mail.com', '300000004', '1996-08-08'),
(5, '1005', 'Andriu', 'Zambrano', 'user5@mail.com', '300000005', '1996-03-06'),
(6, '1006', 'manuel', 'Gonzales', 'manuel.gonzales@mail.com', '300000006', '1995-11-24'),
(7, '1007', 'alejandro', 'Zambrano', 'user7@mail.com', '300000007', '1996-05-30'),
(8, '1008', 'maria', 'Sarmiento', 'user8@mail.com', '300000008', '1997-02-05'),
(9, '1009', 'marta', 'Lopez', 'user9@mail.com', '300000009', '1995-11-02'),
(10, '10010', 'mariana', 'Padilla', 'user10@mail.com', '300000010', '1996-03-29');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registros`
--

CREATE TABLE `registros` (
  `ID_Registro` int(11) NOT NULL,
  `ID_Empleado` int(11) NOT NULL,
  `Fecha` date DEFAULT NULL,
  `Hora_Entrada` time DEFAULT NULL,
  `Hora_Salida` time DEFAULT NULL,
  `Tipo` varchar(80) DEFAULT NULL,
  `Observacion` varchar(300) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `registros`
--

INSERT INTO `registros` (`ID_Registro`, `ID_Empleado`, `Fecha`, `Hora_Entrada`, `Hora_Salida`, `Tipo`, `Observacion`) VALUES
(1, 1, '2025-05-01', '08:00:00', '17:00:00', 'Normal', NULL),
(2, 2, '2025-05-01', '08:10:00', '17:05:00', 'Tarde', 'Llegó tarde'),
(3, 3, '2025-05-01', '07:55:00', '16:50:00', 'Normal', NULL),
(4, 4, '2025-05-02', '08:00:00', '17:00:00', 'Normal', NULL),
(5, 5, '2025-05-02', '08:20:00', '17:10:00', 'Tarde', 'Trafico'),
(6, 6, '2025-05-02', '08:00:00', '16:00:00', 'Salida anticipada', 'Cita médica'),
(7, 7, '2025-05-03', '08:05:00', '17:00:00', 'Normal', NULL),
(8, 8, '2025-05-03', '08:00:00', NULL, 'Entrada', 'Sin salida registrada'),
(9, 9, '2025-05-03', '07:50:00', '17:10:00', 'Normal', NULL),
(10, 10, '2025-05-04', '08:00:00', '17:00:00', 'Normal', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sst_accidentes`
--

CREATE TABLE `sst_accidentes` (
  `ID_Accidente` int(11) NOT NULL,
  `ID_Empleado` int(11) NOT NULL,
  `Fecha_Accidente` date DEFAULT NULL,
  `Tipo_Accidente` varchar(100) DEFAULT NULL,
  `Descripcion` varchar(500) DEFAULT NULL,
  `Accion_Inmediata` varchar(500) DEFAULT NULL,
  `Fecha_Reporte` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sst_accidentes`
--

INSERT INTO `sst_accidentes` (`ID_Accidente`, `ID_Empleado`, `Fecha_Accidente`, `Tipo_Accidente`, `Descripcion`, `Accion_Inmediata`, `Fecha_Reporte`) VALUES
(1, 1, '2025-03-05', 'Caída', 'Resbalón en piso mojado', 'Primeros auxilios', '2025-03-05'),
(2, 2, '2025-03-12', 'Corte', 'Herida con herramienta', 'Curación', '2025-03-12'),
(3, 3, '2025-03-20', 'Golpe', 'Objeto cayó sobre brazo', 'Evaluación médica', '2025-03-20'),
(4, 4, '2025-03-29', 'Quemadura', 'Contacto con superficie caliente', 'Aplicación de crema', '2025-03-29'),
(5, 5, '2025-04-07', 'Caída', 'Caída desde escalera', 'Reposo', '2025-04-07'),
(6, 6, '2025-04-12', 'Intoxicación', 'Inhalación de químicos', 'Atención médica', '2025-04-12'),
(7, 7, '2025-04-17', 'Corte', 'Corte leve en dedo', 'Vendaje', '2025-04-17'),
(8, 8, '2025-04-22', 'Golpe', 'Golpe contra maquinaria', 'Observación', '2025-04-22'),
(9, 9, '2025-04-29', 'Caída', 'Tropiezo en pasillo', 'Hielo', '2025-04-29'),
(10, 10, '2025-05-03', 'Quemadura', 'Salpicadura caliente', 'Curación', '2025-05-03');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  ADD PRIMARY KEY (`ID_Candidato`),
  ADD KEY `FK_Candidato_Persona` (`ID_Persona`),
  ADD KEY `FK_Candidato_Cargo` (`ID_Cargo`);

--
-- Indices de la tabla `cargos`
--
ALTER TABLE `cargos`
  ADD PRIMARY KEY (`ID_Cargo`),
  ADD KEY `FK_Cargo_Departamento` (`ID_Departamento`);

--
-- Indices de la tabla `cargo_dias`
--
ALTER TABLE `cargo_dias`
  ADD PRIMARY KEY (`ID_Cargo`,`Dia_Semana`);

--
-- Indices de la tabla `contratos`
--
ALTER TABLE `contratos`
  ADD PRIMARY KEY (`ID_Contrato`),
  ADD KEY `FK_Contrato_Empleado` (`ID_Empleado`),
  ADD KEY `FK_Contrato_Cargo` (`ID_Cargo`);

--
-- Indices de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`ID_Departamento`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`ID_Empleado`),
  ADD KEY `FK_Empleado_Persona` (`ID_Persona`),
  ADD KEY `FK_Empleado_Cargo` (`ID_Cargo`);

--
-- Indices de la tabla `personas`
--
ALTER TABLE `personas`
  ADD PRIMARY KEY (`ID_Persona`),
  ADD UNIQUE KEY `UK_Numero_Documento` (`Numero_Documento`);

--
-- Indices de la tabla `registros`
--
ALTER TABLE `registros`
  ADD PRIMARY KEY (`ID_Registro`),
  ADD KEY `FK_Registro_Empleado` (`ID_Empleado`);

--
-- Indices de la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  ADD PRIMARY KEY (`ID_Accidente`),
  ADD KEY `FK_Accidente_Empleado` (`ID_Empleado`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `candidatos`
--
ALTER TABLE `candidatos`
  MODIFY `ID_Candidato` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `cargos`
--
ALTER TABLE `cargos`
  MODIFY `ID_Cargo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `contratos`
--
ALTER TABLE `contratos`
  MODIFY `ID_Contrato` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `ID_Departamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `ID_Empleado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `personas`
--
ALTER TABLE `personas`
  MODIFY `ID_Persona` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `ID_Registro` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  MODIFY `ID_Accidente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `candidatos`
--
ALTER TABLE `candidatos`
  ADD CONSTRAINT `FK_Candidato_Cargo` FOREIGN KEY (`ID_Cargo`) REFERENCES `cargos` (`ID_Cargo`),
  ADD CONSTRAINT `FK_Candidato_Persona` FOREIGN KEY (`ID_Persona`) REFERENCES `personas` (`ID_Persona`);

--
-- Filtros para la tabla `cargos`
--
ALTER TABLE `cargos`
  ADD CONSTRAINT `FK_Cargo_Departamento` FOREIGN KEY (`ID_Departamento`) REFERENCES `departamentos` (`ID_Departamento`);

--
-- Filtros para la tabla `cargo_dias`
--
ALTER TABLE `cargo_dias`
  ADD CONSTRAINT `FK_CargoDias_Cargo` FOREIGN KEY (`ID_Cargo`) REFERENCES `cargos` (`ID_Cargo`);

--
-- Filtros para la tabla `contratos`
--
ALTER TABLE `contratos`
  ADD CONSTRAINT `FK_Contrato_Cargo` FOREIGN KEY (`ID_Cargo`) REFERENCES `cargos` (`ID_Cargo`),
  ADD CONSTRAINT `FK_Contrato_Empleado` FOREIGN KEY (`ID_Empleado`) REFERENCES `empleados` (`ID_Empleado`);

--
-- Filtros para la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD CONSTRAINT `FK_Empleado_Cargo` FOREIGN KEY (`ID_Cargo`) REFERENCES `cargos` (`ID_Cargo`),
  ADD CONSTRAINT `FK_Empleado_Persona` FOREIGN KEY (`ID_Persona`) REFERENCES `personas` (`ID_Persona`);

--
-- Filtros para la tabla `registros`
--
ALTER TABLE `registros`
  ADD CONSTRAINT `FK_Registro_Empleado` FOREIGN KEY (`ID_Empleado`) REFERENCES `empleados` (`ID_Empleado`);

--
-- Filtros para la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  ADD CONSTRAINT `FK_Accidente_Empleado` FOREIGN KEY (`ID_Empleado`) REFERENCES `empleados` (`ID_Empleado`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
