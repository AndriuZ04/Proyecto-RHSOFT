from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0002_postulacion'),
    ]

    operations = [
        # Agregar campo Requisitos a Cargo
        migrations.AddField(
            model_name='cargo',
            name='Requisitos',
            field=models.TextField(blank=True, null=True),
        ),

        # Agregar campos IA a Postulacion
        migrations.AddField(
            model_name='postulacion',
            name='Resultado_IA',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postulacion',
            name='Puntaje_IA',
            field=models.IntegerField(blank=True, null=True),
        ),

        # Actualizar estados de Empleado
        migrations.AlterField(
            model_name='empleado',
            name='Estado_Empleado',
            field=models.CharField(
                choices=[
                    ('Activo',     'Activo'),
                    ('Inactivo',   'Inactivo'),
                    ('Licencia',   'En licencia'),
                    ('Suspension', 'Suspendido'),
                    ('Retirado',   'Retirado'),
                ],
                default='Activo',
                max_length=50,
            ),
        ),

        # Tabla Evaluaciones
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('ID_Evaluacion', models.AutoField(primary_key=True, serialize=False)),
                ('Fecha', models.DateField()),
                ('Periodo', models.CharField(
                    choices=[
                        ('Mensual', 'Mensual'),
                        ('Trimestral', 'Trimestral'),
                        ('Semestral', 'Semestral'),
                        ('Anual', 'Anual'),
                    ],
                    max_length=20,
                )),
                ('Resultado', models.CharField(
                    choices=[
                        ('Excelente', 'Excelente'),
                        ('Bueno', 'Bueno'),
                        ('Regular', 'Regular'),
                        ('Deficiente', 'Deficiente'),
                    ],
                    max_length=20,
                )),
                ('Observaciones', models.TextField(blank=True, null=True)),
                ('Evaluador', models.CharField(blank=True, max_length=150, null=True)),
                ('ID_Empleado', models.ForeignKey(
                    db_column='ID_Empleado',
                    on_delete=django.db.models.deletion.PROTECT,
                    to='asistencia.empleado',
                )),
            ],
            options={'db_table': 'evaluaciones'},
        ),

        # Tabla Capacitaciones
        migrations.CreateModel(
            name='Capacitacion',
            fields=[
                ('ID_Capacitacion', models.AutoField(primary_key=True, serialize=False)),
                ('Titulo', models.CharField(max_length=200)),
                ('Descripcion', models.TextField(blank=True, null=True)),
                ('Tipo', models.CharField(
                    choices=[
                        ('Presencial', 'Presencial'),
                        ('Virtual', 'Virtual'),
                        ('Mixta', 'Mixta'),
                    ],
                    default='Presencial',
                    max_length=20,
                )),
                ('Fecha_Evento', models.DateField(blank=True, null=True)),
                ('Lugar', models.CharField(blank=True, max_length=200, null=True)),
                ('Material', models.FileField(blank=True, null=True, upload_to='capacitaciones/')),
                ('Fecha_Publicacion', models.DateField(auto_now_add=True)),
            ],
            options={'db_table': 'capacitaciones'},
        ),

        # Tabla EmpleadoCapacitacion
        migrations.CreateModel(
            name='EmpleadoCapacitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('Estado', models.CharField(
                    choices=[
                        ('Pendiente', 'Pendiente'),
                        ('En curso', 'En curso'),
                        ('Completada', 'Completada'),
                    ],
                    default='Pendiente',
                    max_length=20,
                )),
                ('Fecha_Completado', models.DateField(blank=True, null=True)),
                ('ID_Capacitacion', models.ForeignKey(
                    db_column='ID_Capacitacion',
                    on_delete=django.db.models.deletion.CASCADE,
                    to='asistencia.capacitacion',
                )),
                ('ID_Empleado', models.ForeignKey(
                    db_column='ID_Empleado',
                    on_delete=django.db.models.deletion.CASCADE,
                    to='asistencia.empleado',
                )),
            ],
            options={
                'db_table': 'empleado_capacitaciones',
                'unique_together': {('ID_Empleado', 'ID_Capacitacion')},
            },
        ),
    ]
