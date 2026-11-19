// Dashboard View - Kisan-First Botanical Functionalism with Live SQLite, Auth & Unified Weather
window.AgroModules = window.AgroModules || {};

window.AgroModules.dashboard = {
  render: async function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    let summaryData = null;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/dashboard/summary');
      if (res.ok) {
        summaryData = await res.json();
      }
    } catch (e) {
      console.warn('Dashboard live summary fetch notice:', e);
    }

    const farm = summaryData ? summaryData.farm_overview : {};
    const weather = summaryData ? summaryData.micro_climate : {};
    const recentScans = (summaryData && summaryData.recent_activity && summaryData.recent_activity.length > 0)
      ? summaryData.recent_activity
      : [];

    const totalScans = farm.total_scans_logged !== undefined ? farm.total_scans_logged : (state.scans ? state.scans.length : 0);
    const healthScore = farm.foliar_health_score_pct !== undefined ? farm.foliar_health_score_pct : 86;
    const attentionCount = farm.attention_needed_count !== undefined ? farm.attention_needed_count : 0;
    const avgConfidence = farm.average_model_confidence ? Math.round(farm.average_model_confidence * 100) : 91;

    const currentTemp = weather.temperature || '28.5°C';
    const currentCondition = isHi ? (weather.condition_hi || weather.condition || 'आंशिक रूप से बादल') : (weather.condition_en || weather.condition || 'Partly Cloudy');
    const currentHumidity = weather.humidity || '81%';
    const currentWind = weather.wind || '1.0 km/h';
    const currentRain = weather.rain_risk || '0%';

    const spray = (weather && typeof weather.spray_advisory === 'object') ? weather.spray_advisory : {
      status: 'postpone',
      badge: '🔴',
      title_hi: 'अभी छिड़काव टालें',
      title_en: 'Postpone Foliar Spray',
      reason_hi: 'हवा शांत है लेकिन नमी अधिक है जिससे दवा पत्ती पर सूखने में समय लेगी.',
      reason_en: 'Wind is calm but humidity is high, slowing evaporation.',
      next_check_hi: 'अगले 3-4 घंटे बाद मौसम दोबारा देखें.',
      next_check_en: 'Re-check weather in 3-4 hours.',
      is_safe_to_spray: false
    };

    const sprayTitle = isHi ? (spray.title_hi || spray.title || 'छिड़काव सलाह') : (spray.title_en || spray.title || 'Spray Advisory');
    const sprayReason = isHi ? (spray.reason_hi || spray.reason || spray.advisory || '') : (spray.reason_en || spray.reason || spray.advisory || '');

    // Authenticated Farmer Context
    const currentUser = window.AgroAuth ? window.AgroAuth.getUser() : null;
    const farmerName = currentUser && currentUser.full_name ? currentUser.full_name.split(' ')[0] : (isHi ? 'किसान भाई' : 'Farmer');
    const farmLocation = (currentUser && currentUser.location) || (isHi ? 'लखनऊ फार्म, उत्तर प्रदेश' : 'Lucknow Farm, UP');

    // Overall Farm Status Pill
    const farmStatusPill = attentionCount === 0
      ? `<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container text-on-secondary-container font-label-md font-bold text-sm">🟢 ${isHi ? 'फसल ठीक है' : 'All Crops Healthy'}</span>`
      : `<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-300 font-label-md font-bold text-sm">🟡 ${isHi ? attentionCount + ' खेत पर ध्यान दें' : attentionCount + ' Plots Need Care'}</span>`;

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-7xl mx-auto w-full">
          <!-- Top Greeting & Header Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs">
                <span class="font-headline-lg text-headline-lg text-on-surface font-extrabold tracking-tight">
                  ${isHi ? `नमस्ते, ${farmerName} जी` : `Good morning, ${farmerName}`}
                </span>
                <span class="text-headline-lg animate-bounce">🌱</span>
              </div>
              <p class="font-body-lg text-body-lg text-on-surface-variant flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[18px] text-secondary">location_on</span>
                <span>${isHi ? 'फार्म और फसल स्थिति:' : 'Monitoring crops for'} <strong>${farmLocation}</strong></span>
              </p>
            </div>
            <div class="flex items-center gap-space-sm flex-wrap">
              <button class="flex items-center gap-space-xs px-space-md py-2 rounded-full bg-surface-container hover:bg-surface-container-high active:scale-95 text-on-surface transition-all font-label-md border border-outline-variant/30 shadow-xs" id="refresh-btn">
                <span class="material-symbols-outlined text-[18px] text-secondary">refresh</span>
                <span>${isHi ? 'ताज़ा करें' : 'Refresh'}</span>
              </button>
              <button class="flex items-center gap-space-xs px-space-md py-2 rounded-full bg-surface-container hover:bg-surface-container-high active:scale-95 text-on-surface transition-all font-label-md border border-outline-variant/30 shadow-xs" onclick="window.location.hash='#scan-history'">
                <span class="material-symbols-outlined text-[18px] text-on-surface-variant">history</span>
                <span>${isHi ? 'पुरानी जांचें' : 'Scan Archive'}</span>
              </button>
            </div>
          </div>

          <!-- Kisan-First Status Hero Card (आज खेत का क्या हाल है?) -->
          <div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#EBF5EC] via-[#F1F8F2] to-[#E8F5E9] p-space-lg lg:p-space-xl border border-secondary/20 shadow-[0_4px_24px_rgba(27,94,32,0.05)]">
            <div class="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-space-lg">
              <div class="flex flex-col gap-space-sm max-w-2xl">
                <div class="flex items-center gap-2">
                  <div class="inline-flex items-center gap-1 px-space-sm py-0.5 rounded-full bg-surface-container-lowest/90 border border-primary/20 shadow-xs">
                    <span class="material-symbols-outlined text-[16px] text-primary" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
                    <span class="font-label-sm text-label-sm text-primary uppercase tracking-wider font-bold">AI Krishi Vision</span>
                  </div>
                  ${farmStatusPill}
                </div>
                <h1 class="font-display-sm text-display-sm text-primary font-bold tracking-tight">
                  ${isHi ? 'आज खेत का क्या हाल है?' : 'Scan Your Crop with AgroAI'}
                </h1>
                <p class="font-body-lg text-body-lg text-on-surface-variant">
                  ${isHi
                    ? 'पौधे की पत्ती की फोटो लें और बीमारी, कीड़े या पोषण की कमी की तुरंत जांच करें.'
                    : 'Take a clear leaf photo to instantly detect diseases, pest stress, or nutrient deficiencies.'}
                </p>
              </div>
              <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-space-md w-full lg:w-auto flex-shrink-0">
                <button onclick="window.location.hash='#crop-scanner'" class="group flex items-center justify-center gap-space-sm px-space-lg py-3.5 rounded-2xl bg-primary text-on-primary font-label-lg shadow-[0_4px_16px_rgba(27,94,32,0.25)] hover:bg-primary-container active:scale-98 transition-all font-bold">
                  <span class="material-symbols-outlined text-[22px] transition-transform group-hover:scale-110">photo_camera</span>
                  <span>${isHi ? 'फसल की जांच करें' : 'Scan Your Crop'}</span>
                  <span class="ml-space-xs px-2 py-0.5 rounded-lg bg-surface-container-lowest/20 text-on-primary font-label-sm">AI</span>
                </button>
                <button onclick="window.location.hash='#ai-assistant'" class="flex items-center justify-center gap-space-xs px-space-md py-3.5 rounded-2xl bg-surface-container-lowest hover:bg-surface-container text-on-surface font-label-lg transition-all border border-outline-variant/30 shadow-xs font-semibold">
                  <span class="material-symbols-outlined text-[20px] text-secondary">smart_toy</span>
                  <span>${isHi ? 'कृषि सहायक से पूछें' : 'Ask AI Copilot'}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 4 Simple KPIs for Farmers -->
          <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-space-md">
            <!-- Total Scans -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg flex flex-col justify-between border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md transition-all">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl bg-secondary-container/60 flex items-center justify-center text-primary">
                  <span class="material-symbols-outlined text-[24px]">document_scanner</span>
                </div>
                <span class="px-space-xs py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm font-semibold">
                  ${isHi ? 'सक्रिय' : 'Active'}
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-label-md text-label-md text-outline uppercase tracking-wider font-semibold">
                  ${isHi ? 'मैंने कितनी बार जांच की' : 'Total Scans Logged'}
                </span>
                <div class="font-headline-lg text-headline-lg text-on-surface font-extrabold mt-1">${totalScans}</div>
                <span class="font-body-sm text-on-surface-variant">${isHi ? 'पौधों की जांचें' : 'leaf scans'}</span>
              </div>
            </div>

            <!-- Health Score -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg flex flex-col justify-between border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md transition-all">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl bg-primary-fixed/50 flex items-center justify-center text-secondary">
                  <span class="material-symbols-outlined text-[24px]" style="font-variation-settings: 'FILL' 1;">eco</span>
                </div>
                <span class="px-space-xs py-0.5 rounded-full bg-surface-container-high text-on-surface-variant font-label-sm font-semibold">
                  NDVI
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-label-md text-label-md text-outline uppercase tracking-wider font-semibold">
                  ${isHi ? 'फसल की सेहत' : 'Foliar Health Score'}
                </span>
                <div class="flex items-baseline gap-space-xs mt-1">
                  <span class="font-headline-lg text-headline-lg text-secondary font-extrabold">${healthScore}%</span>
                  <span class="font-body-sm text-body-sm text-on-surface-variant">${isHi ? 'स्वस्थ फसल' : 'healthy crops'}</span>
                </div>
              </div>
            </div>

            <!-- Attention Needed -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg flex flex-col justify-between border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md transition-all">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl ${attentionCount > 0 ? 'bg-error-container text-error' : 'bg-secondary-container text-secondary'} flex items-center justify-center">
                  <span class="material-symbols-outlined text-[24px]">${attentionCount > 0 ? 'warning' : 'check_circle'}</span>
                </div>
                <span class="px-space-xs py-0.5 rounded-full ${attentionCount > 0 ? 'bg-error-container text-on-error-container font-bold' : 'bg-secondary-container text-on-secondary-container font-semibold'} font-label-sm">
                  ${attentionCount > 0 ? (isHi ? 'जांच जरूरी' : 'Attention') : (isHi ? 'सब ठीक' : 'Optimal')}
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-label-md text-label-md text-outline uppercase tracking-wider font-semibold">
                  ${isHi ? 'जिन फसलों पर ध्यान चाहिए' : 'Attention Needed'}
                </span>
                <div class="flex items-baseline gap-space-xs mt-1">
                  <span class="font-headline-lg text-headline-lg ${attentionCount > 0 ? 'text-error' : 'text-on-surface'} font-extrabold">${attentionCount}</span>
                  <span class="font-body-sm text-body-sm text-on-surface-variant">${isHi ? 'पौधे' : 'plots'}</span>
                </div>
              </div>
            </div>

            <!-- AI Model Confidence -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg flex flex-col justify-between border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md transition-all">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl bg-tertiary-fixed/60 flex items-center justify-center text-tertiary">
                  <span class="material-symbols-outlined text-[24px]">psychology</span>
                </div>
                <span class="px-space-xs py-0.5 rounded-full bg-surface-container text-on-surface-variant font-label-sm font-semibold">
                  MobileNetV3
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-label-md text-label-md text-outline uppercase tracking-wider font-semibold">
                  ${isHi ? 'AI के नतीजे पर भरोसा' : 'Diagnostic Confidence'}
                </span>
                <div class="flex items-baseline gap-space-xs mt-1">
                  <span class="font-headline-lg text-headline-lg text-on-surface font-extrabold">${avgConfidence}%</span>
                  <span class="font-body-sm text-body-sm text-on-surface-variant">${isHi ? 'सटीकता' : 'accuracy'}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Main Grid: Recent Activity & Live Micro-Climate -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
            <!-- Left Column: Recent Scans -->
            <div class="lg:col-span-8 flex flex-col gap-space-lg">
              <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] flex flex-col gap-space-md">
                <div class="flex items-center justify-between">
                  <div>
                    <h2 class="font-title-lg text-title-lg text-on-surface font-bold">
                      ${isHi ? 'हाल की फसल जांचें' : 'Recent Crop Scans'}
                    </h2>
                    <p class="font-body-sm text-body-sm text-on-surface-variant">
                      ${isHi ? 'AI द्वारा जांची गई हाल की पत्तियां' : 'Recently verified crop health scans'}
                    </p>
                  </div>
                  <a class="font-label-md text-secondary font-bold hover:underline hidden sm:inline-flex items-center gap-1" href="#scan-history">
                    <span>${isHi ? 'सभी जांचें देखें' : 'View All Scans'}</span>
                    <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                  </a>
                </div>

                <div class="flex flex-col gap-space-sm" id="dashboard-scans-container">
                  ${recentScans && recentScans.length > 0 ? recentScans.map(s => {
                    const isHealthy = s.diagnosis && s.diagnosis.toLowerCase().includes('healthy');
                    const badgeClass = isHealthy ? 'bg-secondary-container text-on-secondary-container' : 'bg-error-container/80 text-on-error-container';
                    const dotClass = isHealthy ? 'bg-secondary' : 'bg-[#fbc02d]';
                    const timeStr = s.created_at ? new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'हाल ही में';
                    return `
                      <div class="p-space-md rounded-2xl bg-surface-container-low hover:bg-surface-container transition-all flex flex-col md:flex-row md:items-center justify-between gap-space-md border border-outline-variant/20">
                        <div class="flex items-center gap-space-md min-w-0">
                          <div class="relative w-16 h-16 rounded-2xl overflow-hidden flex-shrink-0 bg-surface-container-highest flex items-center justify-center">
                            ${s.image_url ? `
                              <img alt="${s.crop}" class="w-full h-full object-cover" src="http://127.0.0.1:8000${s.image_url}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                              <div class="hidden w-full h-full items-center justify-center bg-secondary-container text-secondary">
                                <span class="material-symbols-outlined text-[28px]">eco</span>
                              </div>
                            ` : `
                              <div class="w-full h-full flex items-center justify-center bg-secondary-container text-secondary">
                                <span class="material-symbols-outlined text-[28px]">eco</span>
                              </div>
                            `}
                            <span class="absolute bottom-1 right-1 w-3 h-3 rounded-full ${dotClass} ring-2 ring-white"></span>
                          </div>
                          <div class="flex flex-col min-w-0">
                            <div class="flex items-center gap-space-xs flex-wrap">
                              <span class="font-title-md text-title-md text-on-surface font-bold truncate">${s.crop}</span>
                              <span class="px-space-xs py-0.5 rounded-full ${badgeClass} font-label-sm font-bold">
                                ${isHealthy ? (isHi ? 'स्वस्थ पत्ती' : 'Healthy Leaf') : (isHi ? 'ध्यान दें' : 'Attention Needed')}
                              </span>
                            </div>
                            <span class="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
                              ${isHi ? 'निदान:' : 'Diagnosis:'} <span class="text-on-surface font-semibold">${s.diagnosis}</span>
                            </span>
                            <div class="flex items-center gap-space-md text-outline font-label-sm mt-1">
                              <span class="text-secondary font-bold">${Math.round((s.confidence || 0.9) * 100)}% ${isHi ? 'भरोसा' : 'Confidence'}</span>
                              <span>•</span>
                              <span>${timeStr}</span>
                            </div>
                          </div>
                        </div>
                        <div class="flex items-center gap-space-sm self-end md:self-center flex-shrink-0">
                          <button onclick="window.location.hash='#scan-history'" class="px-space-md py-2 rounded-xl bg-surface-container-lowest hover:bg-surface-container-high text-on-surface font-label-md transition-all border border-outline-variant/30 shadow-2xs font-semibold">
                            ${isHi ? 'रिपोर्ट देखें' : 'View Report'}
                          </button>
                        </div>
                      </div>
                    `;
                  }).join('') : `
                    <div class="p-space-lg rounded-2xl bg-surface-container-low text-center text-on-surface-variant border border-outline-variant/20">
                      <div class="w-12 h-12 rounded-full bg-secondary-container/60 text-secondary mx-auto flex items-center justify-center mb-2">
                        <span class="material-symbols-outlined text-[24px]">photo_camera</span>
                      </div>
                      <p class="font-body-md font-bold text-on-surface">${isHi ? 'आज अभी तक कोई जांच नहीं की गई.' : 'No scans logged yet today.'}</p>
                      <p class="font-body-sm text-on-surface-variant mt-1">${isHi ? 'ऊपर "फसल की जांच करें" बटन दबाकर पौधे की पत्ती की फोटो भेजें.' : 'Click "Scan Crop Leaf" to upload a leaf photograph for instant AI diagnostics.'}</p>
                    </div>
                  `}
                </div>
              </div>
            </div>

            <!-- Right Column: Live Weather & Spray Advisory -->
            <div class="lg:col-span-4 flex flex-col gap-space-lg">
              <!-- Live Weather Card -->
              <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] flex flex-col gap-space-md">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-space-xs text-secondary font-bold">
                    <span class="material-symbols-outlined text-[22px]">partly_cloudy_day</span>
                    <span class="font-label-md uppercase tracking-wider">${isHi ? 'खेत का मौसम' : 'Field Weather'}</span>
                  </div>
                  <span class="px-space-xs py-0.5 rounded-full bg-surface-container text-outline font-label-sm font-semibold">Open-Meteo</span>
                </div>
                <div>
                  <div class="flex items-center justify-between mt-space-xs">
                    <div class="flex items-baseline gap-space-xs">
                      <span class="font-display-md text-display-md text-on-surface font-extrabold">${currentTemp.replace('°C', '°')}</span>
                      <span class="font-title-md text-title-md text-on-surface-variant font-bold">C</span>
                    </div>
                    <div class="flex flex-col items-end">
                      <span class="font-title-sm text-title-sm text-on-surface font-bold">${currentCondition}</span>
                      <span class="font-label-sm text-secondary font-medium">${isHi ? 'लाइव तापमान' : 'Live Temperature'}</span>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-space-sm bg-surface-container-low p-space-sm rounded-2xl border border-outline-variant/20">
                  <div class="flex items-center gap-space-xs">
                    <span class="material-symbols-outlined text-[20px] text-blue-600">water_drop</span>
                    <div class="flex flex-col">
                      <span class="font-label-sm text-outline font-medium">${isHi ? 'नमी' : 'Humidity'}</span>
                      <span class="font-title-sm text-on-surface font-bold">${currentHumidity}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-space-xs">
                    <span class="material-symbols-outlined text-[20px] text-teal-600">air</span>
                    <div class="flex flex-col">
                      <span class="font-label-sm text-outline font-medium">${isHi ? 'हवा' : 'Wind'}</span>
                      <span class="font-title-sm text-on-surface font-bold">${currentWind}</span>
                    </div>
                  </div>
                </div>

                <!-- Unified Spray Alert Card -->
                <div class="p-space-sm rounded-2xl ${spray.status === 'optimal' ? 'bg-secondary-container/40 border border-secondary/20 text-on-secondary-container' : (spray.status === 'caution' ? 'bg-amber-50 border border-amber-200 text-amber-900' : 'bg-rose-50 border border-rose-200 text-rose-900')} flex items-start gap-space-sm">
                  <span class="text-xl flex-shrink-0 mt-0.5">${spray.badge || '🟢'}</span>
                  <div class="flex flex-col">
                    <span class="font-title-sm font-bold">${isHi ? 'छिड़काव सलाह:' : 'Spray Advisory:'} ${sprayTitle}</span>
                    <p class="font-body-sm mt-0.5 font-medium leading-snug">${sprayReason}</p>
                  </div>
                </div>

                <button onclick="window.location.hash='#weather-intelligence'" class="w-full py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-primary font-label-md font-bold transition-all text-center">
                  ${isHi ? 'विस्तृत मौसम देखें →' : 'View Full Weather Details →'}
                </button>
              </div>

              <!-- Quick Agronomic Actions -->
              <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-[0_2px_12px_rgba(0,0,0,0.03)] flex flex-col gap-space-md">
                <h3 class="font-title-md text-on-surface font-bold">${isHi ? 'त्वरित सेवाएं' : 'Quick Actions'}</h3>
                <div class="grid grid-cols-2 gap-space-sm">
                  <button onclick="window.location.hash='#crop-scanner'" class="p-space-sm rounded-2xl bg-surface-container-low hover:bg-surface-container flex flex-col items-center text-center gap-space-xs transition-all border border-outline-variant/10">
                    <div class="w-10 h-10 rounded-xl bg-secondary-container text-on-secondary-container flex items-center justify-center">
                      <span class="material-symbols-outlined text-[20px]">photo_camera</span>
                    </div>
                    <span class="font-label-md font-bold text-on-surface">${isHi ? 'रोग जांच' : 'Disease Scan'}</span>
                  </button>
                  <button onclick="window.location.hash='#crop-identification'" class="p-space-sm rounded-2xl bg-surface-container-low hover:bg-surface-container flex flex-col items-center text-center gap-space-xs transition-all border border-outline-variant/10">
                    <div class="w-10 h-10 rounded-xl bg-tertiary-fixed text-tertiary flex items-center justify-center">
                      <span class="material-symbols-outlined text-[20px]">psychiatry</span>
                    </div>
                    <span class="font-label-md font-bold text-on-surface">${isHi ? 'पौधा पहचान' : 'Crop ID'}</span>
                  </button>
                  <button onclick="window.location.hash='#smart-irrigation'" class="p-space-sm rounded-2xl bg-surface-container-low hover:bg-surface-container flex flex-col items-center text-center gap-space-xs transition-all border border-outline-variant/10">
                    <div class="w-10 h-10 rounded-xl bg-surface-container-high text-primary flex items-center justify-center">
                      <span class="material-symbols-outlined text-[20px]">water_drop</span>
                    </div>
                    <span class="font-label-md font-bold text-on-surface">${isHi ? 'सिंचाई सलाह' : 'Irrigation'}</span>
                  </button>
                  <button onclick="window.location.hash='#nutrient-and-fertilizer'" class="p-space-sm rounded-2xl bg-surface-container-low hover:bg-surface-container flex flex-col items-center text-center gap-space-xs transition-all border border-outline-variant/10">
                    <div class="w-10 h-10 rounded-xl bg-primary-fixed text-primary flex items-center justify-center">
                      <span class="material-symbols-outlined text-[20px]">compost</span>
                    </div>
                    <span class="font-label-md font-bold text-on-surface">${isHi ? 'खाद कैलकुलेटर' : 'Nutrients'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    const refreshBtn = container.querySelector('#refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function() {
        const icon = this.querySelector('.material-symbols-outlined');
        if (icon) {
          icon.classList.add('animate-spin');
          setTimeout(() => {
            icon.classList.remove('animate-spin');
            window.AgroModules.dashboard.render(container, state);
          }, 600);
        }
      });
    }
  }
};
