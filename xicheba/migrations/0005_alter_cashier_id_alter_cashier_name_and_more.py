# Generated by Django 4.1.2 on 2022-10-19 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xicheba', '0004_cashier_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashier',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='cashier',
            name='name',
            field=models.CharField(choices=[('1-CL', '1-车蜡'), ('2-BLS', '2-玻璃水')], default='', max_length=30, verbose_name='物品名称'),
        ),
        migrations.AlterField(
            model_name='extraproject',
            name='action',
            field=models.CharField(choices=[('1-DL', '1-打蜡'), ('2-JD', '2-脚垫'), ('3-CZ', '3-车座'), ('4-PG', '4-抛光'), ('5-SF', '5-水费'), ('6-DF', '6-电费')], default='', max_length=30, verbose_name='事件类型'),
        ),
    ]
