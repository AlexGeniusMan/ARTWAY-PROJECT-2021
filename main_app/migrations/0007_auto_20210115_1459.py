# Generated by Django 3.1.2 on 2021-01-15 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_auto_20210115_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='prev_location',
            field=models.IntegerField(blank=True, null=True, verbose_name='Локация выше'),
        ),
        migrations.AlterField(
            model_name='artifact',
            name='audio',
            field=models.FileField(blank=True, upload_to='artifact_audios', verbose_name='Аудио'),
        ),
        migrations.AlterField(
            model_name='artifact',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='artifact_photos', verbose_name='Фотография'),
        ),
        migrations.AlterField(
            model_name='artifact',
            name='qr_code',
            field=models.ImageField(blank=True, upload_to='artifact_qrs', verbose_name='QR code'),
        ),
        migrations.AlterField(
            model_name='location',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='locations', verbose_name='Фотография'),
        ),
        migrations.AlterField(
            model_name='museum',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='museums', verbose_name='Фотография'),
        ),
    ]