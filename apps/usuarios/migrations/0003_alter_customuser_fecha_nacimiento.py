# Generated by Django 5.1.4 on 2024-12-23 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_customuser_fecha_nacimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, help_text='Formato: dd/mm/yyyy', null=True),
        ),
    ]