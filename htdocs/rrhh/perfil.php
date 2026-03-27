<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfil Profesional | COBALSA RRHH</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root { 
            --dark: #355872; 
            --med: #7aaace; 
            --cream: #f8f0f0; 
        }
        body { background-color: var(--cream); }
        .bg-cobalsa { background-color: var(--dark); }
        .border-cobalsa { border-color: var(--med); }
        .text-cobalsa { color: var(--dark); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-0 md:p-6">

    <div class="w-full max-w-7xl min-h-screen md:min-h-0 bg-white md:rounded-3xl shadow-2xl overflow-hidden border border-gray-200 flex flex-col">
        
        <div class="bg-cobalsa p-6 flex justify-between items-center shadow-lg">
            <img src="logo.png" alt="COBALSA" class="h-10 md:h-14 object-contain" onerror="this.src='https://via.placeholder.com/200x60?text=COBALSA'">
            <div class="text-right">
                <h1 class="text-white text-lg md:text-2xl font-bold tracking-tighter uppercase">Expediente Digital de Empleado</h1>
                <p class="text-blue-200 text-xs">Gestión de Talento Humano</p>
            </div>
        </div>

        <form action="procesar_cambios.php" method="POST" enctype="multipart/form-data" class="flex-grow grid grid-cols-1 lg:grid-cols-12">
            
            <div class="lg:col-span-4 bg-gray-50 p-8 flex flex-col items-center border-r border-gray-100">
                <div class="relative group">
                    <div class="w-56 h-56 rounded-full border-8 border-white shadow-2xl overflow-hidden bg-white">
                        <img id="imgPreview" src="https://www.w3schools.com/howto/img_avatar.png" class="w-full h-full object-cover">
                    </div>
                    <label for="inputFoto" class="absolute bottom-4 right-4 bg-cobalsa text-white p-4 rounded-full cursor-pointer hover:scale-110 transition shadow-xl border-4 border-white">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path></svg>
                    </label>
                    <input type="file" id="inputFoto" name="nueva_foto" class="hidden" accept="image/*" onchange="preview(event)">
                </div>

                <div class="text-center mt-8 w-full">
                    <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Nombre del Funcionario</span>
                    <h2 class="text-2xl font-serif text-gray-800 font-bold italic mt-1">Nombre Apellido</h2>
                    <div class="mt-4 inline-block px-6 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-bold uppercase shadow-sm">
                        Empleado Activo
                    </div>
                </div>
            </div>

            <div class="lg:col-span-8 p-8 md:p-12 space-y-10">
                
                <section>
                    <div class="flex items-center space-x-3 mb-6">
                        <div class="w-1 h-6 bg-cobalsa rounded-full"></div>
                        <h3 class="text-xl font-bold text-gray-700">Información Personal Actualizable</h3>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-1">
                            <label class="text-xs font-bold text-gray-500 uppercase">Nombres Completos</label>
                            <input type="text" name="txt_nombres" placeholder="Escriba sus nombres" class="w-full p-4 bg-white border-2 border-gray-100 rounded-2xl focus:border-cobalsa outline-none transition shadow-sm">
                        </div>
                        <div class="space-y-1">
                            <label class="text-xs font-bold text-gray-500 uppercase">Apellidos</label>
                            <input type="text" name="txt_apellidos" placeholder="Escriba sus apellidos" class="w-full p-4 bg-white border-2 border-gray-100 rounded-2xl focus:border-cobalsa outline-none transition shadow-sm">
                        </div>
                        <div class="space-y-1">
                            <label class="text-xs font-bold text-gray-500 uppercase">Correo Personal</label>
                            <input type="email" name="txt_email" placeholder="ejemplo@cobalsa.com" class="w-full p-4 bg-white border-2 border-gray-100 rounded-2xl focus:border-cobalsa outline-none transition shadow-sm">
                        </div>
                        <div class="space-y-1">
                            <label class="text-xs font-bold text-gray-500 uppercase">Teléfono Móvil</label>
                            <input type="text" name="txt_tel" placeholder="+57 300..." class="w-full p-4 bg-white border-2 border-gray-100 rounded-2xl focus:border-cobalsa outline-none transition shadow-sm">
                        </div>
                    </div>
                </section>

                <section class="bg-blue-50/50 p-8 rounded-3xl border-2 border-blue-100 relative overflow-hidden">
                    <svg class="absolute -right-4 -bottom-4 w-32 h-32 text-blue-100 opacity-50" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"></path></svg>

                    <div class="flex items-center space-x-3 mb-6">
                        <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"></path></svg>
                        <h3 class="text-sm font-black text-gray-400 uppercase tracking-widest">Información Contractual (Solo Lectura)</h3>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
                        <div>
                            <p class="text-[10px] font-bold text-blue-400 uppercase">Rol Asignado</p>
                            <p class="text-lg font-bold text-gray-600">Empleado Estándar</p>
                        </div>
                        <div>
                            <p class="text-[10px] font-bold text-blue-400 uppercase">Departamento</p>
                            <p class="text-lg font-bold text-gray-600">Operaciones</p>
                        </div>
                        <div>
                            <p class="text-[10px] font-bold text-blue-400 uppercase">Cargo</p>
                            <p class="text-lg font-bold text-gray-600">Analista Junior</p>
                        </div>
                    </div>
                </section>

                <div class="flex justify-end pt-6">
                    <button type="submit" class="w-full md:w-auto bg-cobalsa text-white font-bold py-5 px-16 rounded-2xl shadow-2xl hover:bg-slate-800 transition-all active:scale-95 flex items-center justify-center space-x-3">
                        <span>Actualizar mi Perfil Profesional</span>
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </button>
                </div>
            </div>
        </form>
    </div>

    <script>
        function preview(e) {
            const reader = new FileReader();
            reader.onload = () => document.getElementById('imgPreview').src = reader.result;
            reader.readAsDataURL(e.target.files[0]);
        }
    </script>
</body>
</html>