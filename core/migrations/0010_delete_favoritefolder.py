# Generated by Django 2.2.2 on 2019-06-27 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_favoritefolder'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FavoriteFolder',
        ),
    ]