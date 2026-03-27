<?php
require_once 'config.php';

// Manejar logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: index.php');
    exit;
}

// Manejar login por PIN
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['pin'])) {
    $pin = trim($_POST['pin']);
    $db  = getDB();

    $stmt = $db->prepare("
        SELECT e.ID_Empleado, e.Rol, e.Estado_Empleado,
               p.Nombres, p.Apellidos
        FROM   EMPLEADOS e
        JOIN   PERSONAS  p ON p.ID_Persona = e.ID_Persona
        WHERE  e.PIN = ? AND e.Estado_Empleado = 'Activo'
    ");
    $stmt->execute([$pin]);
    $emp = $stmt->fetch();

    if ($emp) {
        $_SESSION['empleado_id'] = $emp['ID_Empleado'];
        $_SESSION['nombre']      = $emp['Nombres'] . ' ' . $emp['Apellidos'];
        $_SESSION['rol']         = $emp['Rol'];

        if ($emp['Rol'] === 'admin') {
            header('Location: admin.php');
        } else {
            header('Location: registro.php');
        }
        exit;
    } else {
        $error = 'PIN incorrecto o empleado inactivo.';
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sistema de Gestión — Acceso</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --azul-oscuro : #355872;
    --azul-medio  : #7aaace;
    --azul-claro  : #9cd5ff;
    --blanco-roto : #f7f8f0;
    --texto       : #1e3344;
    --sombra      : 0 8px 40px rgba(53,88,114,.18);
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--azul-oscuro);
    background-image:
      radial-gradient(ellipse 80% 60% at 20% 10%, rgba(122,170,206,.25) 0%, transparent 60%),
      radial-gradient(ellipse 60% 80% at 80% 90%, rgba(156,213,255,.15) 0%, transparent 60%);
    font-family: 'DM Sans', sans-serif;
    overflow: hidden;
  }

  /* Patrón decorativo de fondo */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
      45deg,
      rgba(255,255,255,.03) 0px,
      rgba(255,255,255,.03) 1px,
      transparent 1px,
      transparent 40px
    );
    pointer-events: none;
  }

  .card {
    background: var(--blanco-roto);
    border-radius: 24px;
    padding: 56px 52px;
    width: min(460px, 94vw);
    box-shadow: var(--sombra);
    animation: aparecer .6s cubic-bezier(.22,1,.36,1) both;
    position: relative;
    overflow: hidden;
  }

  /* Acento superior */
  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, var(--azul-oscuro), var(--azul-medio), var(--azul-claro));
  }

  @keyframes aparecer {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .logo-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 36px;
  }

  .logo-icon {
    width: 50px; height: 50px;
    background: var(--azul-oscuro);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }

  .logo-icon svg { width: 26px; height: 26px; fill: var(--blanco-roto); }

  .logo-text h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: var(--texto);
    line-height: 1.2;
  }

  .logo-text p {
    font-size: .78rem;
    color: var(--azul-oscuro);
    opacity: .7;
    margin-top: 2px;
    letter-spacing: .04em;
    text-transform: uppercase;
  }

  h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--texto);
    line-height: 1.15;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: .92rem;
    color: var(--azul-oscuro);
    opacity: .65;
    margin-bottom: 36px;
  }

  label {
    display: block;
    font-size: .82rem;
    font-weight: 600;
    color: var(--azul-oscuro);
    letter-spacing: .05em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .pin-group {
    display: flex;
    gap: 10px;
    margin-bottom: 28px;
  }

  .pin-group input[type="text"] {
    width: 48px; height: 56px;
    border: 2px solid rgba(53,88,114,.2);
    border-radius: 12px;
    background: white;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--texto);
    outline: none;
    transition: border-color .2s, box-shadow .2s;
    caret-color: transparent;
  }

  .pin-group input[type="text"]:focus {
    border-color: var(--azul-medio);
    box-shadow: 0 0 0 3px rgba(122,170,206,.25);
  }

  .pin-group input[type="text"].filled {
    border-color: var(--azul-oscuro);
    background: rgba(53,88,114,.05);
  }

  /* PIN oculto real */
  #pin-real {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .btn {
    width: 100%;
    padding: 16px;
    background: var(--azul-oscuro);
    color: var(--blanco-roto);
    border: none;
    border-radius: 14px;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: .03em;
    transition: background .2s, transform .15s;
    position: relative;
    overflow: hidden;
  }

  .btn::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,.08), transparent);
  }

  .btn:hover  { background: #2a4860; transform: translateY(-1px); }
  .btn:active { transform: translateY(0); }

  .error-msg {
    background: #fff0f0;
    border: 1.5px solid #f5b8b8;
    color: #c0392b;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: .87rem;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .hint {
    text-align: center;
    margin-top: 24px;
    font-size: .8rem;
    color: var(--azul-oscuro);
    opacity: .5;
  }

  /* Teclado numérico */
  .numpad {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 20px;
  }

  .num-btn {
    height: 52px;
    border: 2px solid rgba(53,88,114,.15);
    border-radius: 12px;
    background: white;
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--texto);
    cursor: pointer;
    transition: all .15s;
  }

  .num-btn:hover  { background: rgba(122,170,206,.15); border-color: var(--azul-medio); }
  .num-btn:active { transform: scale(.95); }

  .num-btn.del {
    background: rgba(53,88,114,.08);
    font-size: .9rem;
    color: var(--azul-oscuro);
  }

  .num-btn.cero { grid-column: 2; }

  .divider {
    height: 1px;
    background: rgba(53,88,114,.1);
    margin: 28px 0;
  }
</style>
</head>
<body>

<div class="card">
  <div class="logo-wrap">
    <div class="logo-icon">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
      </svg>
    </div>
    <div class="logo-text">
      <h1>Gestión Empresarial</h1>
      <p>Sistema de Control</p>
    </div>
  </div>

  <h2>Ingresa<br><em>tu PIN</em></h2>
  <p class="subtitle">Accede con tu código de 6 dígitos</p>

  <?php if (!empty($error)): ?>
    <div class="error-msg">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <?= htmlspecialchars($error) ?>
    </div>
  <?php endif; ?>

  <form method="POST" id="loginForm">
    <label>Código PIN</label>
    <div class="pin-group" id="pinDisplay">
      <input type="text" maxlength="1" readonly id="d1" data-i="0">
      <input type="text" maxlength="1" readonly id="d2" data-i="1">
      <input type="text" maxlength="1" readonly id="d3" data-i="2">
      <input type="text" maxlength="1" readonly id="d4" data-i="3">
      <input type="text" maxlength="1" readonly id="d5" data-i="4">
      <input type="text" maxlength="1" readonly id="d6" data-i="5">
    </div>
    <input type="hidden" name="pin" id="pin-real">

    <div class="numpad">
      <?php foreach ([1,2,3,4,5,6,7,8,9] as $n): ?>
        <button type="button" class="num-btn" onclick="addDigit('<?= $n ?>')"><?= $n ?></button>
      <?php endforeach; ?>
      <button type="button" class="num-btn del" onclick="delDigit()">⌫ Borrar</button>
      <button type="button" class="num-btn cero" onclick="addDigit('0')">0</button>
    </div>

    <button type="submit" class="btn" id="submitBtn" disabled>Ingresar al sistema →</button>
  </form>

  <div class="hint">PIN de 6 dígitos proporcionado por RRHH</div>
</div>

<script>
  let pin = [];

  function updateDisplay() {
    const digits = document.querySelectorAll('#pinDisplay input');
    digits.forEach((d, i) => {
      d.value = pin[i] ? '●' : '';
      d.classList.toggle('filled', !!pin[i]);
    });
    document.getElementById('pin-real').value = pin.join('');
    document.getElementById('submitBtn').disabled = pin.length < 6;
  }

  function addDigit(d) {
    if (pin.length < 6) {
      pin.push(d);
      updateDisplay();
      // Auto-submit cuando completa 6 dígitos
      if (pin.length === 6) {
        setTimeout(() => document.getElementById('loginForm').submit(), 300);
      }
    }
  }

  function delDigit() {
    pin.pop();
    updateDisplay();
  }

  // Soporte teclado físico
  document.addEventListener('keydown', e => {
    if (e.key >= '0' && e.key <= '9') addDigit(e.key);
    if (e.key === 'Backspace') delDigit();
  });
</script>
</body>
</html>
