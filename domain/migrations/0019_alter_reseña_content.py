# Generated by Django 5.0.4 on 2024-05-31 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0018_alter_listadejuegos_descripcion_alter_usuario_foto_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reseña',
            name='content',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
