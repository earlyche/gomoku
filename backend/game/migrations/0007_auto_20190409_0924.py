# Generated by Django 2.1.7 on 2019-04-09 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_tile_player'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='captures_o',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='captures_x',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
