<?php
// install.php — Instalador automático del sistema

require_once 'config.php';

echo '<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instalación — Gestión de Empleados</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        body { font-family: system-ui, sans-serif; }
    </style>
</head>
<body class="bg-zinc-950 text-zinc-200 min-h-screen flex items-center justify-center">
<div class="max-w-lg mx-auto p-8">';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // Conexión sin base de datos seleccionada
        $pdo = new PDO("mysql:host=" . DB_HOST, DB_USER, DB_PASS, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
        ]);

        // Crear base de datos
        $pdo->exec("CREATE DATABASE IF NOT EXISTS " . DB_NAME . " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
        echo '<div class="bg-green-900/50 border border-green-600 rounded-2xl p-6 mb-6">
                <p class="text-green-400 font-medium">✓ Base de datos <strong>' . DB_NAME . '</strong> creada correctamente.</p>
              </div>';

        // Usar la base de datos
        $pdo->exec("USE " . DB_NAME);

        // Leer y ejecutar setup.sql
        $sql = file_get_contents('setup.sql');
        $pdo->exec($sql);

        echo '<div class="bg-green-900/50 border border-green-600 rounded-2xl p-6">
                <h2 class="text-2xl font-semibold mb-4 text-white">¡Instalación completada con éxito! 🎉</h2>
                <p class="mb-6">Ahora puedes acceder al sistema:</p>
                <div class="space-y-3">
                    <a href="index.php" class="block bg-white text-zinc-900 font-semibold text-center py-4 rounded-2xl hover:bg-amber-300 transition">
                        Ir al Login (PIN)
                    </a>
                    <p class="text-xs text-zinc-500 text-center">
                        Usuario administrador de prueba:<br>
                        <strong>PIN: 999999</strong>
                    </p>
                </div>
              </div>';

    } catch (Exception $e) {
        echo '<div class="bg-red-900/50 border border-red-600 rounded-2xl p-6">
                <h2 class="text-red-400 font-medium mb-3">Error durante la instalación</h2>
                <p class="text-sm text-red-300 whitespace-pre-wrap">' . htmlspecialchars($e->getMessage()) . '</p>
              </div>';
    }
} else {
    // Pantalla inicial
    ?>
    <div class="bg-zinc-900 border border-zinc-700 rounded-3xl p-10">
        <div class="flex items-center gap-4 mb-8">
            <div class="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-2xl">📋</div>
            <div>
                <h1 class="text-3xl font-semibold">Instalación del Sistema</h1>
                <p class="text-zinc-400">Gestión de Empleados con Control de Asistencia</p>
            </div>
        </div>

        <div class="space-y-6 text-sm">
            <div class="bg-zinc-800 rounded-2xl p-6">
                <p class="font-medium mb-2">Este instalador hará lo siguiente:</p>
                <ul class="space-y-2 text-zinc-400">
                    <li class="flex gap-2">✓ Crear la base de datos <strong>gestion_empleados</strong></li>
                    <li class="flex gap-2">✓ Crear todas las tablas</li>
                    <li class="flex gap-2">✓ Insertar departamentos, cargos y datos de ejemplo</li>
                    <li class="flex gap-2">✓ Crear usuario administrador (PIN 999999)</li>
                </ul>
            </div>

            <form method="POST">
                <button type="submit" 
                        class="w-full bg-white hover:bg-amber-300 transition text-zinc-900 font-semibold py-4 rounded-2xl text-lg">
                    Iniciar Instalación Automática
                </button>
            </form>

            <p class="text-center text-xs text-zinc-500">
                Asegúrate de que el usuario <strong><?= DB_USER ?></strong> tenga permisos para crear bases de datos.
            </p>
        </div>
    </div>
    <?php
}

echo '</div></body></html>';
?>