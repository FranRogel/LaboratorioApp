# Generated by Django 5.0.4 on 2024-04-19 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0006_alter_videojuego_portada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videojuego',
            name='plataforms',
            field=models.CharField(max_length=250),
        ),
    ]
