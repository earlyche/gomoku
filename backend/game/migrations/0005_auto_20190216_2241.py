# Generated by Django 2.1.7 on 2019-02-16 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20190216_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='type',
            field=models.CharField(max_length=30),
        ),
    ]