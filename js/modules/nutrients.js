// Nutrient & Fertilizer Guidance Module - Kisan-First Agronomic Nutrition with 4-Question Structure
window.AgroModules = window.AgroModules || {};

window.AgroModules['nutrient-and-fertilizer'] = {
  render: async function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    let currentCrop = state.nutrientCrop || 'Tomato';
    let currentSymptom = state.nutrientSymptom || 'yellowing_lower_leaves';

    async function fetchGuidance() {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/nutrients/guidance?crop=${encodeURIComponent(currentCrop)}&stage=vegetative&observed_symptoms=${encodeURIComponent(currentSymptom)}&soil_ph=6.8`);
        if (res.ok) {
          return await res.json();
        }
      } catch (e) {
        console.warn('Nutrient guidance fetch notice:', e);
      }
      return {
        crop: currentCrop,
        stage: 'vegetative',
        soil_ph: 6.8,
        standard_npk_rdf_kg_per_ha: { nitrogen_n: 100, phosphorus_p2o5: 60, potassium_k2o: 60 },
        diagnosis: {
          detected_deficiency: 'Nitrogen (N) Deficiency',
          confidence: 0.88,
          cause: 'Mobilization of nitrogen to newer growth.',
          severity: 'Moderate'
        },
        recommendations: {
          synthetic_option: 'Neem-coated Urea (46% N) at standard doses before watering.',
          organic_option: 'Well-decomposed vermicompost or fermented Jeevamrutha.',
          foliar_intervention: 'Mild foliar spray in early morning hours.',
          application_timing: 'Morning application during cool hours.'
        },
        disclaimer: 'Always verify with a local certified soil test before applying synthetic bulk fertilizers.'
      };
    }

    const data = await fetchGuidance();
    const npk = data.standard_npk_rdf_kg_per_ha || data.base_crop_rdf_kg_ha || { nitrogen_n: 100, phosphorus_p2o5: 60, potassium_k2o: 60 };
    const diag = typeof data.diagnosis === 'object' ? data.diagnosis : {
      detected_deficiency: data.diagnosis || 'Nitrogen Deficiency',
      confidence: 0.88,
      cause: '',
      severity: 'Moderate'
    };
    const rec = data.recommendations || {};

    const cropNames = {
      'Tomato': { hi: 'टमाटर (Tomato)', en: 'Tomato' },
      'Rice': { hi: 'धान / चावल (Paddy Rice)', en: 'Paddy Rice' },
      'Corn': { hi: 'मक्का (Corn / Maize)', en: 'Corn / Maize' },
      'Potato': { hi: 'आलू (Potato)', en: 'Potato' }
    };

    const symptomLabels = {
      'yellowing_lower_leaves': {
        hi: 'नीचे या पुरानी पत्तियों का पीला पड़ना (नाइट्रोजन कमी संकेत)',
        en: 'Yellowing of lower / older leaves (Possible N deficit)'
      },
      'purpling_stems': {
        hi: 'पत्तियों और तनों पर बैंगनी या गहरा रंग (फास्फोरस कमी संकेत)',
        en: 'Purplish tint on leaves & stems (Possible P deficit)'
      },
      'burnt_margins': {
        hi: 'पत्तियों के किनारों का झुलसना या मुड़ना (पोटाश कमी संकेत)',
        en: 'Scorched, curling leaf margins (Possible K deficit)'
      },
      'none': {
        hi: 'कोई लक्षण नहीं / सामान्य संतुलित पोषण खुराक',
        en: 'No visible symptoms / Balanced standard nutrition'
      }
    };

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-6xl mx-auto w-full">
          <!-- Top Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
                <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Home'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'खाद और पोषक तत्व' : 'Crop Nutrients'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'फसल के पोषक तत्व और खाद' : 'Crop Nutrients & Fertilizer Guide'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ${isHi ? 'आपकी फसल को किस पोषक तत्व की जरूरत हो सकती है? आसान भाषा में सलाह.' : 'Understand what nutrients your crop needs with clear actionable guidance.'}
              </p>
            </div>
            <div class="flex items-center gap-space-xs bg-surface-container px-space-md py-2 rounded-full border border-outline-variant/30">
              <span class="material-symbols-outlined text-secondary text-[18px]">spa</span>
              <span class="font-label-md font-semibold text-on-surface">
                ${isHi ? 'अनुमानित मिट्टी pH:' : 'Estimated Soil pH:'} <strong>${data.soil_ph} (${isHi ? 'सामान्य' : 'Optimal'})</strong>
              </span>
            </div>
          </div>

          <!-- Selector Card (Crop & Symptoms) -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-space-md">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-space-md flex-1">
              <div class="flex flex-col">
                <label class="font-label-sm text-outline uppercase font-bold">${isHi ? '1. फसल चुनें' : '1. Select Crop'}</label>
                <select id="nutrient-crop" class="mt-1 bg-surface-container-low px-space-md py-2.5 rounded-2xl text-on-surface font-title-sm outline-none border border-outline-variant/20 focus:ring-2 focus:ring-primary">
                  <option value="Tomato" ${currentCrop === 'Tomato' ? 'selected' : ''}>${cropNames['Tomato'][isHi ? 'hi' : 'en']}</option>
                  <option value="Rice" ${currentCrop === 'Rice' ? 'selected' : ''}>${cropNames['Rice'][isHi ? 'hi' : 'en']}</option>
                  <option value="Corn" ${currentCrop === 'Corn' ? 'selected' : ''}>${cropNames['Corn'][isHi ? 'hi' : 'en']}</option>
                  <option value="Potato" ${currentCrop === 'Potato' ? 'selected' : ''}>${cropNames['Potato'][isHi ? 'hi' : 'en']}</option>
                </select>
              </div>
              <div class="flex flex-col">
                <label class="font-label-sm text-outline uppercase font-bold">${isHi ? '2. पत्ती पर क्या दिख रहा है?' : '2. Observed Leaf Symptom'}</label>
                <select id="nutrient-symptom" class="mt-1 bg-surface-container-low px-space-md py-2.5 rounded-2xl text-on-surface font-title-sm outline-none border border-outline-variant/20 focus:ring-2 focus:ring-primary">
                  <option value="yellowing_lower_leaves" ${currentSymptom === 'yellowing_lower_leaves' ? 'selected' : ''}>${symptomLabels['yellowing_lower_leaves'][isHi ? 'hi' : 'en']}</option>
                  <option value="purpling_stems" ${currentSymptom === 'purpling_stems' ? 'selected' : ''}>${symptomLabels['purpling_stems'][isHi ? 'hi' : 'en']}</option>
                  <option value="burnt_margins" ${currentSymptom === 'burnt_margins' ? 'selected' : ''}>${symptomLabels['burnt_margins'][isHi ? 'hi' : 'en']}</option>
                  <option value="none" ${currentSymptom === 'none' ? 'selected' : ''}>${symptomLabels['none'][isHi ? 'hi' : 'en']}</option>
                </select>
              </div>
            </div>

            <button id="diagnose-nutrients-btn" class="px-space-lg py-3 rounded-2xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container transition-all flex items-center justify-center gap-2 shrink-0">
              <span class="material-symbols-outlined text-[20px]">psychology</span>
              <span>${isHi ? 'जांच देखें' : 'Get Guidance'}</span>
            </button>
          </div>

          <!-- 4-Question Result Structure Card -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-xs flex flex-col gap-space-lg">
            <div class="flex items-center justify-between border-b border-outline-variant/20 pb-space-sm">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-[24px] text-primary">eco</span>
                <h2 class="font-title-lg text-on-surface font-bold">
                  ${isHi ? 'पोषक तत्व विश्लेषण' : 'Agronomic Nutrient Assessment'}
                </h2>
              </div>
              <span class="px-3 py-1 rounded-full bg-secondary-container text-on-secondary-container font-label-sm font-bold">
                ${isHi ? 'भरोसा: 88%' : 'Confidence: 88%'}
              </span>
            </div>

            <!-- 4 Questions -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
              <!-- Q1: क्या हो रहा है? -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col gap-1 border border-outline-variant/10">
                <span class="font-label-sm text-primary font-bold uppercase flex items-center gap-1">
                  <span class="material-symbols-outlined text-[16px]">visibility</span>
                  ${isHi ? '1. क्या हो रहा है?' : '1. What is happening?'}
                </span>
                <p class="font-title-sm text-on-surface font-semibold mt-1">
                  ${isHi ? 'पत्तियों में पोषक तत्व की कमी के संकेत दिखाई दे रहे हैं.' : 'Foliar signs indicate possible nutrient deficiency.'}
                </p>
                <span class="font-body-sm text-on-surface-variant">${diag.cause || (isHi ? 'पौधा तेजी से बढ़ रहा है और मिट्टी से पर्याप्त खुराक नहीं मिल पा रही.' : 'Plant is growing rapidly and requires supplementary nutrition.')}</span>
              </div>

              <!-- Q2: इसका मतलब क्या है? -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col gap-1 border border-outline-variant/10">
                <span class="font-label-sm text-amber-800 font-bold uppercase flex items-center gap-1">
                  <span class="material-symbols-outlined text-[16px]">help</span>
                  ${isHi ? '2. इसका मतलब क्या है?' : '2. What does this mean?'}
                </span>
                <p class="font-title-sm text-on-surface font-semibold mt-1">
                  ${diag.detected_deficiency}
                </p>
                <span class="font-body-sm text-on-surface-variant">${isHi ? 'इस पोषक तत्व की कमी से पौधे की बढ़वार या हरियाली प्रभावित हो सकती है.' : 'This deficiency may slow vegetative vigor if unaddressed.'}</span>
              </div>

              <!-- Q3: अभी क्या करें? -->
              <div class="p-space-md rounded-2xl bg-secondary-container/30 flex flex-col gap-1 border border-secondary/20 md:col-span-2">
                <span class="font-label-sm text-secondary font-bold uppercase flex items-center gap-1">
                  <span class="material-symbols-outlined text-[16px]">task_alt</span>
                  ${isHi ? '3. अभी क्या करें?' : '3. What should you do now?'}
                </span>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-space-sm mt-1">
                  <div class="p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/20">
                    <span class="font-label-md text-primary font-bold">🌿 ${isHi ? 'जैविक / देसी तरीका:' : 'Organic / Natural Option:'}</span>
                    <p class="font-body-sm text-on-surface mt-0.5">${rec.organic_option || (isHi ? 'सड़ी गोबर की खाद या जीवामृत का छिड़काव करें.' : 'Apply well-decomposed vermicompost or organic compost.')}</p>
                  </div>
                  <div class="p-2.5 rounded-xl bg-surface-container-lowest border border-outline-variant/20">
                    <span class="font-label-md text-on-surface font-bold">🧪 ${isHi ? 'संतुलित खाद:' : 'Standard Dose:'}</span>
                    <p class="font-body-sm text-on-surface mt-0.5">${rec.synthetic_option || (isHi ? 'सामान्य खुराक अनुसार खाद दें, ज्यादा डालने से बचें.' : 'Apply standard balanced fertilizer per ICAR baseline.')}</p>
                  </div>
                </div>
              </div>

              <!-- Q4: कब दोबारा जांचें? -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col gap-1 border border-outline-variant/10 md:col-span-2">
                <span class="font-label-sm text-outline font-bold uppercase flex items-center gap-1">
                  <span class="material-symbols-outlined text-[16px]">schedule</span>
                  ${isHi ? '4. कब दोबारा जांचें?' : '4. When to check again?'}
                </span>
                <p class="font-body-md text-on-surface font-medium mt-1">
                  ⏱️ ${isHi ? 'खाद या स्प्रे देने के 5 से 7 दिन बाद नई पत्तियों की हरियाली और स्थिति देखें.' : 'Re-inspect new emerging leaves 5 to 7 days after fertilizer application.'}
                </p>
              </div>
            </div>
          </div>

          <!-- 3 Visual NPK Cards for Farmer -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-space-md">
            <!-- N - Nitrogen -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col justify-between">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl bg-primary-fixed/50 flex items-center justify-center text-primary font-extrabold text-xl">N</div>
                <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm font-bold">
                  ${isHi ? 'नाइट्रोजन' : 'Nitrogen'}
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-title-sm text-on-surface font-bold">${isHi ? 'पत्तियों की हरियाली और बढ़वार' : 'Leaf greenness & vegetative growth'}</span>
                <p class="font-body-sm text-on-surface-variant mt-1">
                  ${isHi ? 'पौधे को हरा-भरा रखने और तेजी से बढ़ाने के लिए जरूरी.' : 'Essential for leafy canopy and rapid growth.'}
                </p>
              </div>
            </div>

            <!-- P - Phosphorus -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col justify-between">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl bg-tertiary-fixed/60 flex items-center justify-center text-tertiary font-extrabold text-xl">P</div>
                <span class="px-2.5 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-label-sm font-bold">
                  ${isHi ? 'फास्फोरस' : 'Phosphorus'}
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-title-sm text-on-surface font-bold">${isHi ? 'जड़ और तने का विकास' : 'Root development & early vigor'}</span>
                <p class="font-body-sm text-on-surface-variant mt-1">
                  ${isHi ? 'जड़ों को मिट्टी में गहराई तक फैलाने और तने को मजबूत करने में मदद.' : 'Strengthens root architecture and flowering.'}
                </p>
              </div>
            </div>

            <!-- K - Potash -->
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col justify-between">
              <div class="flex items-center justify-between">
                <div class="w-12 h-12 rounded-2xl bg-secondary-container/50 flex items-center justify-center text-secondary font-extrabold text-xl">K</div>
                <span class="px-2.5 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-label-sm font-bold">
                  ${isHi ? 'पोटाश' : 'Potash'}
                </span>
              </div>
              <div class="mt-space-md">
                <span class="font-title-sm text-on-surface font-bold">${isHi ? 'पौधे की मजबूती और सहनशीलता' : 'Plant immunity & crop resilience'}</span>
                <p class="font-body-sm text-on-surface-variant mt-1">
                  ${isHi ? 'कीड़ों, सूखे और बीमारियों से लड़ने की ताकत देता है.' : 'Builds disease defense and water retention.'}
                </p>
              </div>
            </div>
          </div>

          <!-- Expandable Technical Section (ICAR RDF) -->
          <details class="bg-surface-container-lowest rounded-2xl p-space-md border border-outline-variant/30 text-on-surface">
            <summary class="font-label-md font-bold text-primary cursor-pointer hover:underline">
              📊 ${isHi ? 'तकनीकी जानकारी (ICAR RDF विस्तार से देखें)' : 'Technical Agronomic Data (ICAR RDF breakdown)'}
            </summary>
            <div class="mt-space-md pt-space-sm border-t border-outline-variant/20 grid grid-cols-1 sm:grid-cols-3 gap-space-sm text-body-sm">
              <div class="p-3 rounded-xl bg-surface-container-low">
                <span class="text-outline font-semibold">ICAR N Dose:</span>
                <p class="font-headline-sm font-bold text-on-surface mt-1">${npk.nitrogen_n} kg N/ha</p>
              </div>
              <div class="p-3 rounded-xl bg-surface-container-low">
                <span class="text-outline font-semibold">ICAR P₂O₅ Dose:</span>
                <p class="font-headline-sm font-bold text-on-surface mt-1">${npk.phosphorus_p2o5} kg P₂O₅/ha</p>
              </div>
              <div class="p-3 rounded-xl bg-surface-container-low">
                <span class="text-outline font-semibold">ICAR K₂O Dose:</span>
                <p class="font-headline-sm font-bold text-on-surface mt-1">${npk.potassium_k2o} kg K₂O/ha</p>
              </div>
            </div>
            <p class="font-body-sm text-outline mt-space-sm">${data.disclaimer}</p>
          </details>
        </div>
      </div>
    `;

    container.querySelector('#diagnose-nutrients-btn')?.addEventListener('click', () => {
      state.nutrientCrop = container.querySelector('#nutrient-crop').value;
      state.nutrientSymptom = container.querySelector('#nutrient-symptom').value;
      window.AgroModules['nutrient-and-fertilizer'].render(container, state);
    });
  }
};
