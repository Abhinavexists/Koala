// Toast Notification Component
class ToastComponent {
    constructor() {
        this.container = document.getElementById('toast-container');
        this.toasts = new Map();
    }

    show(type = 'info', title = '', message = '', duration = UI_CONFIG.TOAST_DURATION) {
        const id = Date.now().toString();
        const toast = this.createToast(id, type, title, message);
        
        this.container.appendChild(toast);
        this.toasts.set(id, toast);

        // Auto-remove after duration
        setTimeout(() => {
            this.remove(id);
        }, duration);

        return id;
    }

    createToast(id, type, title, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.dataset.id = id;

        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icons[type]}"></i>
            </div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${Utils.sanitizeHTML(title)}</div>` : ''}
                <div class="toast-message">${Utils.sanitizeHTML(message)}</div>
            </div>
        `;

        return toast;
    }

    remove(id) {
        const toast = this.toasts.get(id);
        if (toast) {
            toast.remove();
            this.toasts.delete(id);
        }
    }
} 