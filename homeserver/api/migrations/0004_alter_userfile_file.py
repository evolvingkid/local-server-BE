# Generated by Django 5.1.5 on 2025-02-09 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_userfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfile',
            name='file',
            field=models.CharField(max_length=124),
        ),
    ]
