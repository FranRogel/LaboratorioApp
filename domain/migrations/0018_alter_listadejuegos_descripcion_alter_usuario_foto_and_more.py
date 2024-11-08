# Generated by Django 5.0.4 on 2024-05-28 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0017_alter_siguen_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listadejuegos',
            name='descripcion',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='foto',
            field=models.FileField(default='media/usuarios/yu_foto_perfil.jpg', null=True, upload_to='media/uploads/'),
        ),
        migrations.AlterField(
            model_name='videojuego',
            name='descripcion',
            field=models.CharField(max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name='videojuego',
            name='portada',
            field=models.FileField(null=True, upload_to='media/uploads/'),
        ),
        migrations.AlterUniqueTogether(
            name='listadejuegos',
            unique_together={('name', 'creator')},
        ),
    ]
