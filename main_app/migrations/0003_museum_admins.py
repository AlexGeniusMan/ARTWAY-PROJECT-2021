# Generated by Django 3.1.2 on 2021-01-15 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_auto_20210115_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='museum',
            name='admins',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='museum', to=settings.AUTH_USER_MODEL, verbose_name='Администраторы'),
        ),
    ]
