# Generated by Django 5.0.6 on 2024-05-26 12:56

import apps.user.enums
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('ADMIN', 'ADMIN'), ('USER', 'USER')], default=apps.user.enums.Role['USER'], max_length=255),
        ),
    ]
