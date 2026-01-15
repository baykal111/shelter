from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

from .models import Animal, Reservation, SupportRequest, Adoption, Donation, CustomUser
from .forms import (
    RegistrationForm, LoginForm, ReservationForm, 
    SupportRequestForm, ProfileUpdateForm
)


def home(request):
    """Главная страница"""
    # Получаем последних добавленных животных
    animals = Animal.objects.filter(status='available').order_by('-created_at')[:6]
    
    context = {
        'animals': animals,
    }
    return render(request, 'shelter/index.html', context)


def animals_list(request):
    """Список всех животных с фильтрацией"""
    animals = Animal.objects.filter(status='available')
    
    # Фильтрация
    animal_type = request.GET.get('animal_type')
    age = request.GET.get('age')
    gender = request.GET.get('gender')
    size = request.GET.get('size')
    search = request.GET.get('search')
    
    if animal_type:
        animals = animals.filter(animal_type=animal_type)
    if age:
        animals = animals.filter(age=age)
    if gender:
        animals = animals.filter(gender=gender)
    if size:
        animals = animals.filter(size=size)
    if search:
        animals = animals.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(breed__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(animals, 12)  # 12 животных на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'animals': page_obj,
        'filters': {
            'animal_type': animal_type,
            'age': age,
            'gender': gender,
            'size': size,
            'search': search,
        }
    }
    return render(request, 'shelter/animals_list.html', context)


def animal_detail(request, pk):
    """Детальная страница животного"""
    animal = get_object_or_404(Animal, pk=pk)
    
    # Похожие животные
    similar_animals = Animal.objects.filter(
        animal_type=animal.animal_type,
        status='available'
    ).exclude(pk=pk)[:4]
    
    context = {
        'animal': animal,
        'similar_animals': similar_animals,
    }
    return render(request, 'shelter/animal_detail.html', context)


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Автоматический вход после регистрации
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegistrationForm()
    
    return render(request, 'shelter/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email или пароль')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
    
    return redirect('home')


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')


@login_required
def profile(request):
    """Профиль пользователя"""
    user = request.user
    reservations = Reservation.objects.filter(user=user).order_by('-created_at')
    adoptions = Adoption.objects.filter(user=user).order_by('-created_at')
    donations = Donation.objects.filter(user=user).order_by('-created_at')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен успешно!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'reservations': reservations,
        'adoptions': adoptions,
        'donations': donations,
    }
    return render(request, 'shelter/profile.html', context)


@require_POST
def create_reservation(request):
    """Создание бронирования"""
    animal_id = request.POST.get('animal_id')
    animal = get_object_or_404(Animal, pk=animal_id)
    
    # Проверка доступности животного
    if animal.status != 'available':
        messages.error(request, 'К сожалению, это животное уже недоступно для бронирования')
        return redirect('animal_detail', pk=animal_id)
    
    # Проверка даты
    visit_date_str = request.POST.get('visit_date')
    try:
        visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
        if visit_date < datetime.now().date():
            messages.error(request, 'Дата посещения не может быть в прошлом')
            return redirect('animal_detail', pk=animal_id)
    except ValueError:
        messages.error(request, 'Неверный формат даты')
        return redirect('animal_detail', pk=animal_id)
    
    # Создание бронирования
    reservation = Reservation.objects.create(
        animal=animal,
        user=request.user if request.user.is_authenticated else None,
        name=request.POST.get('name'),
        phone=request.POST.get('phone'),
        email=request.POST.get('email'),
        visit_date=visit_date,
        comment=request.POST.get('comment', '')
    )
    
    # Обновление статуса животного
    animal.status = 'reserved'
    animal.save()
    
    messages.success(
        request, 
        f'Ваша заявка на встречу с {animal.name} успешно отправлена! '
        'Мы свяжемся с вами в ближайшее время.'
    )
    
    return redirect('animal_detail', pk=animal_id)


@require_POST
def support_request(request):
    """Создание обращения в поддержку"""
    support_req = SupportRequest.objects.create(
        user=request.user if request.user.is_authenticated else None,
        name=request.POST.get('name'),
        email=request.POST.get('email'),
        subject=request.POST.get('subject'),
        message=request.POST.get('message')
    )
    
    messages.success(
        request,
        'Ваше обращение успешно отправлено! Мы ответим вам в ближайшее время.'
    )
    
    return redirect('home')


def about(request):
    """Страница о приюте"""
    # Статистика
    total_animals = Animal.objects.count()
    adopted_animals = Animal.objects.filter(status='adopted').count()
    available_animals = Animal.objects.filter(status='available').count()
    
    context = {
        'total_animals': total_animals,
        'adopted_animals': adopted_animals,
        'available_animals': available_animals,
    }
    return render(request, 'shelter/about.html', context)


def contact(request):
    """Страница контактов"""
    return render(request, 'shelter/contact.html')


def help_page(request):
    """Страница помощи приюту"""
    return render(request, 'shelter/help.html')


def donations_page(request):
    """Страница пожертвований"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        message = request.POST.get('message', '')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        donation = Donation.objects.create(
            user=request.user if request.user.is_authenticated and not is_anonymous else None,
            name=request.POST.get('name') if not is_anonymous else '',
            email=request.POST.get('email') if not is_anonymous else '',
            amount=amount,
            message=message,
            is_anonymous=is_anonymous,
            payment_status='pending'
        )
        
        # Здесь должна быть интеграция с платежной системой
        # Например: Yookassa, Stripe, PayPal и т.д.
        
        messages.success(request, 'Спасибо за вашу поддержку!')
        return redirect('donations')
    
    # Топ доноров
    top_donors = Donation.objects.filter(
        payment_status='completed',
        is_anonymous=False
    ).exclude(user=None).values('user__first_name', 'user__last_name').distinct()[:10]
    
    context = {
        'top_donors': top_donors,
    }
    return render(request, 'shelter/donations.html', context)


def volunteer_page(request):
    """Страница волонтерства"""
    return render(request, 'shelter/volunteer.html')


def faq_page(request):
    """Страница FAQ"""
    return render(request, 'shelter/faq.html')


def adoption_guide(request):
    """Руководство по усыновлению"""
    return render(request, 'shelter/adoption_guide.html')


def terms(request):
    """Условия использования"""
    return render(request, 'shelter/terms.html')


def privacy(request):
    """Политика конфиденциальности"""
    return render(request, 'shelter/privacy.html')


# API endpoints для AJAX запросов
def api_check_availability(request, animal_id):
    """Проверка доступности животного"""
    animal = get_object_or_404(Animal, pk=animal_id)
    
    return JsonResponse({
        'available': animal.status == 'available',
        'status': animal.get_status_display()
    })


@login_required
def api_cancel_reservation(request, reservation_id):
    """Отмена бронирования"""
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)
        
        # Обновляем статус животного
        animal = reservation.animal
        animal.status = 'available'
        animal.save()
        
        # Отменяем бронирование
        reservation.status = 'cancelled'
        reservation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Бронирование отменено'
        })
    
    return JsonResponse({'success': False}, status=400)
    
