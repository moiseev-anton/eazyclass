# Generated by Django 5.0.4 on 2024-05-11 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0007_remove_lesson_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='date',
            field=models.DateField(null=True),
        ),
    ]