// Crop Scanner View - Kisan-First Clean Empty-State & MobileNetV3 AI Vision
window.AgroModules = window.AgroModules || {};

window.AgroModules.scanner = {
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
                <span class="text-primary font-semibold">${isHi ? 'फसल रोग जांच' : 'Crop Scanner'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'पौधे की फोटो लेकर बीमारी जांचें' : 'Scan Your Crop Leaf'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ${isHi ? 'खराब या दाग वाली पत्ती को साफ रोशनी में पास से दिखाएं. AI तुरंत बीमारी और उसका इलाज बताएगा.' : 'Take a clear, well-lit photo of the affected plant leaf for instant MobileNetV3 diagnosis.'}
              </p>
            </div>
            <div class="flex items-center gap-space-sm bg-surface-container px-space-md py-2 rounded-full border border-outline-variant/30">
              <span class="w-2.5 h-2.5 rounded-full bg-secondary animate-pulse"></span>
              <span class="font-label-md font-semibold text-on-surface">MobileNetV3 AI Active</span>
            </div>
          </div>

          <!-- Hidden File Inputs -->
          <input type="file" id="leaf-file-input" accept="image/*" class="hidden" />
          <input type="file" id="camera-file-input" accept="image/*" capture="environment" class="hidden" />

          <!-- 2-Column Workflow Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
            <!-- Left Panel: Photo Drop & Preview -->
            <div class="lg:col-span-7 flex flex-col gap-space-md">
              <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-md">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-secondary text-[22px]">center_focus_strong</span>
                    <h2 class="font-title-lg text-on-surface font-bold">${isHi ? 'फोटो बॉक्स' : 'Diagnostic Frame'}</h2>
                  </div>
                  <span id="scan-frame-status" class="font-label-sm text-outline font-bold bg-surface-container px-2.5 py-0.5 rounded-full">
                    ${isHi ? 'फोटो की प्रतीक्षा' : 'Awaiting Image'}
                  </span>
                </div>

                <!-- Main Drop Viewport Box (Starts Completely Empty) -->
                <div id="drop-zone" class="relative w-full aspect-[4/3] rounded-2xl overflow-hidden bg-surface-container-low border-2 border-dashed border-outline-variant/50 flex flex-col items-center justify-center p-6 text-center transition-all duration-300 group cursor-pointer hover:border-primary hover:bg-surface-container">
                  <!-- Empty State -->
                  <div id="empty-state-view" class="flex flex-col items-center gap-space-sm max-w-sm">
                    <div class="w-16 h-16 rounded-2xl bg-secondary-container/50 text-secondary flex items-center justify-center group-hover:scale-105 transition-transform">
                      <span class="material-symbols-outlined text-[36px]">add_a_photo</span>
                    </div>
                    <div class="flex flex-col gap-1 mt-2">
                      <span class="font-title-md font-bold text-on-surface">${isHi ? 'पौधे या पत्ती की फोटो जोड़ें' : 'Upload Crop Leaf Photo'}</span>
                      <p class="font-body-sm text-on-surface-variant">
                        ${isHi ? 'यहाँ क्लिक करें, या नीचे कैमरा / गैलरी से फोटो चुनें.' : 'Drag & drop image here, or click buttons below.'}
                      </p>
                    </div>
                    <div class="flex items-center gap-2 mt-3">
                      <button id="browse-btn-trigger" type="button" class="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container shadow-xs transition-all">
                        <span class="material-symbols-outlined text-[18px]">photo_library</span>
                        <span>${isHi ? '🖼️ फोटो चुनें' : 'Browse Gallery'}</span>
                      </button>
                      <button id="camera-btn-trigger" type="button" class="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md font-bold border border-outline-variant/30 transition-all">
                        <span class="material-symbols-outlined text-[18px] text-secondary">photo_camera</span>
                        <span>${isHi ? '📷 फोटो खींचें' : 'Take Photo'}</span>
                      </button>
                    </div>
                  </div>

                  <!-- Loaded Image Preview (Hidden by default) -->
                  <img id="preview-image" class="hidden w-full h-full object-contain select-none" alt="Crop preview" />

                  <!-- Reticle Overlay -->
                  <div id="reticle-overlay" class="hidden absolute inset-0 pointer-events-none">
                    <div class="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-primary rounded-tl"></div>
                    <div class="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-primary rounded-tr"></div>
                    <div class="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-primary rounded-bl"></div>
                    <div class="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-primary rounded-br"></div>
                    <div id="scanning-laser-line" class="hidden absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#91d78a] to-transparent shadow-[0_0_15px_#91d78a] transition-all"></div>
                  </div>

                  <!-- Metadata Badge -->
                  <div id="preview-meta-badge" class="hidden absolute bottom-3 left-3 bg-black/80 backdrop-blur-md text-white px-3 py-1 rounded-lg font-label-sm flex items-center gap-2">
                    <span class="material-symbols-outlined text-[14px] text-secondary-fixed">image</span>
                    <span id="meta-filename">leaf.jpg</span>
                    <span class="text-outline">•</span>
                    <span id="meta-size" class="text-secondary-fixed font-bold">1.2 MB</span>
                  </div>
                </div>

                <!-- Controls Bar -->
                <div id="image-controls-bar" class="hidden flex flex-wrap items-center justify-between gap-space-sm pt-space-xs">
                  <div class="flex items-center gap-space-xs">
                    <button id="replace-img-btn" type="button" class="flex items-center gap-1 px-3.5 py-1.5 rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface font-label-md border border-outline-variant/30 font-semibold">
                      <span class="material-symbols-outlined text-[16px] text-secondary">sync</span>
                      <span>${isHi ? 'फोटो बदलें' : 'Change Photo'}</span>
                    </button>
                    <button id="remove-img-btn" type="button" class="flex items-center gap-1 px-3.5 py-1.5 rounded-xl bg-surface-container-low hover:bg-error-container hover:text-error text-on-surface-variant font-label-md border border-outline-variant/30 font-semibold">
                      <span class="material-symbols-outlined text-[16px]">delete</span>
                      <span>${isHi ? 'हटाएं' : 'Remove'}</span>
                    </button>
                  </div>
                  <span class="text-secondary font-label-md font-bold flex items-center gap-1">
                    <span class="material-symbols-outlined text-[18px]">check_circle</span>
                    <span>${isHi ? 'फोटो तैयार है' : 'Ready to Diagnose'}</span>
                  </span>
                </div>

                <!-- Progress Bar -->
                <div id="scan-progress-box" class="hidden flex flex-col gap-2 p-4 rounded-2xl bg-surface-container-low border border-outline-variant/20">
                  <div class="flex items-center justify-between font-label-md">
                    <span id="progress-step-label" class="font-bold text-primary">${isHi ? 'AI जांच चल रही है...' : 'Running AI Diagnostics...'}</span>
                    <span id="progress-step-pct" class="font-bold text-secondary">40%</span>
                  </div>
                  <div class="w-full h-2.5 rounded-full bg-surface-container-highest overflow-hidden">
                    <div id="progress-bar-fill" class="h-full bg-primary rounded-full transition-all duration-300 w-2/5"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Panel: Crop Selection & Diagnosis Button -->
            <div class="lg:col-span-5 flex flex-col gap-space-md">
              <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-md">
                <h2 class="font-title-lg text-on-surface font-bold">${isHi ? 'फसल की जानकारी' : 'Crop Context'}</h2>

                <div class="flex flex-col gap-1.5">
                  <label class="font-label-md font-bold text-on-surface">${isHi ? 'फसल का नाम' : 'Crop Species'}</label>
                  <select id="crop-species-select" class="bg-surface-container-low px-space-md py-3 rounded-2xl font-title-sm text-on-surface border border-outline-variant/20 outline-none">
                    <option value="Tomato" selected>${isHi ? 'टमाटर (Tomato)' : 'Tomato (Solanum lycopersicum)'}</option>
                    <option value="Paddy Rice">${isHi ? 'धान / चावल (Paddy Rice)' : 'Paddy Rice (Oryza sativa)'}</option>
                    <option value="Corn / Maize">${isHi ? 'मक्का (Maize / Corn)' : 'Corn / Maize (Zea mays)'}</option>
                    <option value="Potato">${isHi ? 'आलू (Potato)' : 'Potato (Solanum tuberosum)'}</option>
                    <option value="Wheat">${isHi ? 'गेहूं (Wheat)' : 'Wheat (Triticum aestivum)'}</option>
                    <option value="Chili Pepper">${isHi ? 'मिर्च (Chili Pepper)' : 'Chili Pepper'}</option>
                  </select>
                </div>

                <div class="flex flex-col gap-1.5">
                  <label class="font-label-md font-bold text-on-surface">${isHi ? 'पत्ती पर क्या दिख रहा है? (वैकल्पिक)' : 'Observed Symptoms (Optional)'}</label>
                  <input id="symptoms-input" type="text" placeholder="${isHi ? 'जैसे: पत्ती पर काले या पीले धब्बे' : 'e.g. Brown spots, yellowing'}" value="${isHi ? 'पत्ती पर धब्बे दिखाई दे रहे हैं' : 'Concentric brown leaf spots'}" class="bg-surface-container-low px-space-md py-3 rounded-2xl font-body-md text-on-surface border border-outline-variant/20 outline-none" />
                </div>

                <!-- Run AI Analysis CTA -->
                <div class="pt-2">
                  <button id="run-ai-diagnosis-btn" type="button" disabled class="w-full py-4 rounded-2xl bg-surface-container-high text-outline font-title-md font-bold transition-all flex items-center justify-center gap-2 cursor-not-allowed">
                    <span class="material-symbols-outlined text-[24px]">psychiatry</span>
                    <span>${isHi ? 'पहले फोटो चुनें' : 'Upload Photo to Start'}</span>
                  </button>
                </div>
              </div>

              <!-- Helpful Tips for Farmers -->
              <div class="bg-surface-container-low rounded-3xl p-space-md border border-outline-variant/20 flex flex-col gap-2">
                <span class="font-label-md text-primary font-bold flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-[18px]">lightbulb</span>
                  ${isHi ? 'सटीक जांच के लिए सुझाव:' : 'Tips for Best Diagnosis:'}
                </span>
                <ul class="text-body-sm text-on-surface-variant space-y-1 list-disc pl-5">
                  <li>${isHi ? 'पत्ती को साफ रोशनी में दिखाएं (छाया न आने दें).' : 'Ensure clear, even daylight without harsh shadows.'}</li>
                  <li>${isHi ? 'कैमरा पत्ती के करीब रखें ताकि दाग साफ दिखें.' : 'Hold camera close enough for lesions to be sharp.'}</li>
                  <li>${isHi ? 'पूरी तरह सूखी या गिरी हुई पत्ती के बजाय ताजी पत्ती लें.' : 'Use fresh attached foliage rather than completely decayed debris.'}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Hook up elements
    const dropZone = container.querySelector('#drop-zone');
    const emptyStateView = container.querySelector('#empty-state-view');
    const previewImg = container.querySelector('#preview-image');
    const reticleOverlay = container.querySelector('#reticle-overlay');
    const laserLine = container.querySelector('#scanning-laser-line');
    const metaBadge = container.querySelector('#preview-meta-badge');
    const metaFilename = container.querySelector('#meta-filename');
    const metaSize = container.querySelector('#meta-size');
    const statusPill = container.querySelector('#scan-frame-status');
    const imageControlsBar = container.querySelector('#image-controls-bar');
    const progressBox = container.querySelector('#scan-progress-box');
    const progressStepLabel = container.querySelector('#progress-step-label');
    const progressStepPct = container.querySelector('#progress-step-pct');
    const progressBarFill = container.querySelector('#progress-bar-fill');
    const analyzeBtn = container.querySelector('#run-ai-diagnosis-btn');
    const fileInput = container.querySelector('#leaf-file-input');
    const cameraInput = container.querySelector('#camera-file-input');
    const cropSelect = container.querySelector('#crop-species-select');
    const symptomsInput = container.querySelector('#symptoms-input');

    let currentSelectedFile = null;

    function handleFile(file) {
      if (!file) return;
      currentSelectedFile = file;

      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewImg.classList.remove('hidden');
        emptyStateView.classList.add('hidden');
        reticleOverlay.classList.remove('hidden');
        metaBadge.classList.remove('hidden');
        imageControlsBar.classList.remove('hidden');

        dropZone.classList.remove('border-dashed', 'hover:border-primary', 'cursor-pointer');
        dropZone.classList.add('border-solid', 'border-primary/20', 'bg-black/90');

        metaFilename.innerText = file.name || 'leaf_scan.jpg';
        metaSize.innerText = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
        statusPill.innerText = isHi ? 'फोटो लोड हो गई' : 'Leaf Loaded';
        statusPill.className = 'font-label-sm text-secondary font-bold bg-secondary-container px-2.5 py-0.5 rounded-full';

        analyzeBtn.disabled = false;
        analyzeBtn.className = 'w-full py-4 rounded-2xl bg-primary text-on-primary font-title-md font-bold shadow-[0_4px_20px_rgba(0,69,13,0.35)] hover:bg-primary-container transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-[0.99]';
        analyzeBtn.innerHTML = `
          <span class="material-symbols-outlined text-[24px]">psychiatry</span>
          <span>${isHi ? 'AI से फसल रोग जांचें' : 'Run AI Crop Diagnosis'}</span>
        `;
      };
      reader.readAsDataURL(file);
    }

    function resetEmptyState() {
      currentSelectedFile = null;
      if (fileInput) fileInput.value = '';
      if (cameraInput) cameraInput.value = '';
      previewImg.src = '';
      previewImg.classList.add('hidden');
      emptyStateView.classList.remove('hidden');
      reticleOverlay.classList.add('hidden');
      metaBadge.classList.add('hidden');
      imageControlsBar.classList.add('hidden');
      progressBox.classList.add('hidden');

      dropZone.className = 'relative w-full aspect-[4/3] rounded-2xl overflow-hidden bg-surface-container-low border-2 border-dashed border-outline-variant/50 flex flex-col items-center justify-center p-6 text-center transition-all duration-300 group cursor-pointer hover:border-primary hover:bg-surface-container';

      statusPill.innerText = isHi ? 'फोटो की प्रतीक्षा' : 'Awaiting Image';
      statusPill.className = 'font-label-sm text-outline font-bold bg-surface-container px-2.5 py-0.5 rounded-full';

      analyzeBtn.disabled = true;
      analyzeBtn.className = 'w-full py-4 rounded-2xl bg-surface-container-high text-outline font-title-md font-bold transition-all flex items-center justify-center gap-2 cursor-not-allowed';
      analyzeBtn.innerHTML = `
        <span class="material-symbols-outlined text-[24px]">psychiatry</span>
        <span>${isHi ? 'पहले फोटो चुनें' : 'Upload Photo to Start'}</span>
      `;
    }

    container.querySelector('#browse-btn-trigger')?.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.click();
    });

    container.querySelector('#camera-btn-trigger')?.addEventListener('click', (e) => {
      e.stopPropagation();
      cameraInput.click();
    });

    dropZone.addEventListener('click', () => {
      if (!currentSelectedFile) {
        fileInput.click();
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0]);
      }
    });

    cameraInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0]);
      }
    });

    container.querySelector('#replace-img-btn')?.addEventListener('click', () => {
      fileInput.click();
    });

    container.querySelector('#remove-img-btn')?.addEventListener('click', () => {
      resetEmptyState();
    });

    analyzeBtn.addEventListener('click', async () => {
      if (!currentSelectedFile) return;

      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = `
        <span class="material-symbols-outlined text-[24px] animate-spin">progress_activity</span>
        <span>${isHi ? 'AI जांच चल रही है...' : 'Neural Inference Running...'}</span>
      `;

      progressBox.classList.remove('hidden');
      laserLine.classList.remove('hidden');

      let topPos = 0;
      let dir = 2;
      const laserInterval = setInterval(() => {
        topPos += dir;
        if (topPos > 95) dir = -2;
        if (topPos < 5) dir = 2;
        laserLine.style.top = `${topPos}%`;
      }, 30);

      try {
        const formData = new FormData();
        formData.append('image', currentSelectedFile);
        formData.append('crop', cropSelect ? cropSelect.value : 'Tomato');
        formData.append('symptoms', symptomsInput ? symptomsInput.value.trim() : 'Observed leaf lesions');

        const res = await fetch('http://127.0.0.1:8000/api/v1/scans', {
          method: 'POST',
          body: formData
        });

        clearInterval(laserInterval);

        if (!res.ok) {
          throw new Error('API returned HTTP ' + res.status);
        }

        const scanData = await res.json();
        scanData.previewUrl = previewImg.src;

        window.AgroAppState.activeScan = scanData;
        localStorage.setItem('agro_active_scan', JSON.stringify(scanData));

        progressStepLabel.innerText = isHi ? 'जांच पूरी! रिपोर्ट खुल रही है...' : 'Diagnosis Complete! Opening report...';
        progressStepPct.innerText = '100%';
        progressBarFill.style.width = '100%';

        setTimeout(() => {
          window.location.hash = '#health-analysis';
        }, 500);

      } catch (err) {
        clearInterval(laserInterval);
        laserLine.classList.add('hidden');
        alert((isHi ? 'जांच में समस्या आई: ' : 'Diagnostic error: ') + err.message);
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `
          <span class="material-symbols-outlined text-[24px]">psychiatry</span>
          <span>${isHi ? 'दोबारा कोशिश करें' : 'Retry AI Diagnosis'}</span>
        `;
      }
    });
  }
};
