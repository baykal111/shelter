// Global variables
let currentAnimalId = null;
let currentAnimalName = null;

// Scroll to search section
function scrollToSearch() {
    const searchSection = document.getElementById('search');
    if (searchSection) {
        searchSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Login Modal
function openLoginModal() {
    closeAllModals();
    document.getElementById('loginModal').classList.add('active');
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.remove('active');
}

function handleLogin(event) {
    // Django будет обрабатывать это на backend
    // Можно добавить клиентскую валидацию здесь
    const form = event.target;
    const email = form.querySelector('input[name="email"]').value;
    const password = form.querySelector('input[name="password"]').value;
    
    if (!email || !password) {
        event.preventDefault();
        showMessage('Пожалуйста, заполните все поля', 'error');
        return false;
    }
    
    // Форма отправится естественным путем на Django backend
}

// Register Modal
function openRegisterModal() {
    closeAllModals();
    document.getElementById('registerModal').classList.add('active');
}

function closeRegisterModal() {
    document.getElementById('registerModal').classList.remove('active');
}

function handleRegister(event) {
    const form = event.target;
    const password = form.querySelector('input[name="password"]').value;
    const passwordConfirm = form.querySelector('input[name="password_confirm"]').value;
    
    if (password !== passwordConfirm) {
        event.preventDefault();
        showMessage('Пароли не совпадают', 'error');
        return false;
    }
    
    if (password.length < 8) {
        event.preventDefault();
        showMessage('Пароль должен содержать минимум 8 символов', 'error');
        return false;
    }
    
    // Форма отправится на Django backend
}

// Reserve Modal
function openReserveModal(animalId, animalName) {
    closeAllModals();
    currentAnimalId = animalId;
    currentAnimalName = animalName;
    
    document.getElementById('reserveAnimalId').value = animalId;
    document.getElementById('reserveAnimalName').value = animalName;
    
    // Установка минимальной даты на сегодня
    const dateInput = document.querySelector('#reserveModal input[name="visit_date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);
    
    document.getElementById('reserveModal').classList.add('active');
}

function closeReserveModal() {
    document.getElementById('reserveModal').classList.remove('active');
    currentAnimalId = null;
    currentAnimalName = null;
}

function handleReservation(event) {
    const form = event.target;
    const visitDate = form.querySelector('input[name="visit_date"]').value;
    const today = new Date().toISOString().split('T')[0];
    
    if (visitDate < today) {
        event.preventDefault();
        showMessage('Дата посещения не может быть в прошлом', 'error');
        return false;
    }
    
    // Показываем индикатор загрузки (опционально)
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Отправка...';
    submitBtn.disabled = true;
    
    // Форма отправится на Django backend
    // После успешной отправки Django должен вернуть сообщение через messages framework
}

// Support Modal
function openSupportModal() {
    closeAllModals();
    document.getElementById('supportModal').classList.add('active');
}

function closeSupportModal() {
    document.getElementById('supportModal').classList.remove('active');
}

function handleSupport(event) {
    const form = event.target;
    const message = form.querySelector('textarea[name="message"]').value;
    
    if (message.length < 10) {
        event.preventDefault();
        showMessage('Сообщение слишком короткое. Минимум 10 символов', 'error');
        return false;
    }
    
    // Форма отправится на Django backend
}

// Close all modals
function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.classList.remove('active');
    });
}

// Close modal on outside click
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        closeAllModals();
    }
});

// Close modal on ESC key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeAllModals();
    }
});

// Show message/notification
function showMessage(text, type = 'info') {
    const messagesContainer = document.getElementById('messages') || createMessagesContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = text;
    
    messagesContainer.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'slideInRight 0.3s reverse';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.id = 'messages';
    document.body.appendChild(container);
    return container;
}

// Phone number formatting
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 0) {
        if (value[0] === '7' || value[0] === '8') {
            value = '7' + value.substring(1);
        } else if (value[0] !== '7') {
            value = '7' + value;
        }
        
        let formattedValue = '+7';
        if (value.length > 1) {
            formattedValue += ' (' + value.substring(1, 4);
        }
        if (value.length >= 5) {
            formattedValue += ') ' + value.substring(4, 7);
        }
        if (value.length >= 8) {
            formattedValue += '-' + value.substring(7, 9);
        }
        if (value.length >= 10) {
            formattedValue += '-' + value.substring(9, 11);
        }
        
        input.value = formattedValue;
    }
}

// Add phone formatting to all phone inputs
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    });
    
    // Auto-hide messages after page load
    setTimeout(() => {
        const messages = document.querySelectorAll('#messages .alert');
        messages.forEach(msg => {
            msg.style.animation = 'slideInRight 0.3s reverse';
            setTimeout(() => msg.remove(), 300);
        });
    }, 5000);
});

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const digits = phone.replace(/\D/g, '');
    return digits.length === 11;
}

// Search form enhancement
const searchForm = document.getElementById('searchForm');
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        // Можно добавить дополнительную валидацию или AJAX запрос
        // Django обработает это естественным путем
    });
}

// Image lazy loading
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.animal-image img');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe animal cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.animal-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        observer.observe(card);
    });
});

// Prevent form double submission
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            setTimeout(() => {
                submitBtn.disabled = false;
            }, 3000);
        }
    });
});

// CSRF Token helper for AJAX requests (если понадобится)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Example AJAX request with CSRF token
function sendAjaxRequest(url, data, method = 'POST') {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error:', error);
        showMessage('Произошла ошибка. Попробуйте позже', 'error');
    });
}

// Export functions for global use
window.shelterApp = {
    openLoginModal,
    closeLoginModal,
    openRegisterModal,
    closeRegisterModal,
    openReserveModal,
    closeReserveModal,
    openSupportModal,
    closeSupportModal,
    showMessage,
    sendAjaxRequest,
    scrollToSearch
};
