# Generated by Django 4.2.18 on 2025-02-10 08:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_division_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='AltPhoneNumber',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='FirstName',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='LastName',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='', max_length=10),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FirstName', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('LastName', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('specialization', models.CharField(max_length=100)),
                ('qualification', models.CharField(max_length=255)),
                ('years_of_experience', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_divisions', models.ManyToManyField(related_name='teachers', to='accounts.division')),
                ('assigned_grades', models.ManyToManyField(related_name='teachers', to='accounts.grade')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
