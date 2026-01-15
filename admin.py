from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser, Animal, Reservation, 
    SupportRequest, Adoption, Donation
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админка для пользователей"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_verified', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_verified', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'avatar', 'date_of_birth', 'address', 'is_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'phone', 'first_name', 'last_name')
        }),
    )


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    """Админка для животных"""
    list_display = [
        'name', 'animal_type', 'breed', 'age', 'gender', 
        'size', 'status', 'photo_preview', 'created_at'
    ]
    list_filter = ['animal_type', 'age', 'gender', 'size', 'status', 'vaccinated', 'sterilized']
    search_fields = ['name', 'breed', 'description']
    ordering = ['-created_at']
    readonly_fields = ['photo_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'animal_type', 'breed', 'age', 'gender', 'size', 'color')
        }),
        ('Описание и здоровье', {
            'fields': ('description', 'health_status', 'vaccinated', 'sterilized')
        }),
        ('Фото', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Статус и даты', {
            'fields': ('status', 'arrival_date', 'created_at', 'updated_at')
        }),
    )
    
    def photo_preview(self, obj):
        """Превью фото в админке"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.photo.url
            )
        return format_html('<span>{}</span>', obj.get_emoji())
    
    photo_preview.short_description = 'Превью'
    
    actions = ['mark_as_available', 'mark_as_adopted']
    
    def mark_as_available(self, request, queryset):
        """Пометить как доступных"""
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} животных помечены как доступные')
    mark_as_available.short_description = 'Пометить как доступных'
    
    def mark_as_adopted(self, request, queryset):
        """Пометить как усыновленных"""
        updated = queryset.update(status='adopted')
        self.message_user(request, f'{updated} животных помечены как усыновленные')
    mark_as_adopted.short_description = 'Пометить как усыновленных'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Админка для бронирований"""
    list_display = [
        'id', 'animal', 'name', 'phone', 'email', 
        'visit_date', 'status', 'created_at'
    ]
    list_filter = ['status', 'visit_date', 'created_at']
    search_fields = ['name', 'phone', 'email', 'animal__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Информация о животном', {
            'fields': ('animal',)
        }),
        ('Контактные данные', {
            'fields': ('user', 'name', 'phone', 'email')
        }),
        ('Детали встречи', {
            'fields': ('visit_date', 'comment', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['confirm_reservation', 'cancel_reservation']
    
    def confirm_reservation(self, request, queryset):
        """Подтвердить бронирование"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} бронирований подтверждено')
    confirm_reservation.short_description = 'Подтвердить бронирование'
    
    def cancel_reservation(self, request, queryset):
        """Отменить бронирование"""
        updated = queryset.update(status='cancelled')
        # Вернуть животных в статус "доступно"
        for reservation in queryset:
            reservation.animal.status = 'available'
            reservation.animal.save()
        self.message_user(request, f'{updated} бронирований отменено')
    cancel_reservation.short_description = 'Отменить бронирование'


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    """Админка для обращений в поддержку"""
    list_display = [
        'id', 'name', 'email', 'subject', 
        'status', 'created_at'
    ]
    list_filter = ['subject', 'status', 'created_at']
    search_fields = ['name', 'email', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('user', 'name', 'email')
        }),
        ('Обращение', {
            'fields': ('subject', 'message', 'status')
        }),
        ('Ответ', {
            'fields': ('response',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_in_progress', 'mark_as_resolved']
    
    def mark_as_in_progress(self, request, queryset):
        """Пометить как в обработке"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} обращений помечены как "В обработке"')
    mark_as_in_progress.short_description = 'Пометить как "В обработке"'
    
    def mark_as_resolved(self, request, queryset):
        """Пометить как решенные"""
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} обращений помечены как "Решено"')
    mark_as_resolved.short_description = 'Пометить как "Решено"'


@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    """Админка для усыновлений"""
    list_display = [
        'id', 'animal', 'user', 'status', 
        'adoption_date', 'created_at'
    ]
    list_filter = ['status', 'adoption_date', 'created_at']
    search_fields = ['animal__name', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('animal', 'user', 'status')
        }),
        ('Детали усыновления', {
            'fields': ('adoption_date', 'notes')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_adoption', 'reject_adoption']
    
    def approve_adoption(self, request, queryset):
        """Одобрить усыновление"""
        updated = queryset.update(status='approved')
        # Обновить статус животных
        for adoption in queryset:
            adoption.animal.status = 'adopted'
            adoption.animal.save()
        self.message_user(request, f'{updated} усыновлений одобрено')
    approve_adoption.short_description = 'Одобрить усыновление'
    
    def reject_adoption(self, request, queryset):
        """Отклонить усыновление"""
        updated = queryset.update(status='rejected')
        # Вернуть животных в статус "доступно"
        for adoption in queryset:
            adoption.animal.status = 'available'
            adoption.animal.save()
        self.message_user(request, f'{updated} усыновлений отклонено')
    reject_adoption.short_description = 'Отклонить усыновление'


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """Админка для пожертвований"""
    list_display = [
        'id', 'get_donor_name', 'amount', 'payment_status', 
        'is_anonymous', 'created_at'
    ]
    list_filter = ['payment_status', 'is_anonymous', 'created_at']
    search_fields = ['name', 'email', 'user__first_name', 'user__last_name', 'transaction_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Информация о доноре', {
            'fields': ('user', 'name', 'email', 'is_anonymous')
        }),
        ('Детали пожертвования', {
            'fields': ('amount', 'message', 'payment_status', 'transaction_id')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_donor_name(self, obj):
        """Получить имя донора"""
        if obj.is_anonymous:
            return 'Аноним'
        if obj.user:
            return obj.user.get_full_name()
        return obj.name
    get_donor_name.short_description = 'Донор'
    
    actions = ['mark_as_completed']
    
    def mark_as_completed(self, request, queryset):
        """Пометить как оплаченные"""
        updated = queryset.update(payment_status='completed')
        self.message_user(request, f'{updated} пожертвований помечены как оплаченные')
    mark_as_completed.short_description = 'Пометить как оплаченные'


# Настройка админ-панели
admin.site.site_header = 'Администрирование приюта "Верные друзья"'
admin.site.site_title = 'Админ-панель приюта'
admin.site.index_title = 'Добро пожаловать в панель управления'
