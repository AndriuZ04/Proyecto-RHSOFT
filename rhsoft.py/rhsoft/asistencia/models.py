from django.db import models


class Persona(models.Model):
    ID_Persona       = models.AutoField(primary_key=True)
    Numero_Documento = models.CharField(max_length=50, unique=True)
    Nombres          = models.CharField(max_length=150)
    Apellidos        = models.CharField(max_length=150)
    Email            = models.CharField(max_length=150, null=True, blank=True)
    Telefono         = models.CharField(max_length=30,  null=True, blank=True)
    Fecha_Nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'personas'

    def __str__(self):
        return f'{self.Nombres} {self.Apellidos}'


class Departamento(models.Model):
    ID_Departamento     = models.AutoField(primary_key=True)
    Nombre_Departamento = models.CharField(max_length=150)

    class Meta:
        db_table = 'departamentos'

    def __str__(self):
        return self.Nombre_Departamento


class Cargo(models.Model):
    ID_Cargo              = models.AutoField(primary_key=True)
    ID_Departamento       = models.ForeignKey(Departamento, on_delete=models.PROTECT,
                                              db_column='ID_Departamento')
    Nombre_Cargo          = models.CharField(max_length=150)
    Descripcion_Funciones = models.CharField(max_length=500, null=True, blank=True)
    Salario_Base          = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    Hora_Inicio_Jornada   = models.TimeField(null=True, blank=True)
    Hora_Fin_Jornada      = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'cargos'

    def __str__(self):
        return self.Nombre_Cargo


class CargoDia(models.Model):
    ID_Cargo   = models.ForeignKey(Cargo, on_delete=models.CASCADE,
                                   db_column='ID_Cargo')
    Dia_Semana = models.CharField(max_length=20)

    class Meta:
        db_table   = 'cargo_dias'
        unique_together = [('ID_Cargo', 'Dia_Semana')]


class Empleado(models.Model):
    ROL_CHOICES = [('admin', 'Administrador'), ('empleado', 'Empleado')]
    ESTADO_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo')]

    ID_Empleado     = models.AutoField(primary_key=True)
    ID_Persona      = models.ForeignKey(Persona, on_delete=models.PROTECT,
                                        db_column='ID_Persona')
    ID_Cargo        = models.ForeignKey(Cargo, on_delete=models.PROTECT,
                                        db_column='ID_Cargo')
    PIN             = models.CharField(max_length=6, unique=True)
    Rol             = models.CharField(max_length=20, choices=ROL_CHOICES, default='empleado')
    Fecha_Ingreso   = models.DateField(null=True, blank=True)
    Fecha_Retiro    = models.DateField(null=True, blank=True)
    Estado_Empleado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Activo')

    class Meta:
        db_table = 'empleados'

    def __str__(self):
        return str(self.ID_Persona)

    @property
    def nombre_completo(self):
        return f'{self.ID_Persona.Nombres} {self.ID_Persona.Apellidos}'


class Contrato(models.Model):
    ESTADO_CHOICES = [('Vigente', 'Vigente'), ('Terminado', 'Terminado'), ('Suspendido', 'Suspendido')]

    ID_Contrato     = models.AutoField(primary_key=True)
    ID_Empleado     = models.ForeignKey(Empleado, on_delete=models.PROTECT,
                                        db_column='ID_Empleado', null=True, blank=True)
    ID_Cargo        = models.ForeignKey(Cargo, on_delete=models.PROTECT,
                                        db_column='ID_Cargo')
    Tipo_Contrato   = models.CharField(max_length=100, null=True, blank=True)
    Salario_Pactado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    Fecha_Inicio    = models.DateField(null=True, blank=True)
    Fecha_Fin       = models.DateField(null=True, blank=True)
    Estado_Contrato = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Vigente')

    class Meta:
        db_table = 'contratos'


class Registro(models.Model):
    ID_Registro = models.AutoField(primary_key=True)
    ID_Empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT,
                                    db_column='ID_Empleado')
    Fecha       = models.DateField()
    Hora_Entrada = models.TimeField()
    Hora_Salida  = models.TimeField(null=True, blank=True)
    Tipo         = models.CharField(max_length=80, default='Normal')
    Observacion  = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'registros'


class SstAccidente(models.Model):
    ID_Accidente     = models.AutoField(primary_key=True)
    ID_Empleado      = models.ForeignKey(Empleado, on_delete=models.PROTECT,
                                         db_column='ID_Empleado')
    Fecha_Accidente  = models.DateField(null=True, blank=True)
    Tipo_Accidente   = models.CharField(max_length=100, null=True, blank=True)
    Descripcion      = models.CharField(max_length=500, null=True, blank=True)
    Accion_Inmediata = models.CharField(max_length=500, null=True, blank=True)
    Fecha_Reporte    = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'sst_accidentes'
