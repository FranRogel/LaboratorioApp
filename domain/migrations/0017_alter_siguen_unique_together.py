# Generated by Django 5.0.4 on 2024-05-19 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0016_alter_estaen_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='siguen',
            unique_together={('seguidor', 'seguido')},
        ),
    ]
