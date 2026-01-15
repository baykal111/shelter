from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Расширенная модель пользователя"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр."
    )
    
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name='Телефон'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Адрес'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Подтвержден'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.username


class Animal(models.Model):
    """Модель животного"""
    ANIMAL_TYPES = [
        ('dog', 'Собака'),
        ('cat', 'Кошка'),
        ('other', 'Другое'),
    ]

    AGE_CHOICES = [
        ('young', 'До 1 года'),
        ('adult', '1-7 лет'),
        ('senior', 'Старше 7 лет'),
    ]

    GENDER_CHOICES = [
        ('male', 'Самец'),
        ('female', 'Самка'),
    ]

    SIZE_CHOICES = [
        ('small', 'Маленький'),
        ('medium', 'Средний'),
        ('large', 'Крупный'),
    ]

    STATUS_CHOICES = [
        ('available', 'В приюте'),
        ('reserved', 'Забронирован'),
        ('adopted', 'Усыновлен'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    animal_type = models.CharField(
        max_length=10,
        choices=ANIMAL_TYPES,
        verbose_name='Тип животного'
    )
    breed = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Порода'
    )
    age = models.CharField(
        max_length=10,
        choices=AGE_CHOICES,
        verbose_name='Возраст'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name='Пол'
    )
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        verbose_name='Размер'
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Окрас'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    health_status = models.TextField(
        blank=True,
        verbose_name='Состояние здоровья'
    )
    photo = models.ImageField(
        upload_to='animals/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Статус'
    )
    arrival_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата поступления'
    )
    vaccinated = models.BooleanField(
        default=False,
        verbose_name='Привит'
    )
    sterilized = models.BooleanField(
        default=False,
        verbose_name='Стерилизован'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Животное'
        verbose_name_plural = 'Животные'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_animal_type_display()})"

    def get_emoji(self):
        """Возвращает эмодзи для типа животного"""
        emoji_map = {
            'dog': '🐕',
            'cat': '🐱',
            'other': '🐾',
        }
        return emoji_map.get(self.animal_type, '🐾')


class Reservation(models.Model):
    """Модель бронирования встречи"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Животное'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reservations',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    phone = models.CharField(
        max_length=17,
        verbose_name='Телефон'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    visit_date = models.DateField(
        verbose_name='Дата посещения'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронь: {self.name} - {self.animal.name} ({self.visit_date})"


class SupportRequest(models.Model):
    """Модель обращения в поддержку"""
    SUBJECT_CHOICES = [
        ('adoption', 'Вопрос об усыновлении'),
        ('volunteer', 'Волонтерство'),
        ('donation', 'Пожертвования'),
        ('technical', 'Технические проблемы'),
        ('other', 'Другое'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('in_progress', 'В обработке'),
        ('resolved', 'Решено'),
        ('closed', 'Закрыто'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='support_requests',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES,
        verbose_name='Тема'
    )
    message = models.TextField(
        verbose_name='Сообщение'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    response = models.TextField(
        blank=True,
        verbose_name='Ответ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Обращение в поддержку'
        verbose_name_plural = 'Обращения в поддержку'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_subject_display()} - {self.name}"


class Adoption(models.Model):
    """Модель усыновления"""
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('completed', 'Завершено'),
    ]

    animal = models.OneToOneField(
        Animal,
        on_delete=models.CASCADE,
        related_name='adoption',
        verbose_name='Животное'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='adoptions',
        verbose_name='Усыновитель'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    adoption_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата усыновления'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Примечания'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Усыновление'
        verbose_name_plural = 'Усыновления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} усыновляет {self.animal.name}"


class Donation(models.Model):
    """Модель пожертвования"""
    PAYMENT_STATUS = [
        ('pending', 'Ожидает оплаты'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возвращено'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name='donations',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Имя донора'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма'
    )
    message = models.TextField(
        blank=True,
        verbose_name='Сообщение'
    )
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name='Анонимно'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name='Статус платежа'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID транзакции'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Пожертвование'
        verbose_name_plural = 'Пожертвования'
        ordering = ['-created_at']

    def __str__(self):
        donor = self.name or self.user.get_full_name() if self.user else 'Аноним'
        return f"{donor} - {self.amount} руб."
