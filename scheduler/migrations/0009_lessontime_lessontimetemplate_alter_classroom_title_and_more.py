# Generated by Django 5.0.4 on 2024-05-15 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('scheduler', '0008_lesson_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('lesson_number', models.IntegerField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='LessonTimeTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(
                    choices=[('Monday', 'Понедельник'), ('Tuesday', 'Вторник'), ('Wednesday', 'Среда'),
                             ('Thursday', 'Четверг'), ('Friday', 'Пятница'), ('Saturday', 'Суббота')], max_length=10)),
                ('lesson_number', models.IntegerField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='classroom',
            name='title',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='subject',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='full_name',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
