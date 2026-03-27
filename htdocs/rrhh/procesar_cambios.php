<?php
// 1. Conexión a la base de datos
$conexion = mysqli_connect("localhost", "root", "", "cobalsa_rrhh");

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    
    // 2. Recibir datos del formulario
    $nombres = $_POST['txt_nombres'];
    $apellidos = $_POST['txt_apellidos'];
    $email = $_POST['txt_email'];
    $telefono = $_POST['txt_tel'];
    $id_empleado = 1; // Aquí usarías $_SESSION['id_user']

    // 3. Lógica para la Foto de Perfil
    $ruta_foto = "";
    if (isset($_FILES['nueva_foto']) && $_FILES['nueva_foto']['error'] == 0) {
        $nombre_archivo = time() . "_" . $_FILES['nueva_foto']['name'];
        $ruta_destino = "uploads/" . $nombre_archivo;
        
        if (move_uploaded_file($_FILES['nueva_foto']['tmp_name'], $ruta_destino)) {
            $ruta_foto = ", foto = '$ruta_destino'";
        }
    }

    // 4. Actualizar tabla PERSONAS (basado en tu MER)
    // El empleado solo edita su información personal
    $sql = "UPDATE personas SET 
            nombres = '$nombres', 
            apellidos = '$apellidos', 
            email = '$email', 
            telefono = '$telefono' 
            $ruta_foto 
            WHERE id_persona = (SELECT id_persona FROM empleados WHERE id_empleado = $id_empleado)";

    if (mysqli_query($conexion, $sql)) {
        echo "<script>alert('¡Datos actualizados con éxito en COBALSA!'); window.location.href='perfil_empleado.php';</script>";
    } else {
        echo "Error al guardar: " . mysqli_error($conexion);
    }
}
?>