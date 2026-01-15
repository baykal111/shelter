from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Животные
    path('animals/', views.animals_list, name='animals_list'),
    path('animals/<int:pk>/', views.animal_detail, name='animal_detail'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Профиль
    path('profile/', views.profile, name='profile'),
    
    # Бронирование и заявки
    path('reservation/create/', views.create_reservation, name='create_reservation'),
    path('support/', views.support_request, name='support_request'),
    
    # Информационные страницы
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help_page, name='help'),
    path('donations/', views.donations_page, name='donations'),
    path('volunteer/', views.volunteer_page, name='volunteer'),
    path('faq/', views.faq_page, name='faq'),
    path('adoption-guide/', views.adoption_guide, name='adoption_guide'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Дополнительные страницы (заглушки)
    path('team/', views.about, name='team'),
    path('reports/', views.about, name='reports'),
    path('careers/', views.about, name='careers'),
    
    # API endpoints
    path('api/animal/<int:animal_id>/check/', views.api_check_availability, name='api_check_availability'),
    path('api/reservation/<int:reservation_id>/cancel/', views.api_cancel_reservation, name='api_cancel_reservation'),
]

# Добавляем возможность загрузки медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
