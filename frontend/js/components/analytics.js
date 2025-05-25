// Analytics Component
class AnalyticsComponent {
    constructor() {
        this.totalSearches = document.getElementById('total-searches');
        this.totalWebsites = document.getElementById('total-websites');
        this.activeCrawls = document.getElementById('active-crawls');
        this.popularQueriesAnalytics = document.getElementById('popular-queries-analytics');
        
        this.init();
    }

    init() {
        // Load analytics when page is accessed
        document.addEventListener('pageLoad', (e) => {
            if (e.detail.page === 'analytics') {
                this.loadAnalytics();
            }
        });

        // Auto-refresh analytics every 60 seconds
        setInterval(() => {
            if (document.getElementById('analytics-page').classList.contains('active')) {
                this.loadAnalytics();
            }
        }, 60000);
    }

    async loadAnalytics() {
        try {
            const [stats, popularQueries] = await Promise.all([
                apiService.getStats(),
                apiService.getPopularQueries()
            ]);

            this.updateStats(stats);
            this.updatePopularQueries(popularQueries);
        } catch (error) {
            console.error('Failed to load analytics:', error);
            window.toast.show('error', 'Analytics Error', 'Failed to load analytics data');
        }
    }

    updateStats(stats) {
        // Animate number changes
        this.animateNumber(this.totalSearches, stats.total_searches || 0);
        this.animateNumber(this.totalWebsites, stats.total_websites || 0);
        this.animateNumber(this.activeCrawls, stats.active_crawls || 0);
    }

    updatePopularQueries(queries) {
        if (Object.keys(queries).length === 0) {
            this.popularQueriesAnalytics.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-chart-bar fa-2x"></i>
                    <p>No search queries yet</p>
                </div>
            `;
            return;
        }

        this.popularQueriesAnalytics.innerHTML = '';
        
        // Sort queries by count and take top 10
        const sortedQueries = Object.entries(queries)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10);

        const maxCount = Math.max(...sortedQueries.map(([,count]) => count));

        sortedQueries.forEach(([query, count]) => {
            const queryItem = document.createElement('div');
            queryItem.className = 'query-item fade-in';
            
            const percentage = (count / maxCount) * 100;
            
            queryItem.innerHTML = `
                <div class="query-text">${Utils.sanitizeHTML(query)}</div>
                <div class="query-count">${Utils.formatNumber(count)} searches</div>
                <div class="query-bar" style="width: ${percentage}%; background: linear-gradient(90deg, var(--primary-color), var(--primary-hover)); height: 4px; margin-top: 4px; border-radius: 2px;"></div>
            `;

            // Add click to search functionality
            queryItem.addEventListener('click', () => {
                // Navigate to search page and perform search
                window.location.hash = 'search';
                setTimeout(() => {
                    const searchInput = document.getElementById('search-input');
                    if (searchInput) {
                        searchInput.value = query;
                        window.searchComponent.performSearch();
                    }
                }, 100);
            });

            queryItem.style.cursor = 'pointer';
            queryItem.title = `Click to search for "${query}"`;

            this.popularQueriesAnalytics.appendChild(queryItem);
        });
    }

    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = Math.ceil((targetValue - currentValue) / 20);
        
        if (currentValue === targetValue) return;

        const timer = setInterval(() => {
            const current = parseInt(element.textContent) || 0;
            const next = current + increment;
            
            if ((increment > 0 && next >= targetValue) || (increment < 0 && next <= targetValue)) {
                element.textContent = Utils.formatNumber(targetValue);
                clearInterval(timer);
            } else {
                element.textContent = Utils.formatNumber(next);
            }
        }, 50);
    }
}

// Initialize analytics component
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsComponent = new AnalyticsComponent();
}); 