// Modern Healthcare JavaScript - Dynamic & Interactive Components

class HealthcareApp {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.initializeComponents();
    }

    init() {
        // Initialize the application
        console.log('Healthcare App Initialized');
        this.addLoadingStates();
        this.setupAnimations();
        this.initializeNotifications();
    }

    setupEventListeners() {
        // Form submissions
        document.addEventListener('DOMContentLoaded', () => {
            this.setupFormHandlers();
            this.setupNavigation();
            this.setupModals();
            this.setupTooltips();
            this.setupProgressBars();
        });

        // Window events
        window.addEventListener('scroll', this.handleScroll.bind(this));
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    initializeComponents() {
        this.setupAppointmentCards();
        this.setupHealthStats();
        this.setupVirtualConsultation();
        this.setupSearchFunctionality();
    }

    // Animation System
    setupAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.modern-card, .stat-card, .appointment-card').forEach(el => {
            observer.observe(el);
        });
    }

    // Loading States
    addLoadingStates() {
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(element => {
            element.classList.add('loading');
        });
    }

    // Form Handling
    setupFormHandlers() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // Real-time form validation
        const inputs = document.querySelectorAll('.form-control-modern');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateField.bind(this));
            input.addEventListener('input', this.clearFieldError.bind(this));
        });
    }

    handleFormSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }

        // Add loading state to form
        form.classList.add('loading');
    }

    validateField(event) {
        const field = event.target;
        const value = field.value.trim();
        const fieldName = field.name;
        
        // Remove existing error
        this.clearFieldError(event);
        
        // Validation rules
        const validations = {
            'patient': value.length >= 2,
            'doctor': value.length >= 2,
            'time': value.length > 0,
            'email': /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            'phone': /^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/\s/g, ''))
        };

        if (validations[fieldName] === false) {
            this.showFieldError(field, this.getErrorMessage(fieldName));
        }
    }

    clearFieldError(event) {
        const field = event.target;
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
        field.classList.remove('error');
    }

    showFieldError(field, message) {
        field.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error alert-danger-modern';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    getErrorMessage(fieldName) {
        const messages = {
            'patient': 'Patient name must be at least 2 characters',
            'doctor': 'Doctor name must be at least 2 characters',
            'time': 'Please select a valid time',
            'email': 'Please enter a valid email address',
            'phone': 'Please enter a valid phone number'
        };
        return messages[fieldName] || 'This field is required';
    }

    // Navigation
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Mobile menu toggle
        const mobileMenuBtn = document.querySelector('.navbar-toggler');
        const mobileMenu = document.querySelector('.navbar-collapse');
        
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('show');
            });
        }
    }

    // Modal System
    setupModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        const modals = document.querySelectorAll('.modal');

        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });

        // Close modal on backdrop click
        modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });

        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            setTimeout(() => modal.classList.add('show'), 10);
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 300);
    }

    closeAllModals() {
        document.querySelectorAll('.modal.show').forEach(modal => {
            this.closeModal(modal);
        });
    }

    // Tooltip System
    setupTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    }

    showTooltip(event) {
        const element = event.target;
        const tooltipText = element.getAttribute('data-tooltip');
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
    }

    hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    // Progress Bars
    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-modern');
        
        progressBars.forEach(bar => {
            const progressBar = bar.querySelector('.progress-bar-modern');
            if (progressBar) {
                const progress = progressBar.getAttribute('data-progress') || 0;
                setTimeout(() => {
                    progressBar.style.width = progress + '%';
                }, 500);
            }
        });
    }

    // Appointment Cards
    setupAppointmentCards() {
        const appointmentCards = document.querySelectorAll('.appointment-card');
        
        appointmentCards.forEach(card => {
            // Add click handler for appointment details
            card.addEventListener('click', () => {
                const appointmentId = card.getAttribute('data-appointment-id');
                if (appointmentId) {
                    this.showAppointmentDetails(appointmentId);
                }
            });

            // Add status indicators
            const status = card.getAttribute('data-status');
            if (status) {
                this.updateAppointmentStatus(card, status);
            }
        });
    }

    showAppointmentDetails(appointmentId) {
        // Implementation for showing appointment details
        console.log('Showing details for appointment:', appointmentId);
        this.showNotification('Appointment details loaded', 'success');
    }

    updateAppointmentStatus(card, status) {
        const statusElement = card.querySelector('.appointment-status');
        if (statusElement) {
            statusElement.className = `appointment-status status-${status}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    // Health Statistics
    setupHealthStats() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-target') || stat.textContent);
            const duration = 2000; // 2 seconds
            const increment = target / (duration / 16); // 60fps
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                stat.textContent = Math.floor(current).toLocaleString();
            }, 16);
        });
    }

    // Virtual Consultation
    setupVirtualConsultation() {
        const consultationBtn = document.querySelector('.virtual-consultation-btn');
        if (consultationBtn) {
            consultationBtn.addEventListener('click', () => {
                this.startVirtualConsultation();
            });
        }
    }

    startVirtualConsultation() {
        // Check if user has camera and microphone permissions
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(stream => {
                this.showNotification('Virtual consultation started', 'success');
                // Handle stream for video consultation
            })
            .catch(error => {
                this.showNotification('Camera/microphone access denied', 'error');
            });
    }

    // Search Functionality
    setupSearchFunctionality() {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearch.bind(this));
        }
    }

    handleSearch(event) {
        const query = event.target.value.toLowerCase();
        const searchableElements = document.querySelectorAll('[data-search]');
        
        searchableElements.forEach(element => {
            const searchText = element.getAttribute('data-search').toLowerCase();
            if (searchText.includes(query)) {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        });
    }

    // Notification System
    initializeNotifications() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove after duration
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Scroll Handling
    handleScroll() {
        const scrollTop = window.pageYOffset;
        const header = document.querySelector('.modern-header');
        
        if (header) {
            if (scrollTop > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }

        // Parallax effect for hero section
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        }
    }

    // Resize Handling
    handleResize() {
        // Handle responsive behavior
        const width = window.innerWidth;
        
        if (width < 768) {
            document.body.classList.add('mobile');
        } else {
            document.body.classList.remove('mobile');
        }
    }

    // Utility Functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // API Helper
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            this.showNotification('Request failed. Please try again.', 'error');
            throw error;
        }
    }

    // Local Storage Helper
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    }

    getLocalStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Failed to read from localStorage:', error);
            return null;
        }
    }

    // Theme Management
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.setLocalStorage('theme', theme);
    }

    getTheme() {
        return this.getLocalStorage('theme') || 'light';
    }

    toggleTheme() {
        const currentTheme = this.getTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.healthcareApp = new HealthcareApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HealthcareApp;
} 