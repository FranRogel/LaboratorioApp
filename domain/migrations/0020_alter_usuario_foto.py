# Generated by Django 5.0.4 on 2024-06-07 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0019_alter_reseña_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='foto',
            field=models.ImageField(default='media/usuarios/generica.jpg', upload_to='media/usuarios/'),
        ),
    ]