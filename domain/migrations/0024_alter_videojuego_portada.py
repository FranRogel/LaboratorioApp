# Generated by Django 5.0.4 on 2024-06-27 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0023_alter_videojuego_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videojuego',
            name='portada',
            field=models.ImageField(upload_to='media/uploads/'),
        ),
    ]