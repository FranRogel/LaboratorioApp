# Generated by Django 5.0.4 on 2024-04-26 21:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0007_alter_videojuego_plataforms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listadejuegos',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listas_de_juegos', to='domain.usuario'),
        ),
    ]
