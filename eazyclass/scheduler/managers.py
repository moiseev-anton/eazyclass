import logging
from typing import Dict, Optional, Tuple, Any

from django.contrib.auth.models import BaseUserManager
from django.db import models

from .utils import cache_data, invalidate_cache

CACHE_TIMEOUT = 86400  # 24 часа
USER_DATA_CACHE_TIMEOUT = 3600  # 1 час
KEYBOARD_DATA_CACHE_TIMEOUT = 82800  # 23 часа
GROUP_DATA_CACHE_TIMEOUT = 82800  # 23 часа

logger = logging.getLogger(__name__)


class SingleFieldManagerMixin:
    """ Миксин для сущностей с одним уникальным полем"""

    def get_objects_map(self, values_set, field_name):
        """
        Получить маппинг значений из БД: {значение поля -> id}.
        """
        existing_objects = self.filter(**{f"{field_name}__in": values_set}).values_list(field_name, 'id')
        return dict(existing_objects)

    def get_or_create_objects_map(self, unique_values_set, field_name):
        """
        Получить маппинг существующих объектов и создать недостающие.
        """
        objects_map = self.get_objects_map(unique_values_set, field_name)

        # Определяем недостающие значения
        missing_values = unique_values_set - set(objects_map.keys())
        if missing_values:
            logger.info(f"Создано {len(missing_values)} новых записей '{self.model.__name__}'")
            self.bulk_create([self.model(**{field_name: value}) for value in missing_values])

            # Обновляем маппинг
            objects_map.update(self.get_objects_map(missing_values, field_name))

        return objects_map


class BaseManager(models.Manager):
    def active_keyboard_data(self):
        raise NotImplementedError("Subclasses must implement fetch_active_data method")

    def get_or_create_cached_id(self):
        raise NotImplementedError("Subclasses must implement fetch_active_data method")


class GroupManager(BaseManager):
    def active_keyboard_data(self):
        return (self.filter(is_active=True).values('id', 'title', 'grade', 'faculty__short_title')
                .order_by('faculty__short_title', 'grade', 'title'))

    @cache_data('group_links', GROUP_DATA_CACHE_TIMEOUT, 'default')
    def groups_links(self):
        return self.filter(is_active=True).values('id', 'link')


class TeacherManager(BaseManager, SingleFieldManagerMixin):
    def active_keyboard_data(self):
        return self.filter(is_active=True).values('id', 'short_name').order_by('short_name')

    @cache_data("teacher:{full_name}", timeout=CACHE_TIMEOUT)
    def get_or_create_cached_id(self, full_name: str) -> int:
        obj, created = self.get_or_create(full_name=full_name)
        return obj.id


    # TODO: НАверно этот метод должен называться одинаково с подобными в остальных сущностях чтобы обеспечить LSP!!!
    def get_or_create_teacher_map(self, unique_teachers_set):
        return self.get_or_create_objects_map(unique_teachers_set, 'full_name')


class ClassroomManager(BaseManager, SingleFieldManagerMixin):
    @cache_data("classroom:{title}", timeout=CACHE_TIMEOUT)
    def get_or_create_cached_id(self, title: str) -> int:
        obj, created = self.get_or_create(title=title)
        return obj.id

    def get_or_create_classroom_map(self, unique_classroom_set):
        return self.get_or_create_objects_map(unique_classroom_set, 'title')


class SubjectManager(BaseManager):
    @cache_data("subject:{title}", timeout=CACHE_TIMEOUT)
    def get_or_create_cached_id(self, title: str) -> int:
        obj, created = self.get_or_create(title=title)
        return obj.id

    def get_or_create_subject_map(self, unique_subject_set):
        return self.get_or_create_objects_map(unique_subject_set, 'title')


class LessonTimeManager(BaseManager):
    @staticmethod
    @cache_data("lesson_time:{date_str}{lesson_number}", timeout=CACHE_TIMEOUT)
    def get_or_create_cached_id(self, date, lesson_number: str) -> int:
        obj, created = self.get_or_create(date=date, lesson_number=lesson_number)
        return obj.id

    def get_lesson_times_map(self, lesson_times_set):
        """
        Возвращает словарь {(date, lesson_number): id} для существующих записей.
        Принимает множество кортежей вида {(date_str, lesson_number)}.
        """
        # Выполняем запрос в БД на получение кортежей (date, lesson_number, id)
        # Создаем список условий для фильтрации
        filters = models.Q()
        for date, lesson_number in lesson_times_set:
            filters |= models.Q(date=date, lesson_number=lesson_number)

        # Применяем фильтры
        existing_lesson_times = self.filter(filters).values_list("date", "lesson_number", "id")
        return {(date, lesson_number): lesson_time_id for date, lesson_number, lesson_time_id in existing_lesson_times}

    def get_or_create_lesson_times_map(self, unique_lesson_times):
        """
        Возвращает словарь {(date, lesson_number): id}, создавая недостающие записи.
        Принимает множество кортежей вида {(date_str, lesson_number)}.
        """
        # Получаем существующие записи
        lesson_times_map = self.get_lesson_times_map(unique_lesson_times)

        # Определяем недостающие элементы
        missing_lesson_times = unique_lesson_times - set(lesson_times_map.keys())
        if missing_lesson_times:
            logger.info(f"Создано {len(missing_lesson_times)} новых записей Lesson_times")
            self.bulk_create([
                self.model(date=date, lesson_number=lesson_number)
                for date, lesson_number in missing_lesson_times
            ])

            # Обновляем словарь с добавленными объектами
            lesson_times_map.update(self.get_lesson_times_map(missing_lesson_times))

        return lesson_times_map


class SubscriptionManager(models.Manager):
    def invalidate_all_subscriptions(self, user_id: int):
        self.filter(user_id=user_id).delete()


class UserManager(BaseUserManager):
    @cache_data('user_data_{telegram_id}', timeout=USER_DATA_CACHE_TIMEOUT, cache_name='telegrambot_cache')
    def get_user_data_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        user = self.filter(telegram_id=telegram_id).first()
        if user is None:
            logger.warning(f'Пользователь с telegram_id {telegram_id} не найден.')
            return None
        logger.info(f'Получены данные пользователя с telegram_id {telegram_id} из БД.')
        return user.to_dict()

    @invalidate_cache('user_data_{0}', cache_name='telegrambot_cache')
    def update_contact(self, telegram_id: str, contact) -> 'User':
        user, created = self.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'phone_number': contact.phone_number,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
            }
        )

        return user

    def reset_subgroup(self, user_id: int):
        self.filter(id=user_id).update(subgroup='0')

    def get_or_create_by_telegram_user(self, telegram_user) -> Tuple['User', bool]:
        try:
            user, created = self.get_or_create(
                telegram_id=telegram_user.id,
                defaults={
                    'first_name': telegram_user.first_name or '',
                    'last_name': telegram_user.last_name or '',
                    'is_active': True
                }
            )
            if created:
                logger.info(f"Создан новый пользователь Telegram: {user.username} (ID: {user.id})")
            else:
                logger.info(f"Пользователь Telegram найден: {user.username} (ID: {user.id})")
            return user, created
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя через Telegram: {e}")
            raise

    @invalidate_cache('user_data_{0}', cache_name='telegrambot_cache')
    def update_contact(self, telegram_id: int, contact) -> Optional['User']:
        user = self.filter(telegram_id=telegram_id).first()
        if user:
            user.phone = contact.phone_number
            user.first_name = contact.first_name or user.first_name
            user.last_name = contact.last_name or user.last_name
            user.save(update_fields=['phone', 'first_name', 'last_name'])
            logger.info(f"Контактные данные обновлены для пользователя Telegram ID {telegram_id}.")
            return user
        logger.warning(f'Не найден пользователь для обновления контактов по telegram_id {telegram_id}.')
        return None

    @invalidate_cache('user_data_{0}', cache_name='telegrambot_cache')
    def reset_subgroup(self, user_id: int) -> int:
        updated_count = self.filter(id=user_id).update(subgroup='0')
        logger.debug(f"Сброшена подгруппа для пользователя с ID {user_id}")
        return updated_count

    def create_user(self, username: str, password: Optional[str] = None, **extra_fields) -> 'User':
        if not username:
            raise ValueError('Имя пользователя (username) обязательно для создания учетной записи')

        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        logger.info(f"Создан новый пользователь: {user.username} (ID: {user.id})")
        return user

    def create_superuser(self, username: str, password: str, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(username, password, **extra_fields)