# Generated by Django 5.0.4 on 2024-05-17 16:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0010_reseña_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reseña',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reseñas', to='domain.videojuego'),
        ),
        migrations.AlterField(
            model_name='reseña',
            name='writer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reseñas', to='domain.usuario'),
        ),
    ]
