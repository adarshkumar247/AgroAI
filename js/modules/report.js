// Crop Health Analysis Report View - Kisan-First 4-Question Flow & Action Protocol
window.AgroModules = window.AgroModules || {};

window.AgroModules.report = {
  render: function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    const scan = state.activeScan || {
      scan_id: 'AGR-89241',
      crop: 'Tomato',
      possible_issue: 'Early Blight',
      confidence: 0.91,
      severity: 'Attention Needed',
      stage: 'Stage 2 — Mild Spread',
      pathogen: 'Alternaria solani',
      spread_risk: 'Moderate',
      canopy_loss: '< 4%',
      immediate_action: 'Prune affected lower leaves, switch to targeted drip irrigation, apply neem oil.',
      previewUrl: ''
    };

    const confidencePct = Math.round(scan.confidence * 100);
    const strokeDash = `${confidencePct}, 100`;
    const imageSrc = scan.previewUrl || '';

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-6xl mx-auto w-full">
          <!-- Top Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
                <a class="hover:text-primary transition-colors" href="#crop-scanner">${isHi ? 'रोग जांच' : 'Crop Scanner'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'जांच रिपोर्ट' : 'Diagnostic Report'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'फसल स्वास्थ्य जांच परिणाम' : 'Crop Health Diagnostic Report'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ID: #${scan.scan_id || 'AGR-89241'} • ${isHi ? 'सत्यापित AI परिणाम' : 'Verified Agronomic Vision AI'}
              </p>
            </div>
            <div class="flex flex-wrap items-center gap-space-xs">
              <button onclick="window.print()" class="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md border border-outline-variant/30 font-semibold">
                <span class="material-symbols-outlined text-[18px]">print</span>
                <span>${isHi ? 'प्रिंट / सेव' : 'Print / Save'}</span>
              </button>
              <button onclick="window.location.hash='#crop-scanner'" class="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container shadow-xs">
                <span class="material-symbols-outlined text-[18px]">photo_camera</span>
                <span>${isHi ? 'दूसरी पत्ती जांचें' : 'Scan Another Leaf'}</span>
              </button>
            </div>
          </div>

          <!-- Hero Diagnostic Banner -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-[0_4px_24px_rgba(0,0,0,0.03)] flex flex-col xl:flex-row items-stretch gap-space-lg">
            <!-- Leaf Image Display -->
            <div class="w-full xl:w-72 h-64 xl:h-auto rounded-2xl overflow-hidden bg-surface-container-highest flex items-center justify-center shrink-0 border border-outline-variant/20">
              ${imageSrc ? `
                <img alt="Diagnosed Leaf" class="w-full h-full object-cover" src="${imageSrc}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                <div class="hidden w-full h-full items-center justify-center bg-secondary-container text-secondary">
                  <span class="material-symbols-outlined text-[64px]">eco</span>
                </div>
              ` : `
                <div class="w-full h-full flex items-center justify-center bg-secondary-container text-secondary">
                  <span class="material-symbols-outlined text-[64px]">eco</span>
                </div>
              `}
            </div>

            <!-- Diagnosis Info -->
            <div class="flex-1 flex flex-col justify-between gap-space-md">
              <div class="flex flex-col gap-space-xs">
                <div class="flex items-center gap-space-xs">
                  <span class="px-3 py-1 rounded-full bg-amber-100 text-amber-900 font-label-sm font-bold flex items-center gap-1">
                    <span class="material-symbols-outlined text-[16px] text-amber-700">warning</span>
                    <span>${scan.severity || (isHi ? 'सावधानी जरूरी' : 'Attention Needed')}</span>
                  </span>
                  <span class="px-3 py-1 rounded-full bg-surface-container text-on-surface-variant font-label-sm font-semibold">
                    ${scan.crop}
                  </span>
                </div>

                <div class="mt-1">
                  <span class="font-label-sm text-outline uppercase font-bold">${isHi ? 'संभावित समस्या' : 'Detected Disease'}</span>
                  <h2 class="font-headline-lg text-primary font-bold tracking-tight">${scan.possible_issue}</h2>
                  <p class="font-title-sm text-secondary italic mt-0.5">${scan.pathogen || 'Alternaria solani'}</p>
                </div>

                <p class="font-body-md text-on-surface-variant mt-1">
                  ${isHi
                    ? 'आसान भाषा में: पत्ती पर रोग के लक्षण दिख रहे हैं. समय पर रोकथाम करने से फसल का नुकसान रुक सकता है.'
                    : 'Simple interpretation: Lesions consistent with fungal pathogen stress detected on foliage.'}
                </p>
              </div>

              <!-- Confidence Dial -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-space-md pt-space-xs">
                <div class="flex items-center gap-space-md p-space-sm rounded-2xl bg-surface-container-low border border-outline-variant/20">
                  <div class="relative w-14 h-14 flex-shrink-0 flex items-center justify-center">
                    <svg class="w-14 h-14 transform -rotate-90" viewbox="0 0 36 36">
                      <path class="text-surface-container-high" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="3.5"></path>
                      <path class="text-secondary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="${strokeDash}" stroke-linecap="round" stroke-width="3.5"></path>
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center">
                      <span class="font-label-md font-bold text-primary">${confidencePct}%</span>
                    </div>
                  </div>
                  <div class="flex flex-col">
                    <span class="font-label-sm text-outline uppercase font-semibold">${isHi ? 'AI का भरोसा' : 'AI Confidence'}</span>
                    <span class="font-title-sm text-on-surface font-bold">${isHi ? 'सटीक मिलान' : 'High Precision Match'}</span>
                  </div>
                </div>

                <div class="flex items-center gap-space-md p-space-sm rounded-2xl bg-surface-container-low border border-outline-variant/20">
                  <div class="w-14 h-14 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center font-bold">
                    <span class="material-symbols-outlined text-[28px]">speed</span>
                  </div>
                  <div class="flex flex-col">
                    <span class="font-label-sm text-outline uppercase font-semibold">${isHi ? 'बीमारी का फैलाव' : 'Spread Risk'}</span>
                    <span class="font-title-sm text-amber-900 font-bold">${scan.spread_risk || (isHi ? 'मध्यम' : 'Moderate')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Guidance (अभी क्या करें?) -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-xs flex flex-col gap-space-md">
            <h3 class="font-title-lg text-on-surface font-bold flex items-center gap-2">
              <span class="material-symbols-outlined text-[24px] text-primary">task_alt</span>
              <span>${isHi ? 'किसान के लिए जरूरी कदम (अभी क्या करें?)' : 'Recommended Agronomic Recovery Steps'}</span>
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
              <div class="p-space-md rounded-2xl bg-surface-container-low border border-outline-variant/20 flex items-start gap-3">
                <span class="text-2xl">✂️</span>
                <div>
                  <span class="font-label-md text-on-surface font-bold">${isHi ? '1. ग्रसित पत्तियां हटाएं' : '1. Foliar Sanitation'}</span>
                  <p class="font-body-sm text-on-surface-variant mt-1">
                    ${isHi ? 'ज्यादा खराब पत्तियों को काटकर खेत से दूर नष्ट कर दें ताकि बीमारी न फैले.' : 'Carefully remove and destroy infected bottom foliage.'}
                  </p>
                </div>
              </div>

              <div class="p-space-md rounded-2xl bg-surface-container-low border border-outline-variant/20 flex items-start gap-3">
                <span class="text-2xl">💧</span>
                <div>
                  <span class="font-label-md text-on-surface font-bold">${isHi ? '2. पानी जड़ों में दें, पत्तियों पर नहीं' : '2. Water Management'}</span>
                  <p class="font-body-sm text-on-surface-variant mt-1">
                    ${isHi ? 'ड्रिप से पानी दें ताकि पत्तियां सूखी रहें और फफूंद न पनपे.' : 'Irrigate at root zone via drip to keep canopy dry.'}
                  </p>
                </div>
              </div>

              <div class="p-space-md rounded-2xl bg-secondary-container/30 border border-secondary/30 flex items-start gap-3 md:col-span-2">
                <span class="text-2xl">🌿</span>
                <div>
                  <span class="font-label-md text-secondary font-bold">${isHi ? '3. सुरक्षित जैविक उपचार' : '3. Eco-Friendly Treatment'}</span>
                  <p class="font-body-md text-on-surface mt-1">
                    ${isHi ? 'नीम के तेल (5ml प्रति लीटर पानी) या ट्राइकोडर्मा का छिड़काव सुबह के समय करें.' : 'Apply cold-pressed neem oil (5ml/L) or biological Trichoderma in early morning.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
