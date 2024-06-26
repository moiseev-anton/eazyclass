# Generated by Django 5.0.4 on 2024-05-07 02:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Date',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('short_title', models.CharField(max_length=15)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=30)),
                ('short_name', models.CharField(max_length=30)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('link', models.CharField(max_length=25)),
                ('grade', models.CharField(max_length=1)),
                ('is_active', models.BooleanField(default=True)),
                ('id_faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.faculty')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_number', models.CharField(max_length=1)),
                ('subgroup', models.CharField(max_length=1)),
                ('is_active', models.BooleanField(default=True)),
                ('id_classroom',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.classroom')),
                ('id_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.course')),
                ('id_date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.date')),
                ('id_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.group')),
                ('id_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(unique=True)),
                ('user_name', models.CharField(max_length=32)),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('phone_number', models.CharField(max_length=15)),
                ('subgroup', models.CharField(max_length=1)),
                ('is_active', models.BooleanField(default=True)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('id_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.group')),
            ],
        ),
    ]
