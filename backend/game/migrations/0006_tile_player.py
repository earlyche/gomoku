# Generated by Django 2.1.7 on 2019-02-17 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20190216_2241'),
    ]

    operations = [
        migrations.AddField(
            model_name='tile',
            name='player',
            field=models.CharField(default=None, max_length=30),
            preserve_default=False,
        ),
    ]