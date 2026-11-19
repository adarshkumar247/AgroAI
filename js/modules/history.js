// Scan History & Reports Module - Kisan-First User-Scoped Archive
window.AgroModules = window.AgroModules || {};

window.AgroModules['scan-history'] = {
  render: async function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    const currentUser = window.AgroAuth ? window.AgroAuth.getUser() : null;
    const farmerName = currentUser && currentUser.full_name ? currentUser.full_name.split(' ')[0] : (isHi ? 'किसान भाई' : 'Farmer');

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-6xl mx-auto w-full">
          <!-- Top Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
                <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Dashboard'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'पुरानी जांचें' : 'Scan History'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'पुरानी फसल जांचों का रिकॉर्ड' : 'Diagnostic Archive & Scan History'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ${isHi ? `${farmerName} जी के खेत की सभी पिछली AI जांचें और रिपोर्ट.` : `Diagnostic records and foliar health ratings for ${farmerName}'s farm.`}
              </p>
            </div>
            <button onclick="window.location.hash='#crop-scanner'" class="flex items-center gap-space-xs px-space-lg py-3 rounded-2xl bg-primary text-on-primary font-label-lg font-bold shadow-xs hover:bg-primary-container transition-all self-start md:self-auto">
              <span class="material-symbols-outlined text-[20px]">photo_camera</span>
              <span>${isHi ? 'नई जांच करें' : 'New AI Scan'}</span>
            </button>
          </div>

          <!-- Filter & Search Bar -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-md border border-outline-variant/30 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-space-md">
            <div class="flex items-center gap-space-sm bg-surface-container-low px-space-md py-2.5 rounded-2xl w-full sm:w-80 border border-outline-variant/20">
              <span class="material-symbols-outlined text-outline text-[20px]">search</span>
              <input id="history-search" class="bg-transparent border-none outline-none w-full text-body-md text-on-surface placeholder:text-outline" placeholder="${isHi ? 'फसल, बीमारी या ID खोजें...' : 'Search by crop, disease, or ID...'}" type="text"/>
            </div>
            <div class="flex items-center gap-space-xs self-start sm:self-auto flex-wrap">
              <span class="font-label-md text-on-surface-variant mr-1 font-bold">${isHi ? 'फ़िल्टर:' : 'Filter:'}</span>
              <button class="filter-pill px-3.5 py-1.5 rounded-full bg-primary-container text-on-primary-container font-label-md font-bold transition-all" data-filter="all">${isHi ? 'सभी' : 'All'}</button>
              <button class="filter-pill px-3.5 py-1.5 rounded-full bg-surface-container text-on-surface font-label-md font-medium hover:bg-surface-container-high transition-all" data-filter="alert">${isHi ? 'ध्यान देने योग्य' : 'Attention Needed'}</button>
              <button class="filter-pill px-3.5 py-1.5 rounded-full bg-surface-container text-on-surface font-label-md font-medium hover:bg-surface-container-high transition-all" data-filter="healthy">${isHi ? 'स्वस्थ पत्तियां' : 'Healthy'}</button>
            </div>
          </div>

          <!-- History Records Container -->
          <div id="history-list" class="flex flex-col gap-space-sm">
            <div class="p-space-xl text-center text-on-surface-variant">
              <span class="material-symbols-outlined text-[32px] animate-spin text-secondary">progress_activity</span>
              <p class="mt-2 font-body-md font-semibold">${isHi ? 'डेटाबेस से रिकॉर्ड लोड हो रहे हैं...' : 'Loading scan archives...'}</p>
            </div>
          </div>
        </div>
      </div>
    `;

    const historyList = container.querySelector('#history-list');

    let dbScans = [];
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/scans');
      if (res.ok) {
        dbScans = await res.json();
      }
    } catch (e) {
      console.warn('Scans fetch notice:', e.message);
    }

    const allScans = (dbScans && dbScans.length > 0)
      ? dbScans.map(s => {
          const isHealthy = s.possible_issue && s.possible_issue.toLowerCase().includes('healthy');
          return {
            scan_id: s.scan_id,
            crop: s.crop,
            possible_issue: s.possible_issue,
            confidence: s.confidence,
            severity: s.severity || (isHealthy ? (isHi ? 'स्वस्थ' : 'Healthy') : (isHi ? 'जांच जरूरी' : 'Attention Needed')),
            stage: s.stage || (isHealthy ? 'Vegetative / Optimal' : 'Stage 2 — Moderate Symptoms'),
            pathogen: s.pathogen || (isHealthy ? 'None Detected' : 'Alternaria solani / Fungal Pathogen'),
            created_at: s.created_at ? new Date(s.created_at).toLocaleDateString([], { dateStyle: 'medium' }) : (isHi ? 'आज' : 'Today'),
            image_url: s.image_url ? (s.image_url.startsWith('http') ? s.image_url : `http://127.0.0.1:8000${s.image_url}`) : ''
          };
        })
      : [];

    function renderList(scans) {
      if (!scans.length) {
        historyList.innerHTML = `
          <div class="p-space-xl bg-surface-container-lowest rounded-3xl border border-outline-variant/30 text-center text-on-surface-variant flex flex-col items-center justify-center py-16">
            <div class="w-16 h-16 rounded-full bg-secondary-container/60 text-secondary flex items-center justify-center mb-3">
              <span class="material-symbols-outlined text-[36px]">document_scanner</span>
            </div>
            <h3 class="font-title-lg text-on-surface font-bold">${isHi ? 'अभी कोई पुरानी जांच रिकॉर्ड नहीं है' : 'No Scans Recorded'}</h3>
            <p class="font-body-md text-on-surface-variant max-w-md mx-auto mt-1">
              ${isHi ? 'फसल की पत्ती की फोटो अपलोड करके पहली जांच शुरू करें.' : 'Upload a crop leaf photo to diagnose diseases and log telemetry.'}
            </p>
            <button onclick="window.location.hash='#crop-scanner'" class="mt-6 flex items-center gap-2 px-space-lg py-3 rounded-2xl bg-primary text-on-primary font-label-lg font-bold hover:bg-primary-container transition-all shadow-xs">
              <span class="material-symbols-outlined text-[20px]">photo_camera</span>
              <span>${isHi ? 'पहली फसल जांच शुरू करें' : 'Start First Crop Scan'}</span>
            </button>
          </div>
        `;
        return;
      }

      historyList.innerHTML = scans.map((s, idx) => {
        const isHealthy = s.possible_issue && s.possible_issue.toLowerCase().includes('healthy');
        const badgeColor = isHealthy ? 'bg-secondary-container text-on-secondary-container' : 'bg-error-container/80 text-on-error-container';
        const dotColor = isHealthy ? 'bg-secondary' : 'bg-amber-500';
        const confPct = Math.round((s.confidence || 0.9) * 100);

        return `
          <div class="p-space-md rounded-2xl bg-surface-container-lowest border border-outline-variant/30 shadow-xs hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-space-md">
            <div class="flex items-center gap-space-md min-w-0">
              <div class="relative w-16 h-16 rounded-2xl overflow-hidden flex-shrink-0 bg-surface-container-highest flex items-center justify-center border border-outline-variant/20">
                ${s.image_url ? `
                  <img src="${s.image_url}" class="w-full h-full object-cover" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"/>
                  <div class="hidden w-full h-full items-center justify-center bg-secondary-container text-secondary">
                    <span class="material-symbols-outlined text-[28px]">eco</span>
                  </div>
                ` : `
                  <div class="w-full h-full flex items-center justify-center bg-secondary-container text-secondary">
                    <span class="material-symbols-outlined text-[28px]">eco</span>
                  </div>
                `}
                <span class="absolute bottom-1 right-1 w-3 h-3 rounded-full ${dotColor} ring-2 ring-white"></span>
              </div>
              <div class="flex flex-col min-w-0">
                <div class="flex items-center gap-space-xs flex-wrap">
                  <span class="font-title-md text-on-surface font-bold truncate">${s.crop}</span>
                  <span class="px-space-xs py-0.5 rounded-full ${badgeColor} font-label-sm font-bold">${isHealthy ? (isHi ? 'स्वस्थ पत्ती' : 'Healthy') : (isHi ? 'जांच जरूरी' : 'Attention Needed')}</span>
                  <span class="font-label-sm text-outline font-mono text-[11px]">#${s.scan_id}</span>
                </div>
                <span class="font-body-sm text-on-surface-variant mt-0.5">
                  ${isHi ? 'निदान:' : 'Diagnosis:'} <strong class="text-on-surface font-bold">${s.possible_issue}</strong>
                </span>
                <div class="flex items-center gap-space-md text-outline font-label-sm mt-1">
                  <span class="text-secondary font-bold">${confPct}% ${isHi ? 'भरोसा' : 'Confidence'}</span>
                  <span>•</span>
                  <span>${s.created_at}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-space-sm self-end md:self-center flex-shrink-0">
              <button class="view-report-btn px-space-md py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md font-bold transition-all border border-outline-variant/20 shadow-2xs" data-idx="${idx}">
                ${isHi ? 'रिपोर्ट देखें' : 'View Report'}
              </button>
            </div>
          </div>
        `;
      }).join('');

      historyList.querySelectorAll('.view-report-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-idx'));
          const selectedScan = scans[idx];
          window.AgroAppState.activeScan = {
            ...selectedScan,
            previewUrl: selectedScan.image_url
          };
          window.location.hash = '#health-analysis';
        });
      });
    }

    renderList(allScans);

    container.querySelectorAll('.filter-pill').forEach(pill => {
      pill.addEventListener('click', function() {
        container.querySelectorAll('.filter-pill').forEach(p => {
          p.classList.remove('bg-primary-container', 'text-on-primary-container', 'font-bold');
          p.classList.add('bg-surface-container', 'text-on-surface', 'font-medium');
        });
        this.classList.add('bg-primary-container', 'text-on-primary-container', 'font-bold');
        this.classList.remove('bg-surface-container', 'text-on-surface', 'font-medium');

        const filter = this.getAttribute('data-filter');
        if (filter === 'all') {
          renderList(allScans);
        } else if (filter === 'alert') {
          renderList(allScans.filter(s => !s.possible_issue.toLowerCase().includes('healthy')));
        } else if (filter === 'healthy') {
          renderList(allScans.filter(s => s.possible_issue.toLowerCase().includes('healthy')));
        }
      });
    });

    const searchInput = container.querySelector('#history-search');
    searchInput?.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = allScans.filter(s => 
        (s.crop && s.crop.toLowerCase().includes(q)) ||
        (s.possible_issue && s.possible_issue.toLowerCase().includes(q)) ||
        (s.scan_id && s.scan_id.toLowerCase().includes(q))
      );
      renderList(filtered);
    });
  }
};
