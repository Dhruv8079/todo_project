// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const toggleDarkMode = () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    };
    
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode')) {
        document.body.classList.add('dark-mode');
    }
    
    // Add click listener to dark mode toggle button
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});