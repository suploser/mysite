# Generated by Django 2.0 on 2018-04-04 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0002_auto_20180404_1556'),
        ('blog', '0012_user_email'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
