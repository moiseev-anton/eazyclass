# Generated by Django 5.0.4 on 2024-05-11 00:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0006_alter_lesson_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='date',
        ),
    ]
