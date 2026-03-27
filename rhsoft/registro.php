<?php
require_once 'config.php';

// Redirigir si no hay sesión
if (!isset($_SESSION['empleado_id'])) {
    header('Location: index.php');
    exit;
}

$db        = getDB();
$empId     = $_SESSION['empleado_id'];
$nombre    = $_SESSION['nombre'];
$esAdmin   = isAdmin();

// ── AJAX: marcar entrada ─────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion'])) {
    header('Content-Type: application/json');

    if ($_POST['accion'] === 'entrada') {
        $hoy = date('Y-m-d');
        // Verificar que no haya marcado hoy
        $chk = $db->prepare("SELECT ID_Registro FROM REGISTROS WHERE ID_Empleado=? AND Fecha=? AND Hora_Salida IS NULL");
        $chk->execute([$empId, $hoy]);
        if ($chk->fetch()) {
            echo json_encode(['ok' => false, 'msg' => 'Ya tienes una entrada activa hoy.']);
            exit;
        }
        $chk2 = $db->prepare("SELECT ID_Registro FROM REGISTROS WHERE ID_Empleado=? AND Fecha=? AND Hora_Salida IS NOT NULL");
        $chk2->execute([$empId, $hoy]);
        if ($chk2->fetch()) {
            echo json_encode(['ok' => false, 'msg' => 'Ya completaste tu jornada de hoy.']);
            exit;
        }
        $ins = $db->prepare("INSERT INTO REGISTROS (ID_Empleado, Fecha, Hora_Entrada, Tipo) VALUES (?,?,NOW(),'Normal')");
        $ins->execute([$empId, $hoy]);
        echo json_encode(['ok' => true, 'hora' => date('H:i:s'), 'msg' => '¡Entrada registrada con éxito!']);
        exit;
    }

    if ($_POST['accion'] === 'salida') {
        $hoy = date('Y-m-d');
        $chk = $db->prepare("SELECT ID_Registro FROM REGISTROS WHERE ID_Empleado=? AND Fecha=? AND Hora_Salida IS NULL");
        $chk->execute([$empId, $hoy]);
        $reg = $chk->fetch();
        if (!$reg) {
            echo json_encode(['ok' => false, 'msg' => 'No hay entrada activa para registrar salida.']);
            exit;
        }
        $upd = $db->prepare("UPDATE REGISTROS SET Hora_Salida=NOW() WHERE ID_Registro=?");
        $upd->execute([$reg['ID_Registro']]);
        echo json_encode(['ok' => true, 'hora' => date('H:i:s'), 'msg' => '¡Salida registrada con éxito!']);
        exit;
    }
    exit;
}

// ── Datos del empleado ───────────────────────────────────────
$stmt = $db->prepare("
    SELECT e.*, p.Nombres, p.Apellidos, p.Email, p.Telefono, p.Numero_Documento,
           c.Nombre_Cargo, d.Nombre_Departamento,
           c.Hora_Inicio_Jornada, c.Hora_Fin_Jornada
    FROM   EMPLEADOS    e
    JOIN   PERSONAS     p ON p.ID_Persona = e.ID_Persona
    JOIN   CARGOS       c ON c.ID_Cargo   = e.ID_Cargo
    JOIN   DEPARTAMENTOS d ON d.ID_Departamento = c.ID_Departamento
    WHERE  e.ID_Empleado = ?
");
$stmt->execute([$empId]);
$emp = $stmt->fetch();

// ── Estado de hoy ────────────────────────────────────────────
$hoy = date('Y-m-d');
$stHoy = $db->prepare("SELECT * FROM REGISTROS WHERE ID_Empleado=? AND Fecha=? ORDER BY ID_Registro DESC LIMIT 1");
$stHoy->execute([$empId, $hoy]);
$registroHoy = $stHoy->fetch();

$hayEntrada = $registroHoy && $registroHoy['Hora_Entrada'];
$haySalida  = $registroHoy && $registroHoy['Hora_Salida'];

// ── Historial (últimos 30 días) ──────────────────────────────
$hist = $db->prepare("
    SELECT * FROM REGISTROS
    WHERE  ID_Empleado = ?
    ORDER  BY Fecha DESC, Hora_Entrada DESC
    LIMIT  30
");
$hist->execute([$empId]);
$historial = $hist->fetchAll();

// ── Estadísticas del mes ─────────────────────────────────────
$mesInicio = date('Y-m-01');
$stats = $db->prepare("
    SELECT
        COUNT(*) AS total_dias,
        SUM(CASE WHEN Hora_Salida IS NOT NULL THEN 1 ELSE 0 END) AS dias_completos,
        SEC_TO_TIME(AVG(CASE WHEN Hora_Salida IS NOT NULL
            THEN TIME_TO_SEC(TIMEDIFF(Hora_Salida, Hora_Entrada)) END)) AS promedio_horas
    FROM REGISTROS
    WHERE ID_Empleado=? AND Fecha >= ?
");
$stats->execute([$empId, $mesInicio]);
$estadisticas = $stats->fetch();
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Registro de Asistencia — <?= htmlspecialchars($nombre) ?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">
<style>
  :root {
    --azul-oscuro : #355872;
    --azul-medio  : #7aaace;
    --azul-claro  : #9cd5ff;
    --blanco-roto : #f7f8f0;
    --texto       : #1e3344;
    --fondo       : #eef2f6;
    --sombra      : 0 4px 24px rgba(53,88,114,.12);
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--fondo);
    color: var(--texto);
    min-height: 100vh;
  }

  /* ── Sidebar ── */
  .sidebar {
    position: fixed; top: 0; left: 0; bottom: 0;
    width: 260px;
    background: var(--azul-oscuro);
    padding: 32px 24px;
    display: flex; flex-direction: column;
    z-index: 100;
  }

  .sidebar-logo {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 40px;
  }

  .sidebar-logo .icon {
    width: 40px; height: 40px;
    background: rgba(255,255,255,.15);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
  }

  .sidebar-logo .icon svg { width: 20px; fill: white; }

  .sidebar-logo span {
    font-family: 'DM Serif Display', serif;
    color: white;
    font-size: 1.05rem;
    line-height: 1.2;
  }

  .nav-section {
    font-size: .72rem;
    color: rgba(255,255,255,.4);
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 24px;
  }

  .nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 14px;
    border-radius: 10px;
    color: rgba(255,255,255,.7);
    text-decoration: none;
    font-size: .92rem;
    transition: all .2s;
    margin-bottom: 4px;
  }

  .nav-item svg { width: 18px; fill: currentColor; flex-shrink: 0; }
  .nav-item:hover { background: rgba(255,255,255,.1); color: white; }
  .nav-item.active { background: rgba(255,255,255,.18); color: white; font-weight: 600; }

  .sidebar-footer {
    margin-top: auto;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,.1);
  }

  .user-chip {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px;
    background: rgba(255,255,255,.1);
    border-radius: 12px;
    margin-bottom: 10px;
  }

  .user-avatar {
    width: 36px; height: 36px;
    background: var(--azul-medio);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; color: white; font-size: .9rem;
    flex-shrink: 0;
  }

  .user-info span { display: block; }
  .user-info .uname { color: white; font-size: .88rem; font-weight: 500; }
  .user-info .urole { color: rgba(255,255,255,.5); font-size: .75rem; text-transform: capitalize; }

  .logout-btn {
    display: flex; align-items: center; gap: 8px;
    width: 100%;
    padding: 10px 14px;
    background: none;
    border: 1.5px solid rgba(255,255,255,.15);
    border-radius: 10px;
    color: rgba(255,255,255,.6);
    font-family: 'DM Sans', sans-serif;
    font-size: .88rem;
    cursor: pointer;
    transition: all .2s;
  }

  .logout-btn svg { width: 16px; fill: currentColor; }
  .logout-btn:hover { border-color: rgba(255,255,255,.4); color: white; }

  /* ── Contenido principal ── */
  .main {
    margin-left: 260px;
    padding: 36px 40px;
    min-height: 100vh;
  }

  .page-header {
    margin-bottom: 32px;
  }

  .page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--texto);
    margin-bottom: 4px;
  }

  .page-header p { color: var(--azul-oscuro); opacity: .6; font-size: .92rem; }

  /* ── Reloj ── */
  .clock-widget {
    background: var(--azul-oscuro);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    color: white;
    position: relative;
    overflow: hidden;
  }

  .clock-widget::before {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(122,170,206,.15);
  }

  .clock-time {
    font-family: 'DM Serif Display', serif;
    font-size: 3.5rem;
    line-height: 1;
    letter-spacing: -.02em;
  }

  .clock-date { opacity: .6; font-size: .9rem; margin-top: 4px; }

  .clock-actions { display: flex; gap: 12px; flex-shrink: 0; position: relative; z-index: 1; }

  .action-btn {
    padding: 14px 28px;
    border: none;
    border-radius: 14px;
    font-family: 'DM Sans', sans-serif;
    font-size: .95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s;
    display: flex; align-items: center; gap: 8px;
  }

  .btn-entrada {
    background: var(--azul-claro);
    color: var(--texto);
  }
  .btn-entrada:hover:not(:disabled) { filter: brightness(1.08); transform: translateY(-2px); }

  .btn-salida {
    background: rgba(255,255,255,.15);
    color: white;
    border: 1.5px solid rgba(255,255,255,.3);
  }
  .btn-salida:hover:not(:disabled) { background: rgba(255,255,255,.25); transform: translateY(-2px); }

  .action-btn:disabled { opacity: .4; cursor: not-allowed; transform: none !important; }

  /* ── Toast ── */
  .toast {
    position: fixed;
    bottom: 32px; right: 32px;
    background: var(--texto);
    color: white;
    padding: 14px 20px;
    border-radius: 14px;
    font-size: .92rem;
    font-weight: 500;
    box-shadow: 0 8px 32px rgba(0,0,0,.2);
    transform: translateY(80px);
    opacity: 0;
    transition: all .35s cubic-bezier(.22,1,.36,1);
    z-index: 999;
    max-width: 320px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .toast.show { transform: translateY(0); opacity: 1; }
  .toast.success { background: #1a6344; }
  .toast.error   { background: #8b2020; }

  /* ── Grid de estadísticas ── */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }

  .stat-card {
    background: white;
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: var(--sombra);
  }

  .stat-card .stat-label {
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--azul-oscuro);
    opacity: .55;
    margin-bottom: 8px;
  }

  .stat-card .stat-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--texto);
    line-height: 1;
  }

  .stat-card .stat-sub { font-size: .82rem; color: var(--azul-oscuro); opacity: .5; margin-top: 4px; }

  /* ── Estado de hoy ── */
  .today-card {
    background: white;
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: var(--sombra);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .status-dot {
    width: 14px; height: 14px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .status-dot.verde  { background: #27ae60; box-shadow: 0 0 0 4px rgba(39,174,96,.15); }
  .status-dot.amarillo { background: #f39c12; box-shadow: 0 0 0 4px rgba(243,156,18,.15); }
  .status-dot.gris   { background: #bdc3c7; }

  .today-info .label { font-size: .8rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; color: var(--azul-oscuro); opacity: .5; }
  .today-info .value { font-size: 1.05rem; font-weight: 600; color: var(--texto); margin-top: 2px; }

  .today-times { display: flex; gap: 32px; margin-left: auto; }

  .time-block .t-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--azul-oscuro); opacity: .5; }
  .time-block .t-value { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: var(--texto); }

  /* ── Historial ── */
  .section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: var(--texto);
    margin-bottom: 16px;
  }

  .table-wrap {
    background: white;
    border-radius: 16px;
    box-shadow: var(--sombra);
    overflow: hidden;
  }

  table { width: 100%; border-collapse: collapse; }

  thead th {
    padding: 14px 20px;
    text-align: left;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .07em;
    text-transform: uppercase;
    color: var(--azul-oscuro);
    opacity: .55;
    background: rgba(53,88,114,.04);
    border-bottom: 1px solid rgba(53,88,114,.08);
  }

  tbody td {
    padding: 14px 20px;
    font-size: .9rem;
    color: var(--texto);
    border-bottom: 1px solid rgba(53,88,114,.06);
  }

  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: rgba(53,88,114,.03); }

  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: .75rem;
    font-weight: 600;
  }

  .badge-ok      { background: rgba(39,174,96,.12);  color: #1a6344; }
  .badge-parcial { background: rgba(243,156,18,.12); color: #7d5a00; }
  .badge-tipo    { background: rgba(53,88,114,.1);   color: var(--azul-oscuro); }

  .empty-state {
    text-align: center;
    padding: 48px;
    color: var(--azul-oscuro);
    opacity: .4;
  }

  /* ── Responsive ── */
  @media (max-width: 900px) {
    .sidebar { width: 220px; }
    .main    { margin-left: 220px; padding: 24px 20px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .clock-time { font-size: 2.4rem; }
  }

  @media (max-width: 640px) {
    .sidebar { display: none; }
    .main    { margin-left: 0; padding: 20px 16px; }
    .stats-grid { grid-template-columns: 1fr; }
    .clock-widget { flex-direction: column; align-items: flex-start; }
    .today-times { flex-wrap: wrap; gap: 16px; }
  }
</style>
</head>
<body>

<!-- ── Sidebar ────────────────────────────── -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="icon">
      <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
    </div>
    <span>Gestión<br>Empresarial</span>
  </div>

  <div class="nav-section">Módulos</div>
  <a href="registro.php" class="nav-item active">
    <svg viewBox="0 0 24 24"><path d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>
    Registro de asistencia
  </a>
  <?php if ($esAdmin): ?>
  <a href="admin.php" class="nav-item">
    <svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
    Gestión de empleados
  </a>
  <?php endif; ?>

  <div class="sidebar-footer">
    <div class="user-chip">
      <div class="user-avatar"><?= strtoupper(substr($emp['Nombres'],0,1) . substr($emp['Apellidos'],0,1)) ?></div>
      <div class="user-info">
        <span class="uname"><?= htmlspecialchars($emp['Nombres'] . ' ' . $emp['Apellidos']) ?></span>
        <span class="urole"><?= htmlspecialchars($_SESSION['rol']) ?></span>
      </div>
    </div>
    <button class="logout-btn" onclick="location.href='index.php?logout=1'">
      <svg viewBox="0 0 24 24"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
      Cerrar sesión
    </button>
  </div>
</aside>

<!-- ── Contenido ────────────────────────── -->
<main class="main">
  <div class="page-header">
    <h1>Registro de Asistencia</h1>
    <p><?= date('l, d \d\e F \d\e Y') ?> · <?= htmlspecialchars($emp['Nombre_Departamento']) ?> — <?= htmlspecialchars($emp['Nombre_Cargo']) ?></p>
  </div>

  <!-- Reloj y botones de marcación -->
  <div class="clock-widget">
    <div>
      <div class="clock-time" id="reloj">--:--:--</div>
      <div class="clock-date"><?= date('d/m/Y') ?></div>
    </div>
    <div class="clock-actions">
      <button class="action-btn btn-entrada" id="btnEntrada"
        <?= ($hayEntrada) ? 'disabled' : '' ?>
        onclick="marcar('entrada')">
        <svg width="18" viewBox="0 0 24 24" fill="currentColor"><path d="M11 16l-4-4 4-4 1.41 1.41L10.83 11H18v2h-7.17l1.59 1.59L11 16zm-6 3H5V5h2V3H5C3.9 3 3 3.9 3 5v14c0 1.1.9 2 2 2h2v-2H5z"/></svg>
        Registrar Entrada
      </button>
      <button class="action-btn btn-salida" id="btnSalida"
        <?= (!$hayEntrada || $haySalida) ? 'disabled' : '' ?>
        onclick="marcar('salida')">
        <svg width="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13 8l4 4-4 4-1.41-1.41L13.17 13H6v-2h7.17l-1.58-1.59L13 8zm4 11h-2v2h2c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-2v2h2v14z"/></svg>
        Registrar Salida
      </button>
    </div>
  </div>

  <!-- Estado de hoy -->
  <div class="today-card">
    <?php
      $dotClass = 'gris';
      $estadoTxt = 'Sin registro hoy';
      if ($hayEntrada && !$haySalida) { $dotClass = 'verde'; $estadoTxt = 'Jornada en curso'; }
      if ($hayEntrada && $haySalida)  { $dotClass = 'amarillo'; $estadoTxt = 'Jornada completada'; }
    ?>
    <div class="status-dot <?= $dotClass ?>"></div>
    <div class="today-info">
      <div class="label">Estado hoy</div>
      <div class="value"><?= $estadoTxt ?></div>
    </div>
    <?php if ($hayEntrada): ?>
    <div class="today-times">
      <div class="time-block">
        <div class="t-label">Entrada</div>
        <div class="t-value" id="horaEntradaHoy"><?= substr($registroHoy['Hora_Entrada'],0,5) ?></div>
      </div>
      <?php if ($haySalida): ?>
      <div class="time-block">
        <div class="t-label">Salida</div>
        <div class="t-value"><?= substr($registroHoy['Hora_Salida'],0,5) ?></div>
      </div>
      <div class="time-block">
        <div class="t-label">Duración</div>
        <div class="t-value">
          <?php
            $ini = new DateTime($registroHoy['Hora_Entrada']);
            $fin = new DateTime($registroHoy['Hora_Salida']);
            $dur = $ini->diff($fin);
            echo $dur->format('%H:%I') . 'h';
          ?>
        </div>
      </div>
      <?php endif; ?>
    </div>
    <?php endif; ?>
  </div>

  <!-- Estadísticas del mes -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Días registrados</div>
      <div class="stat-value"><?= $estadisticas['total_dias'] ?? 0 ?></div>
      <div class="stat-sub">Este mes</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Jornadas completas</div>
      <div class="stat-value"><?= $estadisticas['dias_completos'] ?? 0 ?></div>
      <div class="stat-sub">Con entrada y salida</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Promedio de horas</div>
      <div class="stat-value"><?= $estadisticas['promedio_horas'] ? substr($estadisticas['promedio_horas'],0,5) : '--' ?></div>
      <div class="stat-sub">Por jornada completa</div>
    </div>
  </div>

  <!-- Historial -->
  <div class="section-title">Historial reciente</div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Entrada</th>
          <th>Salida</th>
          <th>Duración</th>
          <th>Tipo</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        <?php if (empty($historial)): ?>
        <tr><td colspan="6"><div class="empty-state">No hay registros aún</div></td></tr>
        <?php else: foreach ($historial as $r): ?>
        <tr>
          <td><?= date('d/m/Y', strtotime($r['Fecha'])) ?></td>
          <td><?= $r['Hora_Entrada'] ? substr($r['Hora_Entrada'],0,5) : '—' ?></td>
          <td><?= $r['Hora_Salida']  ? substr($r['Hora_Salida'],0,5)  : '—' ?></td>
          <td>
            <?php
              if ($r['Hora_Entrada'] && $r['Hora_Salida']) {
                $ini = new DateTime($r['Hora_Entrada']);
                $fin = new DateTime($r['Hora_Salida']);
                echo $ini->diff($fin)->format('%H:%I') . 'h';
              } else { echo '—'; }
            ?>
          </td>
          <td><span class="badge badge-tipo"><?= htmlspecialchars($r['Tipo']) ?></span></td>
          <td>
            <?php if ($r['Hora_Salida']): ?>
              <span class="badge badge-ok">Completo</span>
            <?php else: ?>
              <span class="badge badge-parcial">En curso</span>
            <?php endif; ?>
          </td>
        </tr>
        <?php endforeach; endif; ?>
      </tbody>
    </table>
  </div>
</main>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
// Reloj en tiempo real
function tick() {
  const now = new Date();
  document.getElementById('reloj').textContent =
    now.toLocaleTimeString('es-CO', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
}
tick(); setInterval(tick, 1000);

// Marcar entrada/salida
async function marcar(accion) {
  const btnE = document.getElementById('btnEntrada');
  const btnS = document.getElementById('btnSalida');
  btnE.disabled = btnS.disabled = true;

  const fd = new FormData();
  fd.append('accion', accion);

  try {
    const res  = await fetch('registro.php', { method:'POST', body: fd });
    const data = await res.json();
    showToast(data.msg, data.ok ? 'success' : 'error');

    if (data.ok) {
      // Recargar para actualizar estado
      setTimeout(() => location.reload(), 1500);
    } else {
      btnE.disabled = <?= $hayEntrada ? 'true' : 'false' ?>;
      btnS.disabled = <?= (!$hayEntrada || $haySalida) ? 'true' : 'false' ?>;
    }
  } catch(e) {
    showToast('Error de comunicación', 'error');
    btnE.disabled = <?= $hayEntrada ? 'true' : 'false' ?>;
    btnS.disabled = <?= (!$hayEntrada || $haySalida) ? 'true' : 'false' ?>;
  }
}

function showToast(msg, tipo = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + tipo + ' show';
  setTimeout(() => t.className = 'toast', 4000);
}
</script>
</body>
</html>
