# Generated by Django 5.1.5 on 2025-02-09 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_userfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfile',
            name='file',
            field=models.URLField(),
        ),
    ]
