// Main Application
class KoalaSearchApp {
    constructor() {
        this.init();
    }

    init() {
        // Initialize app when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.setupGlobalErrorHandling();
            this.setupServiceWorker();
            this.setupKeyboardShortcuts();
            this.checkBackendConnection();
        });
    }

    setupGlobalErrorHandling() {
        // Handle uncaught errors
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            if (window.toast) {
                window.toast.show('error', 'Application Error', 'An unexpected error occurred');
            }
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            if (window.toast) {
                window.toast.show('error', 'Network Error', 'Failed to connect to server');
            }
        });
    }

    setupServiceWorker() {
        // Register service worker for offline functionality (optional)
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('search-input');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Escape to clear search or close modals
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('search-input');
                if (searchInput && document.activeElement === searchInput) {
                    searchInput.blur();
                }
                
                // Close mobile menu if open
                if (window.navbar) {
                    window.navbar.closeMobileMenu();
                }
            }

            // Number keys to navigate pages
            if (e.altKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        window.location.hash = 'search';
                        break;
                    case '2':
                        e.preventDefault();
                        window.location.hash = 'websites';
                        break;
                    case '3':
                        e.preventDefault();
                        window.location.hash = 'analytics';
                        break;
                }
            }
        });
    }

    async checkBackendConnection() {
        try {
            await apiService.getStats();
            console.log('Backend connection established');
        } catch (error) {
            console.error('Backend connection failed:', error);
            if (window.toast) {
                window.toast.show('warning', 'Backend Offline', 'Cannot connect to search backend. Please ensure the server is running.');
            }
        }
    }
}

// Initialize the application
new KoalaSearchApp();

// Add some helpful global functions
window.KoalaSearch = {
    // Quick search function
    search: (query) => {
        window.location.hash = 'search';
        setTimeout(() => {
            const searchInput = document.getElementById('search-input');
            if (searchInput && window.searchComponent) {
                searchInput.value = query;
                window.searchComponent.performSearch();
            }
        }, 100);
    },

    // Navigate to page
    navigate: (page) => {
        window.location.hash = page;
    },

    // Show notification
    notify: (type, title, message) => {
        if (window.toast) {
            window.toast.show(type, title, message);
        }
    }
};

// Add helpful console message
console.log(`
🐨 Koala Search Engine
=====================
Available commands:
- KoalaSearch.search('your query') - Perform a search
- KoalaSearch.navigate('page') - Navigate to page (search, websites, analytics)
- KoalaSearch.notify('type', 'title', 'message') - Show notification

Keyboard shortcuts:
- Ctrl/Cmd + K - Focus search input
- Alt + 1/2/3 - Navigate between pages
- Escape - Clear focus/close menus
`); 