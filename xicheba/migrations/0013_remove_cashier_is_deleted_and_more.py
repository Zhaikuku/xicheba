# Generated by Django 4.1.2 on 2022-10-19 23:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xicheba', '0012_extraproject_is_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashier',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='extraproject',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='users',
            name='is_deleted',
        ),
    ]
