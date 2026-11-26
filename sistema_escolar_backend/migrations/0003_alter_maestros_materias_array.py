import json

from django.db import migrations, models


def normalizar_materias(apps, schema_editor):
    # Garantiza que el texto existente sea JSON válido antes de convertir la columna
    Maestros = apps.get_model('sistema_escolar_backend', 'Maestros')
    for maestro in Maestros.objects.all():
        try:
            json.loads(maestro.materias_array)
        except (TypeError, ValueError):
            maestro.materias_array = '[]'
            maestro.save(update_fields=['materias_array'])


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_escolar_backend', '0002_administradores_maestros_delete_profiles'),
    ]

    operations = [
        migrations.RunPython(normalizar_materias, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='maestros',
            name='materias_array',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
