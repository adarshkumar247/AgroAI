// Crop Identification Module - Kisan-First Botanical Species Recognition
window.AgroModules = window.AgroModules || {};

window.AgroModules['crop-identification'] = {
  render: function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-6xl mx-auto w-full">
          <!-- Top Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
                <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Home'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'पौधा पहचानें' : 'Crop ID'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'पौधा या फसल पहचानें' : 'Identify Crop or Plant Species'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ${isHi ? 'किसी भी फसल या जंगली पौधे की पत्ती की फोटो भेजें. AI तुरंत पौधे का नाम और प्रजाति बताएगा.' : 'Upload any plant or crop photo to identify botanical species, genus and family.'}
              </p>
            </div>
            <input type="file" id="crop-id-file-input" accept="image/*" class="hidden" />
            <button id="trigger-id-upload" class="flex items-center gap-space-xs px-space-lg py-3 rounded-2xl bg-primary text-on-primary font-label-lg font-bold shadow-xs hover:bg-primary-container transition-all self-start md:self-auto">
              <span class="material-symbols-outlined text-[20px]">photo_camera</span>
              <span>${isHi ? 'फोटो से पहचानें' : 'Identify from Photo'}</span>
            </button>
          </div>

          <!-- AI Identification Result Box (Hidden until uploaded) -->
          <div id="crop-id-result-container" class="hidden"></div>

          <!-- Drop / Select Zone -->
          <div id="crop-id-dropzone" class="p-space-lg rounded-3xl bg-surface-container-low border-2 border-dashed border-outline-variant hover:border-primary transition-all cursor-pointer text-center flex flex-col items-center justify-center gap-space-xs">
            <div class="w-14 h-14 rounded-2xl bg-secondary-container/60 text-secondary flex items-center justify-center">
              <span class="material-symbols-outlined text-[32px]">psychiatry</span>
            </div>
            <span class="font-title-md font-bold text-on-surface mt-1">
              ${isHi ? 'पौधे की फोटो अपलोड करने के लिए यहाँ दबाएं' : 'Click to Upload Plant Photo for Species ID'}
            </span>
            <p class="font-body-sm text-on-surface-variant max-w-md">
              ${isHi ? 'धान, गेहूं, टमाटर, मक्का, आलू, मिर्च या अन्य पौधों की पत्ती की फोटो दें.' : 'Supports Tomato, Rice, Wheat, Corn, Potato, and diverse crop cultivars.'}
            </p>
          </div>

          <!-- Common Families Guide -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-space-md">
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-sm">
              <div class="w-12 h-12 rounded-2xl bg-secondary-container text-secondary flex items-center justify-center font-bold">
                <span class="material-symbols-outlined text-[24px]">psychiatry</span>
              </div>
              <h3 class="font-title-lg text-on-surface font-bold">${isHi ? 'सोलानेसी कुल (टमाटर, आलू, मिर्च)' : 'Solanaceae Family'}</h3>
              <p class="font-body-sm text-on-surface-variant">${isHi ? 'टमाटर, आलू, बैंगन और मिर्च. अर्ली ब्लाइट और लीफ कर्ल वायरस के प्रति संवेदनशील.' : 'Tomato, Potato, Eggplant, Chili. Sensitive to fungal blights.'}</p>
            </div>

            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-sm">
              <div class="w-12 h-12 rounded-2xl bg-primary-fixed text-primary flex items-center justify-center font-bold">
                <span class="material-symbols-outlined text-[24px]">grass</span>
              </div>
              <h3 class="font-title-lg text-on-surface font-bold">${isHi ? 'पोएसी कुल (अनाज फसलें: धान, गेहूं)' : 'Poaceae (Cereals)'}</h3>
              <p class="font-body-sm text-on-surface-variant">${isHi ? 'धान, गेहूं, मक्का और बाजरा. कल्ले फूटने और ब्लास्ट बीमारी की जांच.' : 'Paddy Rice, Wheat, Corn, Barley. Monitored for tillering and rusts.'}</p>
            </div>

            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-sm">
              <div class="w-12 h-12 rounded-2xl bg-tertiary-fixed text-tertiary flex items-center justify-center font-bold">
                <span class="material-symbols-outlined text-[24px]">eco</span>
              </div>
              <h3 class="font-title-lg text-on-surface font-bold">${isHi ? 'फेबेसी कुल (दालें: अरहर, चना)' : 'Fabaceae (Legumes)'}</h3>
              <p class="font-body-sm text-on-surface-variant">${isHi ? 'चना, अरहर, मसूर और मूंग. जड़ों में नाइट्रोजन गांठें बनाकर मिट्टी को उपजाऊ बनाते हैं.' : 'Chickpea, Pigeon pea, Lentils. Natural nitrogen-fixing root nodules.'}</p>
            </div>
          </div>
        </div>
      </div>
    `;

    const fileInput = container.querySelector('#crop-id-file-input');
    const resultBox = container.querySelector('#crop-id-result-container');
    const dropZone = container.querySelector('#crop-id-dropzone');
    const triggerBtn = container.querySelector('#trigger-id-upload');

    const openPicker = () => fileInput && fileInput.click();
    dropZone?.addEventListener('click', openPicker);
    triggerBtn?.addEventListener('click', openPicker);

    fileInput?.addEventListener('change', async (e) => {
      if (!e.target.files || !e.target.files[0]) return;
      const file = e.target.files[0];
      const previewUrl = URL.createObjectURL(file);

      resultBox.classList.remove('hidden');
      resultBox.innerHTML = `
        <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex items-center gap-space-md text-on-surface">
          <span class="material-symbols-outlined text-[32px] text-secondary animate-spin">progress_activity</span>
          <div>
            <h3 class="font-title-md font-bold">${isHi ? 'AI पौधे की पहचान कर रहा है...' : 'Running Botanical Classification AI...'}</h3>
            <p class="font-body-sm text-on-surface-variant">${isHi ? 'पत्ती की नसों, आकार और विशेषताओं का विश्लेषण.' : 'Analyzing leaf morphology and venation with MobileNetV3.'}</p>
          </div>
        </div>
      `;

      try {
        const formData = new FormData();
        formData.append('image', file);

        const res = await fetch('http://127.0.0.1:8000/api/v1/crop-id/identify', {
          method: 'POST',
          body: formData
        });

        if (!res.ok) throw new Error('API returned HTTP ' + res.status);
        const data = await res.json();

        if (data.identified) {
          resultBox.innerHTML = `
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-space-lg">
              <div class="flex items-center gap-space-md">
                <div class="w-20 h-20 rounded-2xl overflow-hidden bg-surface-container-highest shrink-0 border border-outline-variant/20">
                  <img src="${previewUrl}" class="w-full h-full object-cover"/>
                </div>
                <div class="flex flex-col">
                  <div class="flex items-center gap-space-xs flex-wrap">
                    <h3 class="font-headline-sm text-primary font-bold">
                      ${isHi ? `यह पौधा ${data.crop} लगता है.` : `This plant is ${data.crop}.`}
                    </h3>
                    <span class="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm font-bold">
                      ${isHi ? 'AI का भरोसा:' : 'AI Confidence:'} ${Math.round(data.confidence * 100)}%
                    </span>
                  </div>
                  <span class="font-title-sm italic text-on-surface-variant mt-0.5">${data.botanical_name || data.scientific_name || ''}</span>
                  <details class="mt-2 text-body-sm text-on-surface">
                    <summary class="text-primary font-bold cursor-pointer hover:underline">
                      ℹ️ ${isHi ? 'और जानकारी (कुल और उपयोग)' : 'More Botanical Details'}
                    </summary>
                    <div class="mt-1 p-2 rounded-xl bg-surface-container-low text-body-sm">
                      <p><strong>${isHi ? 'कुल (Family):' : 'Family:'}</strong> ${data.family || 'Solanaceae'}</p>
                      <p><strong>${isHi ? 'प्रजातियां (Cultivars):' : 'Common Cultivars:'}</strong> ${data.common_cultivars ? data.common_cultivars.join(', ') : 'Standard Indian varieties'}</p>
                    </div>
                  </details>
                </div>
              </div>
              <button onclick="window.location.hash='#crop-scanner'" class="flex items-center gap-1.5 px-space-md py-2.5 rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container transition-all shrink-0">
                <span class="material-symbols-outlined text-[18px]">document_scanner</span>
                <span>${isHi ? 'इसकी बीमारी जांचें' : 'Check for Diseases'}</span>
              </button>
            </div>
          `;
        } else {
          resultBox.innerHTML = `
            <div class="bg-amber-50 border border-amber-300 rounded-3xl p-space-lg shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-space-md">
              <div class="flex items-center gap-space-md">
                <div class="w-14 h-14 rounded-2xl bg-amber-100 text-amber-900 flex items-center justify-center shrink-0">
                  <span class="material-symbols-outlined text-[32px]">help</span>
                </div>
                <div class="flex flex-col">
                  <span class="font-title-md font-bold text-amber-950">
                    ${isHi ? 'पौधे की पहचान अस्पष्ट है' : 'Uncertain Plant Match'} (${Math.round(data.confidence * 100)}%)
                  </span>
                  <p class="font-body-sm text-amber-900 mt-0.5">
                    ${isHi ? 'कृपया पत्ती की और साफ, सीधी और पास की फोटो खींचकर दोबारा प्रयास करें.' : 'Please take a clearer, closer photo with better lighting.'}
                  </p>
                </div>
              </div>
              <button onclick="document.querySelector('#crop-id-file-input').click()" class="px-space-md py-2 rounded-xl bg-surface-container-lowest text-amber-950 font-label-md font-bold hover:bg-surface-container transition-all shrink-0">
                ${isHi ? 'दूसरी फोटो लें' : 'Try Another Photo'}
              </button>
            </div>
          `;
        }
      } catch (err) {
        resultBox.innerHTML = `
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 text-on-surface">
            <span class="text-error font-bold">Notice:</span>
            <span class="text-on-surface-variant ml-1">${err.message}</span>
          </div>
        `;
      }
    });
  }
};
