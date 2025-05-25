class APIService {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async search(query, page = 1, perPage = API_CONFIG.DEFAULT_PARAMS.PER_PAGE) {
        const params = new URLSearchParams({
            q: query,
            page: page.toString(),
            per_page: perPage.toString(),
            sort_by: 'score'
        });

        return this.request(`${API_CONFIG.ENDPOINTS.SEARCH}?${params}`);
    }

    async getWebsites() {
        return this.request(API_CONFIG.ENDPOINTS.WEBSITES);
    }

    async addWebsite(websiteData) {
        return this.request(API_CONFIG.ENDPOINTS.WEBSITES, {
            method: 'POST',
            body: JSON.stringify(websiteData)
        });
    }

    async deleteWebsite(websiteId) {
        return this.request(`${API_CONFIG.ENDPOINTS.WEBSITES}/${websiteId}`, {
            method: 'DELETE'
        });
    }

    async recrawlWebsite(websiteId) {
        return this.request(`${API_CONFIG.ENDPOINTS.WEBSITES}/${websiteId}/recrawl`, {
            method: 'POST'
        });
    }

    async getPopularQueries() {
        return this.request(API_CONFIG.ENDPOINTS.POPULAR);
    }

    async getStats() {
        return this.request(API_CONFIG.ENDPOINTS.STATS);
    }
}

window.apiService = new APIService(); 