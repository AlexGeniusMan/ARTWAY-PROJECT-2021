# Generated by Django 3.1.2 on 2021-01-20 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0017_ticket_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='artifact',
            name='video',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Ссылка на видео'),
        ),
    ]