# Generated by Django 3.2 on 2024-09-05 16:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moshtari', '0002_stamp_reasons_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stamp_reasons',
            name='limit',
            field=models.IntegerField(blank=True, default=0, help_text='اگر صفر باشد میتوانید مهر نامحدود با این دلیل بزنید!!', validators=[django.core.validators.MinValueValidator(0)], verbose_name='حداکثر تعداد مهر'),
        ),
    ]
