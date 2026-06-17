<?php
// ============================================================
//  config.php — Configuración actualizada
// ============================================================

define('DB_HOST', 'localhost');
define('DB_USER', 'root');       // Cambia si tu usuario es diferente
define('DB_PASS', '');           // Cambia si tienes contraseña
define('DB_NAME', 'gestion_empleados');

// PIN del administrador (solo de referencia)
define('ADMIN_PIN', '999999');

// Iniciar sesión
session_start();

function getDB(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        try {
            $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
            $pdo = new PDO($dsn, DB_USER, DB_PASS, [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ]);
        } catch (PDOException $e) {
            die(json_encode(['error' => 'Error de conexión: ' . $e->getMessage()]));
        }
    }
    return $pdo;
}

function isAdmin(): bool {
    return isset($_SESSION['rol']) && $_SESSION['rol'] === 'admin';
}

function requireAdmin(): void {
    if (!isAdmin()) {
        header('Location: index.php');
        exit;
    }
}

function jsonResponse(array $data, int $code = 200): void {
    http_response_code($code);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}

// Helper para Tailwind (lo usaremos pronto)
function headTailwind(): void {
    echo '<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>';
}
?>