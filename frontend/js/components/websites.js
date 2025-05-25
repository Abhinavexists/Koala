// Websites Management Component
class WebsitesComponent {
    constructor() {
        this.addWebsiteForm = document.getElementById('add-website-form');
        this.websitesList = document.getElementById('websites-list');
        this.websitesError = document.getElementById('websites-error');
        this.addWebsiteBtn = document.getElementById('add-website-btn');
        
        this.websites = [];
        this.init();
    }

    init() {
        // Form submission
        this.addWebsiteForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addWebsite();
        });

        // Load websites when page is accessed
        document.addEventListener('pageLoad', (e) => {
            if (e.detail.page === 'websites') {
                this.loadWebsites();
            }
        });

        // Auto-refresh websites every 30 seconds to update crawl status
        setInterval(() => {
            if (document.getElementById('websites-page').classList.contains('active')) {
                this.loadWebsites();
            }
        }, 30000);
    }

    async addWebsite() {
        const formData = new FormData(this.addWebsiteForm);
        const websiteData = {
            url: formData.get('url') || document.getElementById('website-url').value,
            name: formData.get('name') || document.getElementById('website-name').value,
            description: formData.get('description') || document.getElementById('website-description').value,
            max_pages: parseInt(document.getElementById('max-pages').value) || 50,
            max_depth: parseInt(document.getElementById('max-depth').value) || 2
        };

        // Validation
        if (!websiteData.url || !websiteData.name) {
            this.showError('URL and name are required');
            return;
        }

        if (!Utils.isValidURL(websiteData.url)) {
            this.showError('Please enter a valid URL');
            return;
        }

        this.setLoading(true);
        this.hideError();

        try {
            await apiService.addWebsite(websiteData);
            
            // Clear form
            this.addWebsiteForm.reset();
            document.getElementById('max-pages').value = '50';
            document.getElementById('max-depth').value = '2';
            
            // Reload websites list
            await this.loadWebsites();
            
            // Show success message
            if (window.toast) {
                window.toast.show('success', 'Website Added', 'Website has been added and crawling started');
            }
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoading(false);
        }
    }

    async loadWebsites() {
        try {
            this.websites = await apiService.getWebsites();
            this.renderWebsites();
        } catch (error) {
            this.showError('Failed to load websites: ' + error.message);
        }
    }

    renderWebsites() {
        if (this.websites.length === 0) {
            this.websitesList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-globe fa-3x"></i>
                    <h3>No websites added yet</h3>
                    <p>Add your first website above to start crawling and searching!</p>
                </div>
            `;
            return;
        }

        this.websitesList.innerHTML = '';
        
        this.websites.forEach(website => {
            const websiteCard = this.createWebsiteCard(website);
            this.websitesList.appendChild(websiteCard);
        });
    }

    createWebsiteCard(website) {
        const card = document.createElement('div');
        card.className = 'website-card fade-in';
        
        const statusClass = `status-${website.status}`;
        const lastCrawled = website.last_crawled 
            ? new Date(website.last_crawled).toLocaleDateString()
            : 'Never';

        card.innerHTML = `
            <div class="website-header">
                <div class="website-info">
                    <h3>${Utils.sanitizeHTML(website.name)}</h3>
                    <div class="website-url">${Utils.sanitizeHTML(website.url)}</div>
                    ${website.description ? `<div class="website-description">${Utils.sanitizeHTML(website.description)}</div>` : ''}
                </div>
                <div class="website-status">
                    <span class="status-badge ${statusClass}">${website.status}</span>
                    <div class="pages-count">${website.pages_crawled} pages</div>
                    <div class="pages-count">Last crawled: ${lastCrawled}</div>
                </div>
            </div>
            <div class="website-actions">
                <button class="btn btn-sm btn-secondary recrawl-btn" data-id="${website.id}">
                    <i class="fas fa-sync-alt"></i> Recrawl
                </button>
                <button class="btn btn-sm btn-danger delete-btn" data-id="${website.id}">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;

        // Add event listeners
        const recrawlBtn = card.querySelector('.recrawl-btn');
        const deleteBtn = card.querySelector('.delete-btn');

        recrawlBtn.addEventListener('click', () => this.recrawlWebsite(website.id));
        deleteBtn.addEventListener('click', () => this.confirmDeleteWebsite(website.id, website.name));

        return card;
    }

    async recrawlWebsite(websiteId) {
        try {
            await apiService.recrawlWebsite(websiteId);
            await this.loadWebsites();
            if (window.toast) {
                window.toast.show('info', 'Recrawl Started', 'Website recrawling has been initiated');
            }
        } catch (error) {
            if (window.toast) {
                window.toast.show('error', 'Recrawl Failed', error.message);
            }
        }
    }

    // Fixed method name and implementation
    async confirmDeleteWebsite(websiteId, websiteName) {
        // Use a more sophisticated confirmation dialog
        const confirmed = await this.showConfirmDialog(
            'Delete Website',
            `Are you sure you want to delete "${websiteName}"? This action cannot be undone.`,
            'Delete',
            'Cancel'
        );

        if (confirmed) {
            await this.deleteWebsite(websiteId, websiteName);
        }
    }

    async deleteWebsite(websiteId, websiteName) {
        try {
            await apiService.deleteWebsite(websiteId);
            await this.loadWebsites();
            if (window.toast) {
                window.toast.show('success', 'Website Deleted', `"${websiteName}" has been removed`);
            }
        } catch (error) {
            if (window.toast) {
                window.toast.show('error', 'Delete Failed', error.message);
            }
        }
    }

    // Custom confirmation dialog
    showConfirmDialog(title, message, confirmText = 'OK', cancelText = 'Cancel') {
        return new Promise((resolve) => {
            // Create modal overlay
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            `;

            // Create modal
            const modal = document.createElement('div');
            modal.className = 'confirm-modal';
            modal.style.cssText = `
                background: white;
                border-radius: 8px;
                padding: 24px;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            `;

            modal.innerHTML = `
                <h3 style="margin: 0 0 16px 0; color: #333;">${title}</h3>
                <p style="margin: 0 0 24px 0; color: #666; line-height: 1.5;">${message}</p>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button class="cancel-btn" style="
                        padding: 8px 16px;
                        border: 1px solid #ddd;
                        background: white;
                        border-radius: 4px;
                        cursor: pointer;
                    ">${cancelText}</button>
                    <button class="confirm-btn" style="
                        padding: 8px 16px;
                        border: none;
                        background: #dc3545;
                        color: white;
                        border-radius: 4px;
                        cursor: pointer;
                    ">${confirmText}</button>
                </div>
            `;

            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            // Add event listeners
            const confirmBtn = modal.querySelector('.confirm-btn');
            const cancelBtn = modal.querySelector('.cancel-btn');

            const cleanup = () => {
                document.body.removeChild(overlay);
            };

            confirmBtn.addEventListener('click', () => {
                cleanup();
                resolve(true);
            });

            cancelBtn.addEventListener('click', () => {
                cleanup();
                resolve(false);
            });

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    cleanup();
                    resolve(false);
                }
            });

            // Focus the confirm button
            setTimeout(() => confirmBtn.focus(), 100);
        });
    }

    setLoading(loading) {
        this.addWebsiteBtn.disabled = loading;
        if (loading) {
            this.addWebsiteBtn.innerHTML = '<div class="spinner"></div> Adding...';
        } else {
            this.addWebsiteBtn.innerHTML = '<i class="fas fa-plus"></i> Add Website';
        }
    }

    showError(message) {
        this.websitesError.textContent = message;
        Utils.show(this.websitesError);
    }

    hideError() {
        Utils.hide(this.websitesError);
    }
}

// Initialize websites component
document.addEventListener('DOMContentLoaded', () => {
    window.websitesComponent = new WebsitesComponent();
}); 