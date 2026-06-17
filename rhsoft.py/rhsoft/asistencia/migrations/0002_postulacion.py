from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Postulacion',
            fields=[
                ('ID_Postulacion', models.AutoField(primary_key=True, serialize=False)),
                ('Hoja_Vida', models.FileField(upload_to='hojas_de_vida/')),
                ('Estado', models.CharField(
                    choices=[
                        ('Pendiente',  'Pendiente'),
                        ('Aceptado',   'Aceptado'),
                        ('Entrevista', 'En entrevista'),
                        ('Rechazado',  'Rechazado'),
                        ('Contratado', 'Contratado'),
                    ],
                    default='Pendiente',
                    max_length=20
                )),
                ('Fecha_Postulacion', models.DateField(auto_now_add=True)),
                ('Observacion', models.CharField(blank=True, max_length=500, null=True)),
                ('Cargo_Aspirado', models.ForeignKey(
                    db_column='Cargo_Aspirado',
                    on_delete=django.db.models.deletion.PROTECT,
                    to='asistencia.cargo'
                )),
                ('ID_Persona', models.ForeignKey(
                    db_column='ID_Persona',
                    on_delete=django.db.models.deletion.PROTECT,
                    to='asistencia.persona'
                )),
            ],
            options={
                'db_table': 'postulaciones',
            },
        ),
    ]
