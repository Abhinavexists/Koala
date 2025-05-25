class SearchComponent {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchBtn = document.getElementById('search-btn');
        this.searchResults = document.getElementById('search-results');
        this.searchStats = document.getElementById('search-stats');
        this.popularQueries = document.getElementById('popular-queries');
        this.popularQueriesList = document.getElementById('popular-queries-list');
        this.errorMessage = document.getElementById('error-message');
        this.loading = document.getElementById('loading');
        this.pagination = document.getElementById('pagination');
        
        this.currentPage = 1;
        this.currentQuery = '';
        this.totalResults = 0;
        
        this.init();
    }

    init() {
        this.searchBtn.addEventListener('click', () => {
            this.performSearch();
        });

        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        const debouncedSearch = Utils.debounce(() => {
            if (this.searchInput.value.trim().length > 2) {
                this.performSearch();
            }
        }, UI_CONFIG.SEARCH_DEBOUNCE);

        this.searchInput.addEventListener('input', debouncedSearch);

        document.addEventListener('pageLoad', (e) => {
            if (e.detail.page === 'search') {
                this.loadPopularQueries();
            }
        });

        this.handleURLParams();
    }

    async performSearch(page = 1) {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.currentQuery = query;
        this.currentPage = page;
        
        this.showLoading();
        this.hideError();

        try {
            const results = await apiService.search(query, page);
            this.displayResults(results);
            this.updateURL();
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(results) {
        this.totalResults = results.total;
        
        this.searchStats.textContent = 
            `Found ${Utils.formatNumber(results.total)} results in ${Utils.formatTime(results.time_taken)}`;
        Utils.show(this.searchStats);

        this.searchResults.innerHTML = '';

        if (results.results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search fa-3x"></i>
                    <h3>No results found</h3>
                    <p>Try different keywords or check your spelling</p>
                </div>
            `;
        } else {
            results.results.forEach(result => {
                const resultCard = this.createResultCard(result);
                this.searchResults.appendChild(resultCard);
            });
        }

        this.updatePagination(results);
        
        Utils.scrollTo(this.searchResults, 100);
    }

    createResultCard(result) {
        const card = document.createElement('div');
        card.className = 'result-card fade-in';
        
        card.innerHTML = `
            <a href="${Utils.sanitizeHTML(result.url)}" class="result-url" target="_blank" rel="noopener">
                ${Utils.sanitizeHTML(result.url)}
            </a>
            <div class="result-score">
                Relevance Score: ${result.score.toFixed(4)}
            </div>
            <div class="result-snippet">
                ${Utils.sanitizeHTML(result.snippet)}
            </div>
        `;

        return card;
    }

    updatePagination(results) {
        if (results.total <= API_CONFIG.DEFAULT_PARAMS.PER_PAGE) {
            Utils.hide(this.pagination);
            return;
        }

        const totalPages = Math.ceil(results.total / API_CONFIG.DEFAULT_PARAMS.PER_PAGE);
        
        this.pagination.innerHTML = `
            <button class="pagination-btn" id="prev-btn" ${this.currentPage === 1 ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i> Previous
            </button>
            <span class="pagination-info">Page ${this.currentPage} of ${totalPages}</span>
            <button class="pagination-btn" id="next-btn" ${this.currentPage === totalPages ? 'disabled' : ''}>
                Next <i class="fas fa-chevron-right"></i>
            </button>
        `;

        document.getElementById('prev-btn').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.performSearch(this.currentPage - 1);
            }
        });

        document.getElementById('next-btn').addEventListener('click', () => {
            if (this.currentPage < totalPages) {
                this.performSearch(this.currentPage + 1);
            }
        });

        Utils.show(this.pagination);
    }

    async loadPopularQueries() {
        try {
            const queries = await apiService.getPopularQueries();
            this.displayPopularQueries(queries);
        } catch (error) {
            this.showError(error.message);
        }
    }

    displayPopularQueries(queries) {
        this.popularQueriesList.innerHTML = '';
        
        const queryArray = Object.keys(queries).sort((a, b) => queries[b] - queries[a]);
        
        queryArray.forEach(query => {
            const queryItem = document.createElement('li');
            queryItem.textContent = query;
            this.popularQueriesList.appendChild(queryItem);
        });

        Utils.show(this.popularQueries);
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.classList.add('error');
        setTimeout(() => {
            this.errorMessage.textContent = '';
            this.errorMessage.classList.remove('error');
        }, UI_CONFIG.TOAST_DURATION);
    }

    hideError() {
        this.errorMessage.textContent = '';
        this.errorMessage.classList.remove('error');
    }

    showLoading() {
        this.loading.classList.add('active');
    }

    hideLoading() {
        this.loading.classList.remove('active');
    }

    updateURL() {
        Utils.updateURL({
            q: this.currentQuery,
            page: this.currentPage.toString()
        });
    }

    handleURLParams() {
        const params = Utils.getQueryParams();
        if (params.q) {
            this.searchInput.value = params.q;
            this.performSearch(parseInt(params.page) || 1);
        }
    }
}

window.searchComponent = new SearchComponent(); 