# Generated by Django 4.1.2 on 2022-10-19 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xicheba', '0008_alter_eventtype_id_alter_extraproject_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashier',
            name='earnings',
            field=models.IntegerField(default=0, help_text='收益自动计算', verbose_name='收益'),
        ),
        migrations.AlterField(
            model_name='cashier',
            name='name',
            field=models.CharField(choices=[('1-CL', '1-车蜡'), ('2-BLS', '2-玻璃水'), ('3-JD', '3-脚垫')], default='', max_length=30, verbose_name='物品名称'),
        ),
    ]
