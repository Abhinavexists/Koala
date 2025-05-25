// Navigation Component
class Navbar {
    constructor() {
        this.navLinks = document.querySelectorAll('.nav-link');
        this.navToggle = document.querySelector('.nav-toggle');
        this.navLinksContainer = document.querySelector('.nav-links');
        this.pages = document.querySelectorAll('.page');
        
        this.init();
    }

    init() {
        // Add click listeners to navigation links
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateTo(page);
            });
        });

        // Mobile menu toggle
        if (this.navToggle) {
            this.navToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.handlePopState();
        });

        // Set initial page based on URL hash
        this.handleInitialNavigation();
    }

    navigateTo(page) {
        // Update active nav link
        this.navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });

        // Show/hide pages
        this.pages.forEach(pageElement => {
            pageElement.classList.remove('active');
            if (pageElement.id === `${page}-page`) {
                pageElement.classList.add('active');
            }
        });

        // Update URL hash
        window.location.hash = page;

        // Close mobile menu if open
        this.closeMobileMenu();

        // Trigger page-specific initialization
        this.triggerPageLoad(page);
    }

    toggleMobileMenu() {
        this.navToggle.classList.toggle('active');
        this.navLinksContainer.classList.toggle('active');
    }

    closeMobileMenu() {
        this.navToggle.classList.remove('active');
        this.navLinksContainer.classList.remove('active');
    }

    handlePopState() {
        const hash = window.location.hash.slice(1) || 'search';
        this.navigateTo(hash);
    }

    handleInitialNavigation() {
        const hash = window.location.hash.slice(1) || 'search';
        this.navigateTo(hash);
    }

    triggerPageLoad(page) {
        // Trigger custom events for page components
        const event = new CustomEvent('pageLoad', { detail: { page } });
        document.dispatchEvent(event);
    }
}

// Initialize navbar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.navbar = new Navbar();
}); 