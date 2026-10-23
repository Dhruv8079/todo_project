(function () {
    'use strict';

    const STORAGE_KEY = 'taskflow-theme';

    function currentTheme() {
        return document.documentElement.getAttribute('data-bs-theme') || 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);
        document.querySelectorAll('[data-theme-icon]').forEach(function (icon) {
            icon.classList.toggle('fa-moon', theme !== 'dark');
            icon.classList.toggle('fa-sun', theme === 'dark');
        });
    }

    window.toggleDarkMode = function () {
        applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
    };

    // Apply stored or system preference as early as possible
    const stored = localStorage.getItem(STORAGE_KEY);
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(stored || (prefersDark ? 'dark' : 'light'));

    document.addEventListener('DOMContentLoaded', function () {
        // Re-sync icons now that the DOM is ready
        applyTheme(currentTheme());

        // Bootstrap tooltips
        if (window.bootstrap && bootstrap.Tooltip) {
            document.querySelectorAll('[title]').forEach(function (el) {
                new bootstrap.Tooltip(el);
            });
        }

        // Auto-dismiss alerts after 5 seconds
        document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
            setTimeout(function () {
                if (window.bootstrap && bootstrap.Alert) {
                    bootstrap.Alert.getOrCreateInstance(alert).close();
                }
            }, 5000);
        });

        // Confirm destructive delete forms
        document.querySelectorAll('form[data-confirm]').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!window.confirm(form.getAttribute('data-confirm'))) {
                    event.preventDefault();
                }
            });
        });
    });
})();
