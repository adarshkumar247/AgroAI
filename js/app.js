// AgroAI Core Application Orchestrator, Router & Authentication Guard
window.AgroAppState = {
  currentRoute: 'dashboard',
  activeScan: null,
  scans: []
};

// Kisan-First Internationalization System (Hindi default | English)
window.AgroI18n = {
  getLanguage: function() {
    return localStorage.getItem('agro_lang') || 'hi';
  },
  setLanguage: function(lang) {
    localStorage.setItem('agro_lang', lang);
    this.updateStaticUI();
    // Re-render active module
    const curRoute = window.AgroAppState.currentRoute || 'dashboard';
    if (window.AgroModules && window.AgroModules[curRoute] && window.AgroModules[curRoute].render) {
      const viewport = document.getElementById('app-viewport');
      if (viewport) {
        window.AgroModules[curRoute].render(viewport, window.AgroAppState);
      }
    }
  },
  isHindi: function() {
    return this.getLanguage() === 'hi';
  },
  updateStaticUI: function() {
    const isHi = this.isHindi();
    const langBtn = document.getElementById('header-lang-text');
    if (langBtn) {
      langBtn.innerText = isHi ? 'हिंदी' : 'English';
    }

    const scanBtnText = document.getElementById('header-scan-text');
    if (scanBtnText) {
      scanBtnText.innerText = isHi ? 'फसल जांचें' : 'Scan Crop';
    }

    // Nav item translations
    const navMap = {
      'dashboard': { hi: 'डैशबोर्ड (मुख्य पृष्ठ)', en: 'Dashboard' },
      'crop-scanner': { hi: 'फसल रोग जांच (AI)', en: 'Crop Scanner' },
      'crop-identification': { hi: 'पौधा पहचानें', en: 'Crop Identification' },
      'nutrient-and-fertilizer': { hi: 'खाद और पोषक तत्व', en: 'Nutrient & Fertilizer' },
      'smart-irrigation': { hi: 'सिंचाई और पानी', en: 'Smart Irrigation' },
      'weather-intelligence': { hi: 'मौसम और छिड़काव', en: 'Weather Intelligence' },
      'ai-assistant': { hi: 'किसान AI सहायक', en: 'AI Assistant' },
      'scan-history': { hi: 'पुरानी जांचें (इतिहास)', en: 'Scan History' },
      'farm-insights': { hi: 'खेत का विश्लेषण', en: 'Farm Insights' },
      'help-and-support': { hi: 'मदद और सुझाव', en: 'Help & Support' },
      'settings': { hi: 'मेरी प्रोफाइल और सेटिंग्स', en: 'Settings & Profile' }
    };

    document.querySelectorAll('nav a[data-path]').forEach(el => {
      const path = el.getAttribute('data-path');
      if (navMap[path]) {
        const textSpan = el.querySelector('span:last-child');
        if (textSpan && !el.querySelector('.bg-secondary-container')) {
          textSpan.innerText = isHi ? navMap[path].hi : navMap[path].en;
        } else if (textSpan) {
          const mainSpan = el.querySelector('div span:last-child');
          if (mainSpan) mainSpan.innerText = isHi ? navMap[path].hi : navMap[path].en;
        }
      }
    });

    // Operations / System category headers
    const headers = document.querySelectorAll('aside span.text-outline');
    if (headers.length >= 2) {
      headers[0].innerText = isHi ? 'मुख्य सेवाएं' : 'Operations';
      headers[1].innerText = isHi ? 'सिस्टम' : 'System';
    }
  }
};

// Authentication Store with Avatar Generation
window.AgroAuth = {
  getToken: function() {
    return localStorage.getItem('agro_auth_token');
  },
  getUser: function() {
    try {
      const u = localStorage.getItem('agro_user');
      return u ? JSON.parse(u) : null;
    } catch (e) {
      return null;
    }
  },
  getAvatarUrl: function(user) {
    if (user && user.profile_photo_url) {
      return user.profile_photo_url;
    }
    const initial = (user && user.full_name) ? user.full_name.trim().charAt(0).toUpperCase() : 'K';
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><circle cx="24" cy="24" r="24" fill="#1b5e20"/><text x="24" y="26" fill="#ffffff" font-family="Plus Jakarta Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle" dominant-baseline="middle">${initial}</text></svg>`;
    return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
  },
  setAuth: function(token, user) {
    if (token) localStorage.setItem('agro_auth_token', token);
    if (user) localStorage.setItem('agro_user', JSON.stringify(user));
    this.updateUserUI();
  },
  clearAuth: function() {
    localStorage.removeItem('agro_auth_token');
    localStorage.removeItem('agro_user');
  },
  isAuthenticated: function() {
    return Boolean(this.getToken());
  },
  logout: async function() {
    const token = this.getToken();
    if (token) {
      try {
        await fetch('http://127.0.0.1:8000/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (e) {}
    }
    this.clearAuth();
    window.location.hash = '#login';
  },
  updateUserUI: function() {
    const user = this.getUser();
    if (!user) return;
    const nameEls = document.querySelectorAll('#sidebar-user-name');
    const locEls = document.querySelectorAll('#sidebar-user-location, #header-user-location');
    nameEls.forEach(el => { el.innerText = user.full_name || 'Farmer'; });
    locEls.forEach(el => { el.innerText = user.location || 'Lucknow Farm, UP'; });

    // Update avatar images
    const avatarUrl = this.getAvatarUrl(user);
    const avatarEls = document.querySelectorAll('#header-user-avatar, #sidebar-user-avatar');
    avatarEls.forEach(img => {
      img.src = avatarUrl;
    });
  }
};

// Global Weather Sync for Header
window.AgroWeather = {
  syncHeaderWeather: async function() {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/weather/current');
      if (res.ok) {
        const data = await res.json();
        const pill = document.getElementById('header-weather-pill');
        if (pill) {
          const temp = data.temperature_c !== undefined ? `${data.temperature_c}°C` : (data.temperature || '28.5°C');
          const spray = data.spray_advisory || {};
          const badge = spray.badge || '🟢';
          const cond = data.condition_hi || data.condition || '';
          pill.innerText = `${badge} ${temp} ${cond}`.trim();
        }
      }
    } catch (e) {
      console.warn('Header weather sync notice:', e);
    }
  }
};

// Global Fetch Interceptor to automatically attach Bearer Auth Token
(function() {
  const originalFetch = window.fetch;
  window.fetch = function(input, init = {}) {
    init = init || {};
    init.headers = init.headers || {};
    const token = window.AgroAuth.getToken();
    if (token) {
      if (init.headers instanceof Headers) {
        if (!init.headers.has('Authorization')) {
          init.headers.set('Authorization', `Bearer ${token}`);
        }
      } else if (Array.isArray(init.headers)) {
        const hasAuth = init.headers.some(([k]) => k.toLowerCase() === 'authorization');
        if (!hasAuth) {
          init.headers.push(['Authorization', `Bearer ${token}`]);
        }
      } else {
        if (!init.headers['Authorization'] && !init.headers['authorization']) {
          init.headers['Authorization'] = `Bearer ${token}`;
        }
      }
    }
    return originalFetch(input, init);
  };
})();

// AgroAI Client Application Bootstrap

(function() {
  const viewport = document.getElementById('app-viewport');
  const sidebar = document.getElementById('app-sidebar');
  const header = document.getElementById('app-header');
  const backdrop = document.getElementById('sidebar-backdrop');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const closeSidebarBtn = document.getElementById('close-sidebar-btn');
  const mainWrapper = viewport ? viewport.parentElement : null;

  // Navigation routes dictionary
  const routes = {
    'login': {
      render: function(container, state) {
        window.AgroModules.auth.render(container, state, 'login');
      }
    },
    'signup': {
      render: function(container, state) {
        window.AgroModules.auth.render(container, state, 'signup');
      }
    },
    'dashboard': window.AgroModules.dashboard,
    'crop-scanner': window.AgroModules.scanner,
    'health-analysis': window.AgroModules.report,
    'crop-identification': window.AgroModules['crop-identification'],
    'nutrient-and-fertilizer': window.AgroModules['nutrient-and-fertilizer'],
    'smart-irrigation': window.AgroModules['smart-irrigation'],
    'weather-intelligence': window.AgroModules['weather-intelligence'],
    'ai-assistant': window.AgroModules['ai-assistant'],
    'scan-history': window.AgroModules['scan-history'],
    'farm-insights': window.AgroModules['farm-insights'],
    'help-and-support': window.AgroModules['help-and-support'],
    'settings': window.AgroModules['settings']
  };

  function closeMobileDrawer() {
    if (sidebar) sidebar.classList.add('-translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
  }

  function openMobileDrawer() {
    if (sidebar) sidebar.classList.remove('-translate-x-full');
    if (backdrop) backdrop.classList.remove('hidden');
  }

  mobileMenuBtn?.addEventListener('click', () => {
    if (sidebar.classList.contains('-translate-x-full')) {
      openMobileDrawer();
    } else {
      closeMobileDrawer();
    }
  });

  closeSidebarBtn?.addEventListener('click', closeMobileDrawer);
  backdrop?.addEventListener('click', closeMobileDrawer);

  document.getElementById('sidebar-logout-btn')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (confirm('Are you sure you want to sign out of AgroAI?')) {
      window.AgroAuth.logout();
    }
  });

  const mobileBottomNav = document.getElementById('mobile-bottom-nav');

  function updateActiveNav(route) {
    const navLinks = document.querySelectorAll('nav a[data-path]');
    navLinks.forEach(link => {
      const path = link.getAttribute('data-path');
      const isCurrent = (path === route) || (route === 'health-analysis' && path === 'crop-scanner');
      if (isCurrent) {
        link.className = 'flex items-center justify-between px-space-md py-space-sm transition-all bg-primary-container text-on-primary-container font-label-lg rounded-xl shadow-[0_2px_6px_-2px_rgba(26,28,25,0.03)]';
        link.setAttribute('aria-current', 'page');
      } else {
        link.className = 'flex items-center justify-between px-space-md py-space-sm rounded-xl font-label-lg text-label-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-all';
        link.removeAttribute('aria-current');
      }
    });

    // Mobile bottom navigation active state
    const mobileLinks = document.querySelectorAll('nav a[data-mobile-path]');
    mobileLinks.forEach(link => {
      const path = link.getAttribute('data-mobile-path');
      const isCurrent = (path === route) || (route === 'health-analysis' && path === 'crop-scanner');
      if (path === 'crop-scanner') return; // Center scan button styling is persistent
      if (isCurrent) {
        link.className = 'flex flex-col items-center justify-center gap-0.5 text-primary font-label-sm py-1 flex-1 font-bold';
      } else {
        link.className = 'flex flex-col items-center justify-center gap-0.5 text-on-surface-variant font-label-sm hover:text-primary transition-colors py-1 flex-1 font-medium';
      }
    });
  }

  function applyLayoutForRoute(route) {
    const isAuthRoute = (route === 'login' || route === 'signup');
    if (isAuthRoute) {
      if (sidebar) sidebar.classList.add('hidden');
      if (header) header.classList.add('hidden');
      if (mobileBottomNav) mobileBottomNav.classList.add('hidden');
      if (mainWrapper) {
        mainWrapper.classList.remove('lg:pl-72');
      }
      if (viewport) {
        viewport.classList.remove('pt-16', 'pb-20');
      }
    } else {
      if (sidebar) sidebar.classList.remove('hidden');
      if (header) header.classList.remove('hidden');
      if (mobileBottomNav) mobileBottomNav.classList.remove('hidden');
      if (mainWrapper) {
        mainWrapper.classList.add('lg:pl-72');
      }
      if (viewport) {
        viewport.classList.add('pt-16', 'pb-20');
      }
      window.AgroAuth.updateUserUI();
    }
  }

  // Navigate to route with Route Guard
  function navigate(rawRoute) {
    let cleanRoute = (rawRoute || '').replace(/^#/, '');

    // Route Guard: unauthenticated users must always go to login first
    const isAuthenticated = window.AgroAuth.isAuthenticated();

    if (!isAuthenticated) {
      if (cleanRoute !== 'signup') {
        cleanRoute = 'login';
      }
      if (window.location.hash !== '#' + cleanRoute) {
        window.location.hash = '#' + cleanRoute;
      }
    } else {
      if (cleanRoute === 'login' || cleanRoute === 'signup' || !cleanRoute) {
        cleanRoute = 'dashboard';
        if (window.location.hash !== '#dashboard') {
          window.location.hash = '#dashboard';
        }
      }
    }

    const targetModule = routes[cleanRoute] || routes['dashboard'];
    window.AgroAppState.currentRoute = cleanRoute;

    applyLayoutForRoute(cleanRoute);
    updateActiveNav(cleanRoute);
    closeMobileDrawer();

    if (viewport && targetModule && targetModule.render) {
      targetModule.render(viewport, window.AgroAppState);
      window.scrollTo(0, 0);
    }
  }

  // Router listener
  window.addEventListener('hashchange', () => {
    navigate(window.location.hash);
  });

  // Initial Route & i18n setup - opens login first if not authenticated
  const initialHash = window.location.hash || (window.AgroAuth.isAuthenticated() ? '#dashboard' : '#login');
  navigate(initialHash);

  window.addEventListener('DOMContentLoaded', () => {
    window.AgroAuth.updateUserUI();
    window.AgroI18n.updateStaticUI();
    if (window.AgroAuth.isAuthenticated()) {
      window.AgroWeather.syncHeaderWeather();
    }
    // Periodically sync weather every 5 minutes
    setInterval(() => {
      if (window.AgroAuth.isAuthenticated()) {
        window.AgroWeather.syncHeaderWeather();
      }
    }, 5 * 60 * 1000);
  });

  // Global Quick Action Handler
  document.getElementById('header-scan-btn')?.addEventListener('click', () => {
    window.location.hash = '#crop-scanner';
  });

  // Header Language Switcher Toggle Handler
  document.getElementById('header-lang-btn')?.addEventListener('click', () => {
    const current = window.AgroI18n.getLanguage();
    const next = current === 'hi' ? 'en' : 'hi';
    window.AgroI18n.setLanguage(next);
  });

})();
