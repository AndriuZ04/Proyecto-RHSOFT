<?php
require_once 'config.php';
requireAdmin();

$db = getDB();

// ── AJAX: operaciones CRUD ───────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion'])) {
    header('Content-Type: application/json');
    $accion = $_POST['accion'];

    // ── Guardar / actualizar persona + empleado ─────────────
    if ($accion === 'guardar_empleado') {
        try {
            $db->beginTransaction();

            $personaId = (int)($_POST['ID_Persona'] ?? 0);
            $empId     = (int)($_POST['ID_Empleado'] ?? 0);

            if ($personaId > 0) {
                $s = $db->prepare("UPDATE PERSONAS SET Numero_Documento=?,Nombres=?,Apellidos=?,Email=?,Telefono=?,Fecha_Nacimiento=? WHERE ID_Persona=?");
                $s->execute([
                    $_POST['Numero_Documento'], $_POST['Nombres'], $_POST['Apellidos'],
                    $_POST['Email'] ?: null, $_POST['Telefono'] ?: null,
                    $_POST['Fecha_Nacimiento'] ?: null, $personaId
                ]);
            } else {
                $s = $db->prepare("INSERT INTO PERSONAS (Numero_Documento,Nombres,Apellidos,Email,Telefono,Fecha_Nacimiento) VALUES (?,?,?,?,?,?)");
                $s->execute([
                    $_POST['Numero_Documento'], $_POST['Nombres'], $_POST['Apellidos'],
                    $_POST['Email'] ?: null, $_POST['Telefono'] ?: null,
                    $_POST['Fecha_Nacimiento'] ?: null
                ]);
                $personaId = (int)$db->lastInsertId();
            }

            // Validar PIN único
            $pinCheck = $db->prepare("SELECT ID_Empleado FROM EMPLEADOS WHERE PIN=? AND ID_Empleado != ?");
            $pinCheck->execute([$_POST['PIN'], $empId]);
            if ($pinCheck->fetch()) {
                $db->rollBack();
                echo json_encode(['ok'=>false,'msg'=>'El PIN ya está en uso por otro empleado.']);
                exit;
            }

            if ($empId > 0) {
                $s = $db->prepare("UPDATE EMPLEADOS SET ID_Cargo=?,PIN=?,Rol=?,Fecha_Ingreso=?,Fecha_Retiro=?,Estado_Empleado=? WHERE ID_Empleado=?");
                $s->execute([
                    $_POST['ID_Cargo'], $_POST['PIN'], $_POST['Rol'],
                    $_POST['Fecha_Ingreso'] ?: null, $_POST['Fecha_Retiro'] ?: null,
                    $_POST['Estado_Empleado'], $empId
                ]);
            } else {
                $s = $db->prepare("INSERT INTO EMPLEADOS (ID_Persona,ID_Cargo,PIN,Rol,Fecha_Ingreso,Estado_Empleado) VALUES (?,?,?,?,?,?)");
                $s->execute([
                    $personaId, $_POST['ID_Cargo'], $_POST['PIN'], $_POST['Rol'],
                    $_POST['Fecha_Ingreso'] ?: null, $_POST['Estado_Empleado']
                ]);
                $empId = (int)$db->lastInsertId();

                // R13: crear contrato automático al registrar nuevo empleado
                if (!empty($_POST['Tipo_Contrato']) && !empty($_POST['Fecha_Inicio_Contrato'])) {
                    $sc = $db->prepare("INSERT INTO CONTRATOS (ID_Empleado,ID_Cargo,Tipo_Contrato,Salario_Pactado,Fecha_Inicio,Fecha_Fin,Estado_Contrato) VALUES (?,?,?,?,?,?,?)");
                    $sc->execute([
                        $empId, $_POST['ID_Cargo'], $_POST['Tipo_Contrato'],
                        $_POST['Salario_Pactado'] ?: null,
                        $_POST['Fecha_Inicio_Contrato'],
                        $_POST['Fecha_Fin_Contrato'] ?: null,
                        'Vigente'
                    ]);
                }
            }

            $db->commit();
            echo json_encode(['ok'=>true,'msg'=>'Empleado guardado correctamente.']);
        } catch (PDOException $e) {
            $db->rollBack();
            $msg = strpos($e->getMessage(), 'UK_Numero_Documento') !== false
                ? 'El número de documento ya existe.'
                : 'Error: ' . $e->getMessage();
            echo json_encode(['ok'=>false,'msg'=>$msg]);
        }
        exit;
    }

    // ── R13: Guardar contrato ────────────────────────────────
    if ($accion === 'guardar_contrato') {
        try {
            $contratoId = (int)($_POST['ID_Contrato'] ?? 0);
            if ($contratoId > 0) {
                $s = $db->prepare("UPDATE CONTRATOS SET Tipo_Contrato=?,Salario_Pactado=?,Fecha_Inicio=?,Fecha_Fin=?,Estado_Contrato=? WHERE ID_Contrato=?");
                $s->execute([
                    $_POST['Tipo_Contrato'], $_POST['Salario_Pactado'] ?: null,
                    $_POST['Fecha_Inicio'], $_POST['Fecha_Fin'] ?: null,
                    $_POST['Estado_Contrato'], $contratoId
                ]);
            } else {
                $s = $db->prepare("INSERT INTO CONTRATOS (ID_Empleado,ID_Cargo,Tipo_Contrato,Salario_Pactado,Fecha_Inicio,Fecha_Fin,Estado_Contrato) VALUES (?,?,?,?,?,?,?)");
                $s->execute([
                    (int)$_POST['ID_Empleado'], (int)$_POST['ID_Cargo'],
                    $_POST['Tipo_Contrato'], $_POST['Salario_Pactado'] ?: null,
                    $_POST['Fecha_Inicio'], $_POST['Fecha_Fin'] ?: null,
                    $_POST['Estado_Contrato']
                ]);
            }
            echo json_encode(['ok'=>true,'msg'=>'Contrato guardado correctamente.']);
        } catch (PDOException $e) {
            echo json_encode(['ok'=>false,'msg'=>'Error: '.$e->getMessage()]);
        }
        exit;
    }

    // ── R14: Guardar accidente SST ───────────────────────────
    if ($accion === 'guardar_sst') {
        try {
            $sstId = (int)($_POST['ID_Accidente'] ?? 0);
            if ($sstId > 0) {
                $s = $db->prepare("UPDATE SST_ACCIDENTES SET ID_Empleado=?,Fecha_Accidente=?,Tipo_Accidente=?,Descripcion=?,Accion_Inmediata=?,Fecha_Reporte=? WHERE ID_Accidente=?");
                $s->execute([
                    (int)$_POST['ID_Empleado_SST'], $_POST['Fecha_Accidente'],
                    $_POST['Tipo_Accidente'], $_POST['Descripcion'],
                    $_POST['Accion_Inmediata'] ?: null, $_POST['Fecha_Reporte'] ?: null,
                    $sstId
                ]);
            } else {
                $s = $db->prepare("INSERT INTO SST_ACCIDENTES (ID_Empleado,Fecha_Accidente,Tipo_Accidente,Descripcion,Accion_Inmediata,Fecha_Reporte) VALUES (?,?,?,?,?,?)");
                $s->execute([
                    (int)$_POST['ID_Empleado_SST'], $_POST['Fecha_Accidente'],
                    $_POST['Tipo_Accidente'], $_POST['Descripcion'],
                    $_POST['Accion_Inmediata'] ?: null, $_POST['Fecha_Reporte'] ?: null
                ]);
            }
            echo json_encode(['ok'=>true,'msg'=>'Accidente SST registrado correctamente.']);
        } catch (PDOException $e) {
            echo json_encode(['ok'=>false,'msg'=>'Error: '.$e->getMessage()]);
        }
        exit;
    }

    // ── Obtener contratos de un empleado ─────────────────────
    if ($accion === 'get_contratos') {
        $s = $db->prepare("SELECT * FROM CONTRATOS WHERE ID_Empleado=? ORDER BY Fecha_Inicio DESC");
        $s->execute([(int)$_POST['ID_Empleado']]);
        echo json_encode($s->fetchAll());
        exit;
    }

    // ── Obtener accidentes SST de un empleado ────────────────
    if ($accion === 'get_sst') {
        $s = $db->prepare("SELECT * FROM SST_ACCIDENTES WHERE ID_Empleado=? ORDER BY Fecha_Accidente DESC");
        $s->execute([(int)$_POST['ID_Empleado']]);
        echo json_encode($s->fetchAll());
        exit;
    }

    // ── Cambiar estado ──────────────────────────────────────
    if ($accion === 'cambiar_estado') {
        $s = $db->prepare("UPDATE EMPLEADOS SET Estado_Empleado=? WHERE ID_Empleado=?");
        $s->execute([$_POST['estado'], (int)$_POST['ID_Empleado']]);
        echo json_encode(['ok'=>true]);
        exit;
    }

    // ── Obtener empleado para editar ────────────────────────
    if ($accion === 'get_empleado') {
        $s = $db->prepare("
            SELECT e.*, p.Nombres, p.Apellidos, p.Numero_Documento, p.Email, p.Telefono, p.Fecha_Nacimiento, p.ID_Persona
            FROM EMPLEADOS e JOIN PERSONAS p ON p.ID_Persona=e.ID_Persona
            WHERE e.ID_Empleado=?
        ");
        $s->execute([(int)$_POST['ID_Empleado']]);
        echo json_encode($s->fetch());
        exit;
    }

    // ── Obtener registros de un empleado ────────────────────
    if ($accion === 'get_registros') {
        $s = $db->prepare("SELECT * FROM REGISTROS WHERE ID_Empleado=? ORDER BY Fecha DESC, Hora_Entrada DESC LIMIT 50");
        $s->execute([(int)$_POST['ID_Empleado']]);
        echo json_encode($s->fetchAll());
        exit;
    }

    // ── R12: Dar de baja (soft delete) ──────────────────────
    if ($accion === 'eliminar_empleado') {
        $db->prepare("UPDATE EMPLEADOS SET Estado_Empleado='Inactivo',Fecha_Retiro=CURDATE() WHERE ID_Empleado=?")
           ->execute([(int)$_POST['ID_Empleado']]);
        // También cerrar contratos vigentes
        $db->prepare("UPDATE CONTRATOS SET Estado_Contrato='Terminado' WHERE ID_Empleado=? AND Estado_Contrato='Vigente'")
           ->execute([(int)$_POST['ID_Empleado']]);
        echo json_encode(['ok'=>true,'msg'=>'Empleado dado de baja y contratos cerrados correctamente.']);
        exit;
    }

    exit;
}

// ── Pestaña activa ───────────────────────────────────────────
$tab = $_GET['tab'] ?? 'empleados';

// ── Datos para empleados ─────────────────────────────────────
$busqueda    = trim($_GET['q'] ?? '');
$filtroEstado = $_GET['estado'] ?? '';

$where  = '1=1';
$params = [];
if ($busqueda) {
    $where .= " AND (p.Nombres LIKE ? OR p.Apellidos LIKE ? OR p.Numero_Documento LIKE ? OR c.Nombre_Cargo LIKE ?)";
    $like = "%$busqueda%";
    $params = array_merge($params, [$like,$like,$like,$like]);
}
if ($filtroEstado) {
    $where .= " AND e.Estado_Empleado = ?";
    $params[] = $filtroEstado;
}

$stmt = $db->prepare("
    SELECT e.ID_Empleado, e.PIN, e.Rol, e.Estado_Empleado, e.Fecha_Ingreso, e.Fecha_Retiro,
           p.ID_Persona, p.Nombres, p.Apellidos, p.Numero_Documento, p.Email, p.Telefono,
           c.ID_Cargo, c.Nombre_Cargo, c.Salario_Base,
           d.ID_Departamento, d.Nombre_Departamento,
           (SELECT COUNT(*) FROM CONTRATOS ct WHERE ct.ID_Empleado=e.ID_Empleado AND ct.Estado_Contrato='Vigente') AS contratos_vigentes
    FROM   EMPLEADOS     e
    JOIN   PERSONAS      p ON p.ID_Persona      = e.ID_Persona
    JOIN   CARGOS        c ON c.ID_Cargo        = e.ID_Cargo
    JOIN   DEPARTAMENTOS d ON d.ID_Departamento = c.ID_Departamento
    WHERE  $where
    ORDER  BY p.Apellidos, p.Nombres
");
$stmt->execute($params);
$empleados = $stmt->fetchAll();

$cargos        = $db->query("SELECT c.*, d.Nombre_Departamento FROM CARGOS c JOIN DEPARTAMENTOS d ON d.ID_Departamento=c.ID_Departamento ORDER BY d.Nombre_Departamento, c.Nombre_Cargo")->fetchAll();
$departamentos = $db->query("SELECT * FROM DEPARTAMENTOS ORDER BY Nombre_Departamento")->fetchAll();

// KPIs empleados
$kpis = $db->query("
    SELECT
        COUNT(*)                                                            AS total,
        SUM(Estado_Empleado='Activo')                                       AS activos,
        SUM(Estado_Empleado='Inactivo' OR Estado_Empleado='Retirado')       AS inactivos,
        SUM(Rol='admin')                                                    AS admins
    FROM EMPLEADOS
")->fetch();

// R13: KPIs contratos
$kpiContratos = $db->query("
    SELECT
        COUNT(*) AS total,
        SUM(Estado_Contrato='Vigente') AS vigentes,
        SUM(Estado_Contrato='Terminado') AS terminados,
        SUM(Estado_Contrato='Suspendido') AS suspendidos
    FROM CONTRATOS
")->fetch();

// Datos contratos con info de empleado
$contratos = $db->query("
    SELECT ct.*, p.Nombres, p.Apellidos, p.Numero_Documento, c.Nombre_Cargo, d.Nombre_Departamento
    FROM CONTRATOS ct
    JOIN EMPLEADOS e ON e.ID_Empleado = ct.ID_Empleado
    JOIN PERSONAS p ON p.ID_Persona = e.ID_Persona
    JOIN CARGOS c ON c.ID_Cargo = ct.ID_Cargo
    JOIN DEPARTAMENTOS d ON d.ID_Departamento = c.ID_Departamento
    ORDER BY ct.Fecha_Inicio DESC
")->fetchAll();

// R14: Datos SST
$kpiSST = $db->query("SELECT COUNT(*) AS total FROM SST_ACCIDENTES")->fetch();
$accidentes = $db->query("
    SELECT sa.*, p.Nombres, p.Apellidos, c.Nombre_Cargo
    FROM SST_ACCIDENTES sa
    JOIN EMPLEADOS e ON e.ID_Empleado = sa.ID_Empleado
    JOIN PERSONAS p ON p.ID_Persona = e.ID_Persona
    JOIN CARGOS c ON c.ID_Cargo = e.ID_Cargo
    ORDER BY sa.Fecha_Accidente DESC
")->fetchAll();

$nombre = $_SESSION['nombre'];
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Administración — Gestión Empresarial</title>
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
    --rojo        : #c0392b;
    --verde       : #27ae60;
    --naranja     : #e67e22;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'DM Sans', sans-serif; background: var(--fondo); color: var(--texto); min-height: 100vh; }

  /* ── Sidebar ── */
  .sidebar { position:fixed; top:0; left:0; bottom:0; width:260px; background:var(--azul-oscuro); padding:32px 24px; display:flex; flex-direction:column; z-index:100; }
  .sidebar-logo { display:flex; align-items:center; gap:12px; margin-bottom:40px; }
  .sidebar-logo .icon { width:40px; height:40px; background:rgba(255,255,255,.15); border-radius:10px; display:flex; align-items:center; justify-content:center; }
  .sidebar-logo .icon svg { width:20px; fill:white; }
  .sidebar-logo span { font-family:'DM Serif Display',serif; color:white; font-size:1.05rem; line-height:1.2; }
  .nav-section { font-size:.72rem; color:rgba(255,255,255,.4); letter-spacing:.1em; text-transform:uppercase; margin-bottom:10px; margin-top:24px; }
  .nav-item { display:flex; align-items:center; gap:12px; padding:11px 14px; border-radius:10px; color:rgba(255,255,255,.7); text-decoration:none; font-size:.92rem; transition:all .2s; margin-bottom:4px; }
  .nav-item svg { width:18px; fill:currentColor; flex-shrink:0; }
  .nav-item:hover { background:rgba(255,255,255,.1); color:white; }
  .nav-item.active { background:rgba(255,255,255,.18); color:white; font-weight:600; }
  .admin-badge { background:var(--azul-claro); color:var(--texto); font-size:.65rem; font-weight:700; padding:2px 7px; border-radius:6px; margin-left:auto; letter-spacing:.04em; text-transform:uppercase; }
  .sidebar-footer { margin-top:auto; padding-top:20px; border-top:1px solid rgba(255,255,255,.1); }
  .user-chip { display:flex; align-items:center; gap:10px; padding:10px 14px; background:rgba(255,255,255,.1); border-radius:12px; margin-bottom:10px; }
  .user-avatar { width:36px; height:36px; background:var(--azul-medio); border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; color:white; font-size:.9rem; flex-shrink:0; }
  .user-info span { display:block; }
  .user-info .uname { color:white; font-size:.88rem; font-weight:500; }
  .user-info .urole { color:rgba(255,255,255,.5); font-size:.75rem; text-transform:capitalize; }
  .logout-btn { display:flex; align-items:center; gap:8px; width:100%; padding:10px 14px; background:none; border:1.5px solid rgba(255,255,255,.15); border-radius:10px; color:rgba(255,255,255,.6); font-family:'DM Sans',sans-serif; font-size:.88rem; cursor:pointer; transition:all .2s; }
  .logout-btn svg { width:16px; fill:currentColor; }
  .logout-btn:hover { border-color:rgba(255,255,255,.4); color:white; }

  /* ── Main ── */
  .main { margin-left:260px; padding:36px 40px; }
  .page-header { display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:28px; flex-wrap:wrap; gap:16px; }
  .page-header h1 { font-family:'DM Serif Display',serif; font-size:2rem; color:var(--texto); margin-bottom:4px; }
  .page-header p { color:var(--azul-oscuro); opacity:.6; font-size:.92rem; }

  .btn-primary { display:inline-flex; align-items:center; gap:8px; padding:12px 22px; background:var(--azul-oscuro); color:white; border:none; border-radius:12px; font-family:'DM Sans',sans-serif; font-size:.9rem; font-weight:600; cursor:pointer; transition:all .2s; text-decoration:none; }
  .btn-primary svg { width:18px; fill:white; }
  .btn-primary:hover { background:#2a4860; transform:translateY(-1px); }

  /* ── Tabs ── */
  .tabs { display:flex; gap:4px; margin-bottom:28px; background:white; padding:6px; border-radius:14px; box-shadow:var(--sombra); width:fit-content; }
  .tab-btn { padding:10px 22px; border:none; background:none; border-radius:10px; font-family:'DM Sans',sans-serif; font-size:.9rem; font-weight:500; color:var(--azul-oscuro); cursor:pointer; transition:all .2s; display:flex; align-items:center; gap:8px; opacity:.6; }
  .tab-btn svg { width:16px; fill:currentColor; }
  .tab-btn.active { background:var(--azul-oscuro); color:white; font-weight:600; opacity:1; }
  .tab-btn:hover:not(.active) { opacity:1; background:rgba(53,88,114,.08); }
  .tab-panel { display:none; }
  .tab-panel.active { display:block; }

  /* ── KPI cards ── */
  .kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }
  .kpi-card { background:white; border-radius:16px; padding:20px 24px; box-shadow:var(--sombra); }
  .kpi-card .kpi-label { font-size:.75rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--azul-oscuro); opacity:.5; margin-bottom:6px; }
  .kpi-card .kpi-value { font-family:'DM Serif Display',serif; font-size:2.2rem; color:var(--texto); line-height:1; }
  .kpi-card .kpi-sub { font-size:.8rem; color:var(--azul-oscuro); opacity:.45; margin-top:3px; }
  .kpi-card.highlight { background:var(--azul-oscuro); }
  .kpi-card.highlight .kpi-label { color:rgba(255,255,255,.6); opacity:1; }
  .kpi-card.highlight .kpi-value { color:white; }
  .kpi-card.highlight .kpi-sub   { color:rgba(255,255,255,.5); opacity:1; }

  /* ── Barra de herramientas ── */
  .toolbar { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
  .search-box { flex:1; min-width:220px; position:relative; }
  .search-box svg { position:absolute; left:14px; top:50%; transform:translateY(-50%); width:18px; fill:var(--azul-oscuro); opacity:.4; }
  .search-box input { width:100%; padding:11px 14px 11px 42px; border:2px solid rgba(53,88,114,.15); border-radius:12px; background:white; font-family:'DM Sans',sans-serif; font-size:.92rem; color:var(--texto); outline:none; transition:border-color .2s; }
  .search-box input:focus { border-color:var(--azul-medio); }
  .filter-select { padding:11px 16px; border:2px solid rgba(53,88,114,.15); border-radius:12px; background:white; font-family:'DM Sans',sans-serif; font-size:.9rem; color:var(--texto); outline:none; cursor:pointer; }
  .filter-select:focus { border-color:var(--azul-medio); }

  /* ── Tabla ── */
  .table-wrap { background:white; border-radius:16px; box-shadow:var(--sombra); overflow:hidden; }
  table { width:100%; border-collapse:collapse; }
  thead th { padding:14px 18px; text-align:left; font-size:.73rem; font-weight:600; letter-spacing:.07em; text-transform:uppercase; color:var(--azul-oscuro); opacity:.5; background:rgba(53,88,114,.04); border-bottom:1px solid rgba(53,88,114,.08); white-space:nowrap; }
  tbody td { padding:14px 18px; font-size:.88rem; color:var(--texto); border-bottom:1px solid rgba(53,88,114,.06); vertical-align:middle; }
  tbody tr:last-child td { border-bottom:none; }
  tbody tr:hover { background:rgba(53,88,114,.03); }
  .emp-name { font-weight:600; }
  .emp-doc  { font-size:.78rem; color:var(--azul-oscuro); opacity:.55; }

  /* ── Badges ── */
  .badge { display:inline-block; padding:3px 10px; border-radius:6px; font-size:.73rem; font-weight:600; }
  .badge-activo     { background:rgba(39,174,96,.12);   color:#1a6344; }
  .badge-inactivo   { background:rgba(192,57,43,.1);    color:#7d1e13; }
  .badge-licencia   { background:rgba(243,156,18,.12);  color:#7d5a00; }
  .badge-suspension { background:rgba(155,89,182,.12);  color:#5b2d8e; }
  .badge-retirado   { background:rgba(127,140,141,.12); color:#4a5254; }
  .badge-admin      { background:rgba(53,88,114,.15);   color:var(--azul-oscuro); }
  .badge-vigente    { background:rgba(39,174,96,.12);   color:#1a6344; }
  .badge-terminado  { background:rgba(127,140,141,.12); color:#4a5254; }
  .badge-suspendido { background:rgba(155,89,182,.12);  color:#5b2d8e; }
  .badge-nocontrato { background:rgba(192,57,43,.1);    color:#7d1e13; }
  .badge-tipo-sst   { background:rgba(230,126,34,.12);  color:#7d4a00; }

  .pin-code { font-family:monospace; font-size:.85rem; background:rgba(53,88,114,.08); padding:2px 8px; border-radius:6px; color:var(--azul-oscuro); letter-spacing:.1em; }
  .contrato-indicator { display:inline-flex; align-items:center; gap:4px; font-size:.78rem; }
  .contrato-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }

  .actions-cell { display:flex; gap:8px; }
  .icon-btn { width:34px; height:34px; border:none; border-radius:8px; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .15s; }
  .icon-btn svg { width:16px; }
  .icon-btn.edit   { background:rgba(122,170,206,.15); color:var(--azul-oscuro); }
  .icon-btn.edit:hover   { background:var(--azul-medio); color:white; }
  .icon-btn.view   { background:rgba(39,174,96,.1);   color:#1a6344; }
  .icon-btn.view:hover   { background:#27ae60; color:white; }
  .icon-btn.contrato { background:rgba(53,88,114,.1); color:var(--azul-oscuro); }
  .icon-btn.contrato:hover { background:var(--azul-oscuro); color:white; }
  .icon-btn.sst    { background:rgba(230,126,34,.1); color:#7d4a00; }
  .icon-btn.sst:hover    { background:var(--naranja); color:white; }
  .icon-btn.danger { background:rgba(192,57,43,.1); color:var(--rojo); }
  .icon-btn.danger:hover { background:var(--rojo); color:white; }

  /* ── Modal ── */
  .modal-overlay { position:fixed; inset:0; background:rgba(30,51,68,.55); backdrop-filter:blur(4px); z-index:200; display:none; align-items:center; justify-content:center; padding:20px; }
  .modal-overlay.open { display:flex; }
  .modal { background:var(--blanco-roto); border-radius:20px; width:min(700px,100%); max-height:90vh; overflow-y:auto; animation:slideUp .35s cubic-bezier(.22,1,.36,1); }
  @keyframes slideUp { from { opacity:0; transform:translateY(30px); } to { opacity:1; transform:translateY(0); } }
  .modal-header { padding:28px 32px 0; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; background:var(--blanco-roto); border-radius:20px 20px 0 0; padding-bottom:20px; border-bottom:1px solid rgba(53,88,114,.1); }
  .modal-header h2 { font-family:'DM Serif Display',serif; font-size:1.4rem; color:var(--texto); }
  .modal-close { width:36px; height:36px; border:none; background:rgba(53,88,114,.1); border-radius:8px; cursor:pointer; display:flex; align-items:center; justify-content:center; color:var(--texto); font-size:1.1rem; transition:background .2s; }
  .modal-close:hover { background:rgba(53,88,114,.2); }
  .modal-body { padding:24px 32px 32px; }

  .form-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  .form-grid .full { grid-column:1/-1; }
  .form-section-title { font-size:.75rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--azul-oscuro); opacity:.5; margin:20px 0 12px; padding-bottom:6px; border-bottom:1px solid rgba(53,88,114,.1); }
  .form-section-icon { display:flex; align-items:center; gap:8px; }
  .form-section-icon svg { width:14px; fill:var(--azul-oscuro); opacity:.5; }

  .field label { display:block; font-size:.78rem; font-weight:600; letter-spacing:.05em; text-transform:uppercase; color:var(--azul-oscuro); margin-bottom:8px; }
  .field input, .field select, .field textarea { width:100%; padding:11px 14px; border:2px solid rgba(53,88,114,.18); border-radius:10px; background:white; font-family:'DM Sans',sans-serif; font-size:.9rem; color:var(--texto); outline:none; transition:border-color .2s; }
  .field input:focus, .field select:focus, .field textarea:focus { border-color:var(--azul-medio); box-shadow:0 0 0 3px rgba(122,170,206,.15); }
  .field textarea { resize:vertical; min-height:80px; }

  .modal-footer { display:flex; gap:12px; justify-content:flex-end; padding-top:20px; border-top:1px solid rgba(53,88,114,.1); margin-top:8px; }
  .btn-secondary { padding:11px 22px; border:2px solid rgba(53,88,114,.2); border-radius:10px; background:transparent; font-family:'DM Sans',sans-serif; font-size:.9rem; font-weight:600; color:var(--azul-oscuro); cursor:pointer; transition:all .2s; }
  .btn-secondary:hover { border-color:var(--azul-oscuro); }
  .btn-save { padding:11px 28px; background:var(--azul-oscuro); color:white; border:none; border-radius:10px; font-family:'DM Sans',sans-serif; font-size:.9rem; font-weight:600; cursor:pointer; transition:all .2s; display:flex; align-items:center; gap:8px; }
  .btn-save:hover { background:#2a4860; transform:translateY(-1px); }
  .btn-danger-full { padding:11px 22px; background:var(--rojo); color:white; border:none; border-radius:10px; font-family:'DM Sans',sans-serif; font-size:.9rem; font-weight:600; cursor:pointer; transition:all .2s; }
  .btn-danger-full:hover { opacity:.85; }

  /* Historial/contratos tabla en modal */
  .hist-table { width:100%; border-collapse:collapse; }
  .hist-table th { padding:10px 14px; text-align:left; font-size:.72rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--azul-oscuro); opacity:.5; border-bottom:1px solid rgba(53,88,114,.1); }
  .hist-table td { padding:10px 14px; font-size:.85rem; border-bottom:1px solid rgba(53,88,114,.06); }
  .hist-table tr:last-child td { border-bottom:none; }

  /* Alerta R13 */
  .alert-r13 { background:rgba(192,57,43,.07); border:1.5px solid rgba(192,57,43,.2); border-radius:10px; padding:10px 14px; font-size:.84rem; color:#7d1e13; display:flex; align-items:center; gap:8px; margin-bottom:16px; }
  .alert-r13 svg { width:16px; fill:currentColor; flex-shrink:0; }

  /* Toast */
  .toast { position:fixed; bottom:32px; right:32px; background:var(--texto); color:white; padding:14px 20px; border-radius:14px; font-size:.92rem; font-weight:500; box-shadow:0 8px 32px rgba(0,0,0,.2); transform:translateY(80px); opacity:0; transition:all .35s cubic-bezier(.22,1,.36,1); z-index:999; max-width:320px; }
  .toast.show { transform:translateY(0); opacity:1; }
  .toast.success { background:#1a6344; }
  .toast.error   { background:var(--rojo); }

  .empty-state { text-align:center; padding:48px; color:var(--azul-oscuro); opacity:.4; }

  @media(max-width:900px){
    .sidebar{width:220px;} .main{margin-left:220px;padding:24px 20px;}
    .kpi-grid{grid-template-columns:repeat(2,1fr);}
    .form-grid{grid-template-columns:1fr;}
  }
  @media(max-width:640px){
    .sidebar{display:none;} .main{margin-left:0;padding:20px 16px;}
    .kpi-grid{grid-template-columns:1fr 1fr;}
  }
</style>
</head>
<body>

<!-- ── Sidebar ── -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="icon"><svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg></div>
    <span>Gestión<br>Empresarial</span>
  </div>

  <div class="nav-section">Módulos</div>
  <a href="registro.php" class="nav-item">
    <svg viewBox="0 0 24 24"><path d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>
    Registro de asistencia
  </a>
  <a href="admin.php" class="nav-item active">
    <svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
    Gestión de empleados
    <span class="admin-badge">Admin</span>
  </a>

  <div class="sidebar-footer">
    <div class="user-chip">
      <div class="user-avatar"><?= strtoupper(substr($nombre,0,2)) ?></div>
      <div class="user-info">
        <span class="uname"><?= htmlspecialchars($nombre) ?></span>
        <span class="urole">Administrador</span>
      </div>
    </div>
    <button class="logout-btn" onclick="location.href='index.php?logout=1'">
      <svg viewBox="0 0 24 24"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
      Cerrar sesión
    </button>
  </div>
</aside>

<!-- ── Main ── -->
<main class="main">
  <div class="page-header">
    <div>
      <h1>Gestión de Empleados</h1>
      <p>Administra el personal, contratos, SST y registros del sistema</p>
    </div>
  </div>

  <!-- ── Tabs ── -->
  <div class="tabs">
    <button class="tab-btn <?= $tab==='empleados'?'active':'' ?>" onclick="switchTab('empleados')">
      <svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
      Empleados
    </button>
    <button class="tab-btn <?= $tab==='contratos'?'active':'' ?>" onclick="switchTab('contratos')">
      <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 15h8v2H8zm0-4h8v2H8zm0-4h5v2H8z"/></svg>
      Contratos <span style="background:rgba(122,170,206,.25);color:var(--azul-oscuro);font-size:.7rem;padding:1px 7px;border-radius:5px;margin-left:4px;font-weight:700;"><?= $kpiContratos['vigentes'] ?> vigentes</span>
    </button>
    <button class="tab-btn <?= $tab==='sst'?'active':'' ?>" onclick="switchTab('sst')">
      <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
      SST / Accidentes <span style="background:rgba(230,126,34,.15);color:#7d4a00;font-size:.7rem;padding:1px 7px;border-radius:5px;margin-left:4px;font-weight:700;"><?= $kpiSST['total'] ?></span>
    </button>
  </div>

  <!-- ════════════════════════════════ TAB: EMPLEADOS ════════════════════════════════ -->
  <div class="tab-panel <?= $tab==='empleados'?'active':'' ?>" id="tab-empleados">

    <div style="display:flex;justify-content:flex-end;margin-bottom:20px;">
      <button class="btn-primary" onclick="abrirModal()">
        <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        Nuevo empleado
      </button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card highlight">
        <div class="kpi-label">Total empleados</div>
        <div class="kpi-value"><?= $kpis['total'] ?></div>
        <div class="kpi-sub">Registrados en el sistema</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Activos</div>
        <div class="kpi-value" style="color:#1a6344"><?= $kpis['activos'] ?></div>
        <div class="kpi-sub">En servicio</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Inactivos / Retirados</div>
        <div class="kpi-value" style="color:var(--rojo)"><?= $kpis['inactivos'] ?></div>
        <div class="kpi-sub">Sin acceso activo</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Administradores</div>
        <div class="kpi-value"><?= $kpis['admins'] ?></div>
        <div class="kpi-sub">Con acceso total</div>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-box">
        <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
        <input type="text" id="searchInput" placeholder="Buscar empleado, cargo..." value="<?= htmlspecialchars($busqueda) ?>" oninput="buscar()">
      </div>
      <select class="filter-select" id="filtroEstado" onchange="buscar()">
        <option value="">Todos los estados</option>
        <option value="Activo"     <?= $filtroEstado==='Activo'     ?'selected':''?>>Activo</option>
        <option value="Inactivo"   <?= $filtroEstado==='Inactivo'   ?'selected':''?>>Inactivo</option>
        <option value="Retirado"   <?= $filtroEstado==='Retirado'   ?'selected':''?>>Retirado</option>
        <option value="Licencia"   <?= $filtroEstado==='Licencia'   ?'selected':''?>>Licencia</option>
        <option value="Suspensión" <?= $filtroEstado==='Suspensión' ?'selected':''?>>Suspensión</option>
      </select>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Empleado</th>
            <th>Departamento</th>
            <th>Cargo</th>
            <th>PIN</th>
            <th>Ingreso</th>
            <th>Estado</th>
            <th>Contrato</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <?php if (empty($empleados)): ?>
          <tr><td colspan="9"><div class="empty-state">No se encontraron empleados</div></td></tr>
          <?php else: foreach ($empleados as $e): ?>
          <tr>
            <td>
              <div class="emp-name"><?= htmlspecialchars($e['Apellidos'] . ', ' . $e['Nombres']) ?></div>
              <div class="emp-doc">Doc: <?= htmlspecialchars($e['Numero_Documento']) ?></div>
            </td>
            <td><?= htmlspecialchars($e['Nombre_Departamento']) ?></td>
            <td><?= htmlspecialchars($e['Nombre_Cargo']) ?></td>
            <td><span class="pin-code"><?= htmlspecialchars($e['PIN']) ?></span></td>
            <td><?= $e['Fecha_Ingreso'] ? date('d/m/Y', strtotime($e['Fecha_Ingreso'])) : '—' ?></td>
            <td>
              <?php
                $badgeClass = match($e['Estado_Empleado']) {
                  'Activo'     => 'badge-activo',
                  'Inactivo'   => 'badge-inactivo',
                  'Licencia'   => 'badge-licencia',
                  'Suspensión' => 'badge-suspension',
                  'Retirado'   => 'badge-retirado',
                  default      => 'badge-inactivo'
                };
              ?>
              <span class="badge <?= $badgeClass ?>"><?= htmlspecialchars($e['Estado_Empleado']) ?></span>
            </td>
            <!-- R13: indicador visual de contrato vigente -->
            <td>
              <?php if ($e['contratos_vigentes'] > 0): ?>
                <span class="badge badge-vigente">✓ Vigente</span>
              <?php elseif ($e['Estado_Empleado'] === 'Activo'): ?>
                <span class="badge badge-nocontrato" title="Empleado activo sin contrato vigente">⚠ Sin contrato</span>
              <?php else: ?>
                <span style="color:var(--azul-oscuro);opacity:.35;font-size:.8rem;">—</span>
              <?php endif; ?>
            </td>
            <td><?php if($e['Rol']==='admin'): ?><span class="badge badge-admin">Admin</span><?php else: ?>Empleado<?php endif; ?></td>
            <td>
              <div class="actions-cell">
                <button class="icon-btn edit" title="Editar empleado" onclick="editarEmpleado(<?= $e['ID_Empleado'] ?>)">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                </button>
                <button class="icon-btn view" title="Ver asistencia" onclick="verRegistros(<?= $e['ID_Empleado'] ?>, '<?= htmlspecialchars(addslashes($e['Nombres'].' '.$e['Apellidos'])) ?>')">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                </button>
                <button class="icon-btn contrato" title="Ver / Añadir contratos" onclick="verContratos(<?= $e['ID_Empleado'] ?>, <?= $e['ID_Cargo'] ?>, '<?= htmlspecialchars(addslashes($e['Nombres'].' '.$e['Apellidos'])) ?>')">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 15h8v2H8zm0-4h8v2H8zm0-4h5v2H8z"/></svg>
                </button>
                <button class="icon-btn sst" title="Registrar accidente SST" onclick="abrirSST(<?= $e['ID_Empleado'] ?>, '<?= htmlspecialchars(addslashes($e['Nombres'].' '.$e['Apellidos'])) ?>')">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
                </button>
                <button class="icon-btn danger" title="Dar de baja" onclick="darDeBaja(<?= $e['ID_Empleado'] ?>, '<?= htmlspecialchars(addslashes($e['Nombres'])) ?>')">
                  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
              </div>
            </td>
          </tr>
          <?php endforeach; endif; ?>
        </tbody>
      </table>
    </div>
  </div><!-- /tab-empleados -->

  <!-- ════════════════════════════════ TAB: CONTRATOS (R13) ════════════════════════════════ -->
  <div class="tab-panel <?= $tab==='contratos'?'active':'' ?>" id="tab-contratos">

    <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);">
      <div class="kpi-card highlight">
        <div class="kpi-label">Total contratos</div>
        <div class="kpi-value"><?= $kpiContratos['total'] ?></div>
        <div class="kpi-sub">Registrados</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Vigentes</div>
        <div class="kpi-value" style="color:#1a6344"><?= $kpiContratos['vigentes'] ?></div>
        <div class="kpi-sub">En curso</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Terminados</div>
        <div class="kpi-value" style="color:var(--azul-oscuro)"><?= $kpiContratos['terminados'] ?></div>
        <div class="kpi-sub">Finalizados</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Suspendidos</div>
        <div class="kpi-value" style="color:var(--naranja)"><?= $kpiContratos['suspendidos'] ?></div>
        <div class="kpi-sub">En pausa</div>
      </div>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Empleado</th>
            <th>Cargo / Depto.</th>
            <th>Tipo contrato</th>
            <th>Salario pactado</th>
            <th>Inicio</th>
            <th>Fin</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <?php if (empty($contratos)): ?>
          <tr><td colspan="7"><div class="empty-state">No hay contratos registrados</div></td></tr>
          <?php else: foreach ($contratos as $ct): ?>
          <tr>
            <td>
              <div class="emp-name"><?= htmlspecialchars($ct['Apellidos'] . ', ' . $ct['Nombres']) ?></div>
              <div class="emp-doc">Doc: <?= htmlspecialchars($ct['Numero_Documento']) ?></div>
            </td>
            <td>
              <div><?= htmlspecialchars($ct['Nombre_Cargo']) ?></div>
              <div class="emp-doc"><?= htmlspecialchars($ct['Nombre_Departamento']) ?></div>
            </td>
            <td><?= htmlspecialchars($ct['Tipo_Contrato'] ?? '—') ?></td>
            <td><?= $ct['Salario_Pactado'] ? '$ ' . number_format($ct['Salario_Pactado'],0,',','.') : '—' ?></td>
            <td><?= $ct['Fecha_Inicio'] ? date('d/m/Y', strtotime($ct['Fecha_Inicio'])) : '—' ?></td>
            <td><?= $ct['Fecha_Fin'] ? date('d/m/Y', strtotime($ct['Fecha_Fin'])) : '<span style="opacity:.4">Indefinido</span>' ?></td>
            <td>
              <?php $bc = match($ct['Estado_Contrato'] ?? '') {
                'Vigente'    => 'badge-vigente',
                'Terminado'  => 'badge-terminado',
                'Suspendido' => 'badge-suspendido',
                default      => 'badge-inactivo'
              }; ?>
              <span class="badge <?= $bc ?>"><?= htmlspecialchars($ct['Estado_Contrato'] ?? '—') ?></span>
            </td>
          </tr>
          <?php endforeach; endif; ?>
        </tbody>
      </table>
    </div>
  </div><!-- /tab-contratos -->

  <!-- ════════════════════════════════ TAB: SST (R14) ════════════════════════════════ -->
  <div class="tab-panel <?= $tab==='sst'?'active':'' ?>" id="tab-sst">

    <div style="display:flex;justify-content:flex-end;margin-bottom:20px;">
      <button class="btn-primary" style="background:var(--naranja);" onclick="abrirSSTNuevo()">
        <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        Nuevo reporte SST
      </button>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Empleado</th>
            <th>Cargo</th>
            <th>Fecha accidente</th>
            <th>Tipo</th>
            <th>Descripción</th>
            <th>Acción inmediata</th>
            <th>Fecha reporte</th>
          </tr>
        </thead>
        <tbody>
          <?php if (empty($accidentes)): ?>
          <tr><td colspan="7"><div class="empty-state">No hay accidentes registrados</div></td></tr>
          <?php else: foreach ($accidentes as $ac): ?>
          <tr>
            <td>
              <div class="emp-name"><?= htmlspecialchars($ac['Apellidos'] . ', ' . $ac['Nombres']) ?></div>
            </td>
            <td><?= htmlspecialchars($ac['Nombre_Cargo']) ?></td>
            <td><?= $ac['Fecha_Accidente'] ? date('d/m/Y', strtotime($ac['Fecha_Accidente'])) : '—' ?></td>
            <td><span class="badge badge-tipo-sst"><?= htmlspecialchars($ac['Tipo_Accidente'] ?? '—') ?></span></td>
            <td style="max-width:200px;white-space:normal;font-size:.82rem;"><?= htmlspecialchars($ac['Descripcion'] ?? '—') ?></td>
            <td style="max-width:160px;white-space:normal;font-size:.82rem;"><?= htmlspecialchars($ac['Accion_Inmediata'] ?? '—') ?></td>
            <td><?= $ac['Fecha_Reporte'] ? date('d/m/Y', strtotime($ac['Fecha_Reporte'])) : '—' ?></td>
          </tr>
          <?php endforeach; endif; ?>
        </tbody>
      </table>
    </div>
  </div><!-- /tab-sst -->

</main><!-- /main -->

<!-- ══════════════════════ MODAL: Empleado ══════════════════════ -->
<div class="modal-overlay" id="modalEmp">
  <div class="modal">
    <div class="modal-header">
      <h2 id="modalTitle">Nuevo Empleado</h2>
      <button class="modal-close" onclick="cerrarModal('modalEmp')">✕</button>
    </div>
    <div class="modal-body">
      <form id="formEmp">
        <input type="hidden" name="accion" value="guardar_empleado">
        <input type="hidden" name="ID_Persona"  id="f_ID_Persona"  value="0">
        <input type="hidden" name="ID_Empleado" id="f_ID_Empleado" value="0">

        <div class="form-section-title">Datos personales</div>
        <div class="form-grid">
          <div class="field">
            <label>Número de documento *</label>
            <input type="text" name="Numero_Documento" id="f_doc" required>
          </div>
          <div class="field">
            <label>Fecha de nacimiento</label>
            <input type="date" name="Fecha_Nacimiento" id="f_fnac">
          </div>
          <div class="field">
            <label>Nombres *</label>
            <input type="text" name="Nombres" id="f_nombres" required>
          </div>
          <div class="field">
            <label>Apellidos *</label>
            <input type="text" name="Apellidos" id="f_apellidos" required>
          </div>
          <div class="field">
            <label>Correo electrónico</label>
            <input type="email" name="Email" id="f_email">
          </div>
          <div class="field">
            <label>Teléfono</label>
            <input type="tel" name="Telefono" id="f_tel">
          </div>
        </div>

        <div class="form-section-title">Datos laborales</div>
        <div class="form-grid">
          <div class="field">
            <label>Cargo *</label>
            <select name="ID_Cargo" id="f_cargo" required>
              <option value="">— Seleccionar —</option>
              <?php foreach ($cargos as $c): ?>
              <option value="<?= $c['ID_Cargo'] ?>">[<?= htmlspecialchars($c['Nombre_Departamento']) ?>] <?= htmlspecialchars($c['Nombre_Cargo']) ?></option>
              <?php endforeach; ?>
            </select>
          </div>
          <div class="field">
            <label>Fecha de ingreso</label>
            <input type="date" name="Fecha_Ingreso" id="f_fingreso">
          </div>
          <div class="field">
            <label>Estado</label>
            <select name="Estado_Empleado" id="f_estado">
              <option>Activo</option>
              <option>Inactivo</option>
              <option>Licencia</option>
              <option>Suspensión</option>
              <option>Retirado</option>
            </select>
          </div>
          <div class="field">
            <label>Fecha de retiro</label>
            <input type="date" name="Fecha_Retiro" id="f_fretiro">
          </div>
          <div class="field">
            <label>PIN de acceso (6 dígitos) *</label>
            <input type="text" name="PIN" id="f_pin" maxlength="6" pattern="\d{6}" required placeholder="000000">
          </div>
          <div class="field">
            <label>Rol</label>
            <select name="Rol" id="f_rol">
              <option value="empleado">Empleado</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
        </div>

        <!-- R13: contrato obligatorio para nuevo empleado -->
        <div id="seccionContrato" class="form-section-title">Contrato inicial</div>
        <div id="camposContrato" class="form-grid">
          <div class="field">
            <label>Tipo de contrato *</label>
            <select name="Tipo_Contrato" id="f_tipo_contrato">
              <option value="">— Sin contrato inicial —</option>
              <option>Indefinido</option>
              <option>Temporal</option>
              <option>Prácticas</option>
              <option>Prestación de servicios</option>
            </select>
          </div>
          <div class="field">
            <label>Salario pactado</label>
            <input type="number" name="Salario_Pactado" id="f_salario_pactado" placeholder="0">
          </div>
          <div class="field">
            <label>Fecha inicio contrato</label>
            <input type="date" name="Fecha_Inicio_Contrato" id="f_inicio_contrato">
          </div>
          <div class="field">
            <label>Fecha fin (vacío = indefinido)</label>
            <input type="date" name="Fecha_Fin_Contrato" id="f_fin_contrato">
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-secondary" onclick="cerrarModal('modalEmp')">Cancelar</button>
          <button type="submit" class="btn-save">
            <svg width="16" viewBox="0 0 24 24" fill="white"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>
            Guardar empleado
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- ══════════════════════ MODAL: Historial asistencia ══════════════════════ -->
<div class="modal-overlay" id="modalHist">
  <div class="modal">
    <div class="modal-header">
      <h2 id="histTitle">Registros de asistencia</h2>
      <button class="modal-close" onclick="cerrarModal('modalHist')">✕</button>
    </div>
    <div class="modal-body">
      <div id="histContent">Cargando...</div>
    </div>
  </div>
</div>

<!-- ══════════════════════ MODAL: Contratos (R13) ══════════════════════ -->
<div class="modal-overlay" id="modalContratos">
  <div class="modal">
    <div class="modal-header">
      <h2 id="contratosTitle">Contratos</h2>
      <button class="modal-close" onclick="cerrarModal('modalContratos')">✕</button>
    </div>
    <div class="modal-body">
      <div id="contratosListado" style="margin-bottom:24px;"></div>

      <div class="form-section-title">Añadir nuevo contrato</div>
      <form id="formContrato">
        <input type="hidden" name="accion" value="guardar_contrato">
        <input type="hidden" name="ID_Contrato" value="0">
        <input type="hidden" name="ID_Empleado" id="fc_emp">
        <input type="hidden" name="ID_Cargo"    id="fc_cargo">
        <div class="form-grid">
          <div class="field">
            <label>Tipo de contrato *</label>
            <select name="Tipo_Contrato" required>
              <option>Indefinido</option>
              <option>Temporal</option>
              <option>Prácticas</option>
              <option>Prestación de servicios</option>
            </select>
          </div>
          <div class="field">
            <label>Salario pactado</label>
            <input type="number" name="Salario_Pactado" placeholder="0">
          </div>
          <div class="field">
            <label>Fecha inicio *</label>
            <input type="date" name="Fecha_Inicio" required>
          </div>
          <div class="field">
            <label>Fecha fin (vacío = indefinido)</label>
            <input type="date" name="Fecha_Fin">
          </div>
          <div class="field full">
            <label>Estado</label>
            <select name="Estado_Contrato">
              <option>Vigente</option>
              <option>Suspendido</option>
              <option>Terminado</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-secondary" onclick="cerrarModal('modalContratos')">Cerrar</button>
          <button type="submit" class="btn-save">
            <svg width="16" viewBox="0 0 24 24" fill="white"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>
            Guardar contrato
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- ══════════════════════ MODAL: SST (R14) ══════════════════════ -->
<div class="modal-overlay" id="modalSST">
  <div class="modal">
    <div class="modal-header">
      <h2 id="sstTitle">Registrar Accidente SST</h2>
      <button class="modal-close" onclick="cerrarModal('modalSST')">✕</button>
    </div>
    <div class="modal-body">
      <form id="formSST">
        <input type="hidden" name="accion" value="guardar_sst">
        <input type="hidden" name="ID_Accidente" value="0">
        <input type="hidden" name="ID_Empleado_SST" id="fsst_emp">
        <div class="form-grid">
          <?php if (!isset($_GET['emp'])): ?>
          <div class="field full">
            <label>Empleado *</label>
            <select name="ID_Empleado_SST" id="fsst_emp_select">
              <option value="">— Seleccionar —</option>
              <?php foreach($empleados as $e): ?>
              <option value="<?= $e['ID_Empleado'] ?>"><?= htmlspecialchars($e['Apellidos'].', '.$e['Nombres']) ?></option>
              <?php endforeach; ?>
            </select>
          </div>
          <?php endif; ?>
          <div class="field">
            <label>Fecha del accidente *</label>
            <input type="date" name="Fecha_Accidente" required>
          </div>
          <div class="field">
            <label>Fecha de reporte</label>
            <input type="date" name="Fecha_Reporte">
          </div>
          <div class="field">
            <label>Tipo de accidente *</label>
            <select name="Tipo_Accidente" required>
              <option value="">— Seleccionar —</option>
              <option>Caída</option>
              <option>Corte</option>
              <option>Golpe</option>
              <option>Quemadura</option>
              <option>Intoxicación</option>
              <option>Atrapamiento</option>
              <option>Eléctrico</option>
              <option>Otro</option>
            </select>
          </div>
          <div class="field full">
            <label>Descripción del incidente *</label>
            <textarea name="Descripcion" required placeholder="Descripción detallada de lo ocurrido..."></textarea>
          </div>
          <div class="field full">
            <label>Acción inmediata tomada</label>
            <textarea name="Accion_Inmediata" placeholder="Ej: Primeros auxilios, traslado a médico..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-secondary" onclick="cerrarModal('modalSST')">Cancelar</button>
          <button type="submit" class="btn-save" style="background:var(--naranja);">
            <svg width="16" viewBox="0 0 24 24" fill="white"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
            Registrar accidente
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
// ── Tabs ──────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(b => {
    if (b.getAttribute('onclick') === `switchTab('${name}')`) b.classList.add('active');
  });
}

// ── Búsqueda ──────────────────────────────────────────────────
let searchTimer;
function buscar() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    const q = document.getElementById('searchInput').value;
    const e = document.getElementById('filtroEstado').value;
    location.href = `admin.php?q=${encodeURIComponent(q)}&estado=${encodeURIComponent(e)}`;
  }, 450);
}

// ── Modal helpers ─────────────────────────────────────────────
function cerrarModal(id) { document.getElementById(id).classList.remove('open'); }
document.querySelectorAll('.modal-overlay').forEach(o => {
  o.addEventListener('click', e => { if(e.target === o) o.classList.remove('open'); });
});

// ── Modal Empleado ────────────────────────────────────────────
function abrirModal(datos = null) {
  document.getElementById('modalTitle').textContent = datos ? 'Editar Empleado' : 'Nuevo Empleado';
  document.getElementById('formEmp').reset();
  document.getElementById('camposContrato').style.display = datos ? 'none' : 'grid';
  document.getElementById('seccionContrato').style.display = datos ? 'none' : 'block';

  if (datos) {
    document.getElementById('f_ID_Persona').value  = datos.ID_Persona  || 0;
    document.getElementById('f_ID_Empleado').value = datos.ID_Empleado || 0;
    document.getElementById('f_doc').value       = datos.Numero_Documento || '';
    document.getElementById('f_nombres').value   = datos.Nombres   || '';
    document.getElementById('f_apellidos').value = datos.Apellidos || '';
    document.getElementById('f_email').value     = datos.Email     || '';
    document.getElementById('f_tel').value       = datos.Telefono  || '';
    document.getElementById('f_fnac').value      = datos.Fecha_Nacimiento || '';
    document.getElementById('f_cargo').value     = datos.ID_Cargo  || '';
    document.getElementById('f_fingreso').value  = datos.Fecha_Ingreso   || '';
    document.getElementById('f_fretiro').value   = datos.Fecha_Retiro    || '';
    document.getElementById('f_estado').value    = datos.Estado_Empleado || 'Activo';
    document.getElementById('f_pin').value       = datos.PIN    || '';
    document.getElementById('f_rol').value       = datos.Rol    || 'empleado';
  } else {
    document.getElementById('f_ID_Persona').value  = 0;
    document.getElementById('f_ID_Empleado').value = 0;
    document.getElementById('f_fingreso').value = new Date().toISOString().slice(0,10);
    document.getElementById('f_inicio_contrato').value = new Date().toISOString().slice(0,10);
  }
  document.getElementById('modalEmp').classList.add('open');
}

async function editarEmpleado(id) {
  const fd = new FormData();
  fd.append('accion','get_empleado');
  fd.append('ID_Empleado', id);
  const res  = await fetch('admin.php',{method:'POST',body:fd});
  const data = await res.json();
  abrirModal(data);
}

// ── Historial asistencia ──────────────────────────────────────
async function verRegistros(id, nombre) {
  document.getElementById('histTitle').textContent = `Asistencia — ${nombre}`;
  document.getElementById('histContent').innerHTML = '<p style="text-align:center;padding:32px;opacity:.5">Cargando...</p>';
  document.getElementById('modalHist').classList.add('open');

  const fd = new FormData();
  fd.append('accion','get_registros');
  fd.append('ID_Empleado',id);
  const res  = await fetch('admin.php',{method:'POST',body:fd});
  const rows = await res.json();

  if (!rows.length) {
    document.getElementById('histContent').innerHTML = '<p style="text-align:center;padding:32px;opacity:.4">Sin registros de asistencia</p>';
    return;
  }

  let html = '<table class="hist-table"><thead><tr><th>Fecha</th><th>Entrada</th><th>Salida</th><th>Tipo</th><th>Duración</th></tr></thead><tbody>';
  rows.forEach(r => {
    let dur = '—';
    if (r.Hora_Entrada && r.Hora_Salida) {
      const [h1,m1] = r.Hora_Entrada.split(':').map(Number);
      const [h2,m2] = r.Hora_Salida.split(':').map(Number);
      const mins = (h2*60+m2) - (h1*60+m1);
      dur = `${Math.floor(mins/60)}h ${mins%60}m`;
    }
    html += `<tr><td>${r.Fecha}</td><td>${r.Hora_Entrada?r.Hora_Entrada.slice(0,5):'—'}</td><td>${r.Hora_Salida?r.Hora_Salida.slice(0,5):'—'}</td><td>${r.Tipo||'Normal'}</td><td>${dur}</td></tr>`;
  });
  html += '</tbody></table>';
  document.getElementById('histContent').innerHTML = html;
}

// ── Contratos (R13) ───────────────────────────────────────────
let _contratoEmpId = 0, _contratoCargoId = 0;
async function verContratos(empId, cargoId, nombre) {
  _contratoEmpId   = empId;
  _contratoCargoId = cargoId;
  document.getElementById('contratosTitle').textContent = `Contratos — ${nombre}`;
  document.getElementById('fc_emp').value   = empId;
  document.getElementById('fc_cargo').value = cargoId;
  document.getElementById('contratosListado').innerHTML = '<p style="opacity:.5">Cargando...</p>';
  document.getElementById('modalContratos').classList.add('open');

  const fd = new FormData();
  fd.append('accion','get_contratos');
  fd.append('ID_Empleado', empId);
  const res  = await fetch('admin.php',{method:'POST',body:fd});
  const rows = await res.json();

  if (!rows.length) {
    document.getElementById('contratosListado').innerHTML = '<div class="alert-r13"><svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>Este empleado no tiene contratos registrados. Añade uno abajo.</div>';
    return;
  }

  let html = '<table class="hist-table"><thead><tr><th>Tipo</th><th>Salario</th><th>Inicio</th><th>Fin</th><th>Estado</th></tr></thead><tbody>';
  rows.forEach(r => {
    const badge = r.Estado_Contrato === 'Vigente' ? 'badge-vigente' : r.Estado_Contrato === 'Terminado' ? 'badge-terminado' : 'badge-suspendido';
    html += `<tr><td>${r.Tipo_Contrato||'—'}</td><td>${r.Salario_Pactado?'$ '+Number(r.Salario_Pactado).toLocaleString('es-CO'):'—'}</td><td>${r.Fecha_Inicio||'—'}</td><td>${r.Fecha_Fin||'Indefinido'}</td><td><span class="badge ${badge}">${r.Estado_Contrato}</span></td></tr>`;
  });
  html += '</tbody></table>';
  document.getElementById('contratosListado').innerHTML = html;
}

document.getElementById('formContrato').addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  // Manejar el select de empleado en SST si aplica
  const empSel = document.getElementById('fsst_emp_select');
  if (empSel) fd.set('ID_Empleado_SST', empSel.value);

  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.textContent = 'Guardando...';
  try {
    const res  = await fetch('admin.php',{method:'POST',body:fd});
    const data = await res.json();
    showToast(data.msg, data.ok ? 'success' : 'error');
    if (data.ok) { cerrarModal('modalContratos'); setTimeout(()=>location.reload(),1200); }
  } catch(err) { showToast('Error de comunicación','error'); }
  finally { btn.disabled=false; btn.textContent='Guardar contrato'; }
});

// ── SST (R14) ─────────────────────────────────────────────────
function abrirSST(empId, nombre) {
  document.getElementById('sstTitle').textContent = `SST — ${nombre}`;
  document.getElementById('fsst_emp').value = empId;
  document.getElementById('formSST').reset();
  document.getElementById('fsst_emp').value = empId;
  document.getElementById('modalSST').classList.add('open');
}

function abrirSSTNuevo() {
  document.getElementById('sstTitle').textContent = 'Registrar Accidente SST';
  document.getElementById('formSST').reset();
  document.getElementById('modalSST').classList.add('open');
}

document.getElementById('formSST').addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const empSel = document.getElementById('fsst_emp_select');
  if (empSel && empSel.value) fd.set('ID_Empleado_SST', empSel.value);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.textContent = 'Guardando...';
  try {
    const res  = await fetch('admin.php',{method:'POST',body:fd});
    const data = await res.json();
    showToast(data.msg, data.ok ? 'success' : 'error');
    if (data.ok) { cerrarModal('modalSST'); setTimeout(()=>location.reload(),1200); }
  } catch(err) { showToast('Error de comunicación','error'); }
  finally { btn.disabled=false; btn.textContent='Registrar accidente'; }
});

// ── Dar de baja (R12) ─────────────────────────────────────────
async function darDeBaja(id, nombre) {
  if (!confirm(`¿Dar de baja a ${nombre}?\nSe marcará como Inactivo, se registrará la fecha de retiro y se cerrarán sus contratos vigentes.`)) return;
  const fd = new FormData();
  fd.append('accion','eliminar_empleado');
  fd.append('ID_Empleado',id);
  const res  = await fetch('admin.php',{method:'POST',body:fd});
  const data = await res.json();
  showToast(data.msg, data.ok ? 'success' : 'error');
  if (data.ok) setTimeout(() => location.reload(), 1500);
}

// ── Formulario empleado ───────────────────────────────────────
document.getElementById('formEmp').addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.textContent = 'Guardando...';
  try {
    const res  = await fetch('admin.php',{method:'POST',body:fd});
    const data = await res.json();
    showToast(data.msg, data.ok ? 'success' : 'error');
    if (data.ok) { cerrarModal('modalEmp'); setTimeout(()=>location.reload(),1200); }
  } catch(err) { showToast('Error de comunicación','error'); }
  finally { btn.disabled=false; btn.innerHTML='<svg width="16" viewBox="0 0 24 24" fill="white"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>Guardar empleado'; }
});

// ── Toast ─────────────────────────────────────────────────────
function showToast(msg, tipo='') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + tipo + ' show';
  setTimeout(() => t.className='toast', 4000);
}

// ── PIN solo dígitos ──────────────────────────────────────────
document.getElementById('f_pin').addEventListener('input', function() {
  this.value = this.value.replace(/\D/g,'').slice(0,6);
});
</script>
</body>
</html>
