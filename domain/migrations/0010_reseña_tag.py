# Generated by Django 5.0.4 on 2024-04-26 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0009_alter_estaen_lista_alter_legusta_lista'),
    ]

    operations = [
        migrations.AddField(
            model_name='reseña',
            name='tag',
            field=models.CharField(choices=[('C', 'Complete'), ('P', 'Playing'), ('D', 'Drop')], max_length=1, null=True),
        ),
    ]
