# Generated by Django 3.1.2 on 2021-01-15 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_auto_20210115_1459'),
    ]

    operations = [
        migrations.RenameField(
            model_name='artifact',
            old_name='prev_artifact',
            new_name='prev',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='prev_location',
            new_name='prev',
        ),
    ]
