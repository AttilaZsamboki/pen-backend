# Generated by Django 4.2.4 on 2023-08-07 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('script_name', models.TextField()),
                ('time', models.DateTimeField()),
                ('status', models.TextField()),
                ('value', models.TextField()),
                ('details', models.TextField()),
            ],
            options={
                'db_table': 'logs',
                'managed': False,
            },
        ),
    ]
