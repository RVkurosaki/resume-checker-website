// Theme Switcher System
const themes = {
    'dark-purple': {
        name: 'Dark Purple',
        icon: '🟣',
        primary: '#6366f1',
        secondary: '#8b5cf6'
    },
    'ocean': {
        name: 'Ocean Blue',
        icon: '🔵',
        primary: '#06b6d4',
        secondary: '#14b8a6'
    },
    'sunset': {
        name: 'Sunset Orange',
        icon: '🟠',
        primary: '#f97316',
        secondary: '#ec4899'
    },
    'forest': {
        name: 'Forest Green',
        icon: '🟢',
        primary: '#10b981',
        secondary: '#059669'
    },
    'cyberpunk': {
        name: 'Cyberpunk',
        icon: '💗',
        primary: '#ec4899',
        secondary: '#06b6d4'
    }
};

// Get saved theme or default
const getSavedTheme = () => {
    return localStorage.getItem('theme') || 'dark-purple';
};

// Apply theme
const applyTheme = (themeName) => {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('theme', themeName);

    // Update active state in theme selector
    document.querySelectorAll('.theme-option').forEach(option => {
        option.classList.remove('active');
        if (option.dataset.theme === themeName) {
            option.classList.add('active');
        }
    });

    // Add transition overlay for smooth change
    const overlay = document.getElementById('theme-transition-overlay');
    if (overlay) {
        overlay.classList.add('active');
        setTimeout(() => {
            overlay.classList.remove('active');
        }, 300);
    }
};

// Toggle theme selector
const toggleThemeSelector = () => {
    const selector = document.getElementById('theme-selector');
    selector.classList.toggle('show');
};

// Close theme selector when clicking outside
document.addEventListener('click', (e) => {
    const selector = document.getElementById('theme-selector');
    const button = document.getElementById('theme-button');

    if (selector && button && !selector.contains(e.target) && !button.contains(e.target)) {
        selector.classList.remove('show');
    }
});

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = getSavedTheme();
    applyTheme(savedTheme);

    // Set up theme selector
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
        // Create theme options
        Object.keys(themes).forEach(themeKey => {
            const theme = themes[themeKey];
            const option = document.createElement('div');
            option.className = 'theme-option';
            option.dataset.theme = themeKey;
            if (themeKey === savedTheme) {
                option.classList.add('active');
            }

            option.innerHTML = `
                <div class="theme-preview">
                    <div class="theme-color" style="background: ${theme.primary}"></div>
                    <div class="theme-color" style="background: ${theme.secondary}"></div>
                </div>
                <div class="theme-info">
                    <span class="theme-icon">${theme.icon}</span>
                    <span class="theme-name">${theme.name}</span>
                </div>
            `;

            option.addEventListener('click', () => {
                applyTheme(themeKey);
                toggleThemeSelector();
            });

            themeSelector.appendChild(option);
        });
    }

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';

    // Add entrance animations to cards
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

    // Observe all cards
    document.querySelectorAll('.analysis-card, .score-card, .summary-card, .linkedin-rating-section').forEach(card => {
        card.classList.add('fade-in-ready');
        observer.observe(card);
    });
});

// Ripple effect on buttons
document.addEventListener('click', function (e) {
    const button = e.target.closest('button, .btn-primary, .btn-secondary');
    if (button) {
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');

        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';

        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }
});
