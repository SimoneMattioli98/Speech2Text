# Generated by Django 3.2.5 on 2021-08-10 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0004_request_model_chosen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='id',
        ),
        migrations.AlterField(
            model_name='request',
            name='id_request',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]