from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Subscribable(models.Model):
    def get_display_name(self):
        raise NotImplementedError("Subclasses must implement get_display_name method")

    def get_filter_params(self, subscription_id):
        raise NotImplementedError("Subclasses must implement get_filter_params method")

    class Meta:
        abstract = True


class Faculty(models.Model):
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=10, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def calculate_short_title(self):
        if not self.groups.exists():
            self.short_title = ''
        else:
            titles = [group.title.lstrip('0123456789-_ ') for group in self.groups.all()]
            result = titles[0]

            for title in titles[1:]:
                result = ''.join(t1 if t1 == t2 else '' for t1, t2 in zip(result, title)).rstrip('0123456789-_ ')

            self.short_title = result
            self.save(update_fields=['short_title'])

    def __str__(self):
        return f"{self.short_title}"

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['short_title']),  # для сортировки
        ]


class Group(Subscribable):
    title = models.CharField(max_length=255)
    link = models.URLField()
    faculty = models.ForeignKey(Faculty, related_name='groups', on_delete=models.CASCADE, null=True)
    grade = models.CharField(max_length=1)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    def get_display_name(self):
        return self.title

    def get_filter_params(self):
        return {'group_id': self.id}

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['grade', 'title']),  # для сортировки
        ]


class Teacher(Subscribable):
    full_name = models.CharField(max_length=64, unique=True)
    short_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.short_name}"

    def save(self, *args, **kwargs):
        if not self.short_name:
            self.short_name = self.generate_short_name()
        super().save(*args, **kwargs)

    def generate_short_name(self):
        full_name = str(self.full_name).strip()
        if full_name in ("не указано", ""):
            self.full_name = "не указано"
            return "не указано"

        names = full_name.split()
        short_name = names[0]  # Берем первый элемент полностью

        # Добавляем первые буквы второго и третьего элементов, если они есть
        if len(names) > 1:
            short_name += f" {names[1][0]}."
        if len(names) > 2:
            short_name += f"{names[2][0]}."

        return short_name

    def get_display_name(self):
        return self.short_name

    def get_filter_params(self):
        return {'teacher_id': self.id}


class Subject(models.Model):
    title = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Classroom(models.Model):
    title = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class LessonTime(models.Model):
    date = models.DateField()
    lesson_number = models.CharField(max_length=1)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)

    class Meta:
        unique_together = ('date', 'lesson_number')
        indexes = [
            models.Index(fields=['date', 'lesson_number']),
            models.Index(fields=['date']),
        ]

    def save(self, *args, **kwargs):
        if not self.start_time or not self.end_time:
            try:
                template = LessonTimeTemplate.objects.get(day_of_week=self.date.strftime('%A'),
                                                          lesson_number=self.lesson_number)
                self.start_time = template.start_time
                self.end_time = template.end_time
            except ObjectDoesNotExist:
                self.start_time = None
                self.end_time = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.lesson_number} пара"


class Lesson(models.Model):
    group = models.ForeignKey(Group, related_name='lessons', on_delete=models.CASCADE, null=True)
    lesson_time = models.ForeignKey(LessonTime, related_name='lessons', on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, related_name='lessons', on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, related_name='lessons', on_delete=models.CASCADE, null=True)
    classroom = models.ForeignKey(Classroom, related_name='lessons', on_delete=models.CASCADE, null=True)
    subgroup = models.CharField(max_length=1, default='0')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.group.title}({self.subgroup})-{self.lesson_time}-{self.subject}"

    class Meta:
        indexes = [
            models.Index(fields=['group', 'lesson_time']),
            models.Index(fields=['group', 'lesson_time', 'subgroup']),
        ]


class LessonBuffer(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    lesson_time = models.ForeignKey(LessonTime, on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True)
    subgroup = models.CharField(max_length=1, default='0')
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['group', 'lesson_time']),
            models.Index(fields=['group', 'lesson_time', 'subgroup']),
        ]

    def __str__(self):
        return f"{self.group.title}({self.subgroup})-{self.lesson_time}-{self.subject}"


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    user_name = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=15)
    subgroup = models.CharField(max_length=1, default='0')
    is_active = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    # Поля для подписки на расписание группы или учителя
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    subscription = GenericForeignKey('content_type', 'object_id')
    # Настройка уведомлений
    notify_on_schedule_change = models.BooleanField(default=True)
    notify_on_lesson_start = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user_name} ({self.first_name} {self.last_name}) [ID: {self.id}]"

    def get_subscription_info(self):
        """
        Возвращает информацию о подписке пользователя, если она есть.

        Returns:
            dict or None: Словарь с информацией о подписке или None, если подписка отсутствует.
        """
        if self.subscription:
            return {
                'type': self.content_type.model,
                'id': self.object_id,
                'name': self.subscription.get_display_name()
            }
        return None

    class Meta:
        indexes = [
            models.Index(fields=['telegram_id', 'is_active']),
        ]


class LessonTimeTemplate(models.Model):
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Понедельник'),
        ('Tuesday', 'Вторник'),
        ('Wednesday', 'Среда'),
        ('Thursday', 'Четверг'),
        ('Friday', 'Пятница'),
        ('Saturday', 'Суббота')
    ])
    lesson_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('day_of_week', 'lesson_number')

    def __str__(self):
        return f"{self.get_day_of_week_display()} - Пара {self.lesson_number}: {self.start_time} - {self.end_time}"
