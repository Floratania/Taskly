# Generated by Django 5.0 on 2023-12-28 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0004_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='date_end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.CharField(max_length=100, null=True),
        ),
    ]