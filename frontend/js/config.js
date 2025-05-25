const API_CONFIG = {
    BASE_URL: '/api',
    ENDPOINTS: {
        SEARCH: '/search',
        WEBSITES: '/websites',
        POPULAR: '/popular',
        STATS: '/stats'
    },
    DEFAULT_PARAMS: {
        PER_PAGE: 10,
        MAX_PAGES: 50,
        MAX_DEPTH: 2
    }
};

const UI_CONFIG = {
    TOAST_DURATION: 5000,
    SEARCH_DEBOUNCE: 300,
    ANIMATION_DURATION: 300
};

window.API_CONFIG = API_CONFIG;
window.UI_CONFIG = UI_CONFIG; 