# Generated by Django 2.0 on 2018-03-30 03:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_blog_read_nums'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='read_nums',
        ),
    ]
