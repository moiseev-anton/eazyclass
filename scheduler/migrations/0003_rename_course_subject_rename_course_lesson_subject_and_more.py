# Generated by Django 5.0.4 on 2024-05-10 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0002_remove_group_id_faculty_remove_lesson_id_classroom_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Course',
            new_name='Subject',
        ),
        migrations.RenameField(
            model_name='lesson',
            old_name='course',
            new_name='subject',
        ),
        migrations.AddField(
            model_name='lesson',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
