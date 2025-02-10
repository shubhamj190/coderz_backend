# Generated by Django 4.2.18 on 2025-02-10 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_grade_division'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='division',
            options={'verbose_name': 'Division', 'verbose_name_plural': 'Divisions'},
        ),
        migrations.AlterUniqueTogether(
            name='division',
            unique_together={('grade', 'name')},
        ),
    ]
