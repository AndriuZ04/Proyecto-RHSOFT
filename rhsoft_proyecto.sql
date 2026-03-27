-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 27-03-2026 a las 13:19:41
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
-- Base de datos: `rhsoft_proyecto`
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

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `ID_Departamento` int(11) NOT NULL,
  `Nombre_Departamento` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  MODIFY `ID_Candidato` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cargos`
--
ALTER TABLE `cargos`
  MODIFY `ID_Cargo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `contratos`
--
ALTER TABLE `contratos`
  MODIFY `ID_Contrato` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `ID_Departamento` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `ID_Empleado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `personas`
--
ALTER TABLE `personas`
  MODIFY `ID_Persona` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `registros`
--
ALTER TABLE `registros`
  MODIFY `ID_Registro` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sst_accidentes`
--
ALTER TABLE `sst_accidentes`
  MODIFY `ID_Accidente` int(11) NOT NULL AUTO_INCREMENT;

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
