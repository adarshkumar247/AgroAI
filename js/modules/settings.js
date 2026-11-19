// Settings & Profile Module - Kisan-First Profile Avatar & Farm Configuration
window.AgroModules = window.AgroModules || {};

window.AgroModules['settings'] = {
  render: async function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    let currentUser = window.AgroAuth ? window.AgroAuth.getUser() : null;

    // Fetch fresh user profile if token exists
    try {
      const token = window.AgroAuth ? window.AgroAuth.getToken() : null;
      if (token) {
        const res = await fetch('http://127.0.0.1:8000/api/v1/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const freshData = await res.json();
          currentUser = freshData;
          if (window.AgroAuth) {
            window.AgroAuth.setAuth(token, freshData);
          }
        }
      }
    } catch (e) {
      console.warn('Profile fetch notice:', e);
    }

    const name = (currentUser && currentUser.full_name) || (isHi ? 'रमेश पटेल' : 'Ramesh Patel');
    const email = (currentUser && currentUser.email) || 'ramesh@agrofield.ai';
    const location = (currentUser && currentUser.location) || (isHi ? 'लखनऊ फार्म, उत्तर प्रदेश' : 'Lucknow Farm, Uttar Pradesh');
    const language = (currentUser && currentUser.preferred_language) || 'Hindi (HI)';
    const farmName = (currentUser && currentUser.farm_name) || (isHi ? 'पटेल कृषि फार्म' : 'Patel Krishi Farm');
    const mainCrop = (currentUser && currentUser.main_crop) || (isHi ? 'गेहूं / धान' : 'Wheat / Rice');
    const farmSize = (currentUser && currentUser.farm_size) || (isHi ? '5 एकड़' : '5 Acres');
    const avatarUrl = window.AgroAuth.getAvatarUrl(currentUser);

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-5xl mx-auto w-full">
          <!-- Top Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
                <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Dashboard'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'प्रोफाइल और सेटिंग्स' : 'Profile & Settings'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'किसान प्रोफाइल और खेत की जानकारी' : 'Farmer Profile & Settings'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ${isHi ? 'अपनी प्रोफाइल फोटो, नाम, खेत का पता और भाषा प्रबंधित करें.' : 'Manage your profile photo, farm name, location, and regional language.'}
              </p>
            </div>
            
            <div class="flex items-center gap-space-sm">
              <button id="profile-logout-btn" class="flex items-center gap-1.5 px-space-md py-2.5 rounded-xl bg-error-container/80 hover:bg-error-container text-on-error-container font-label-md font-bold transition-all shadow-xs">
                <span class="material-symbols-outlined text-[18px]">logout</span>
                <span>${isHi ? 'लॉग आउट' : 'Sign Out'}</span>
              </button>
            </div>
          </div>

          <!-- Toast Banner -->
          <div id="settings-toast" class="hidden p-space-md rounded-2xl bg-secondary-container text-on-secondary-container flex items-center justify-between shadow-xs transition-all">
            <div class="flex items-center gap-space-sm">
              <span class="material-symbols-outlined text-secondary">check_circle</span>
              <span id="settings-toast-msg" class="font-body-md font-semibold">Changes saved successfully.</span>
            </div>
            <button onclick="document.getElementById('settings-toast').classList.add('hidden')" class="text-on-secondary-container hover:opacity-75">
              <span class="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <!-- 1. Profile Photo Management Card -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-[0_4px_24px_rgba(0,0,0,0.03)] flex flex-col md:flex-row items-center gap-space-lg">
            <input type="file" id="avatar-file-input" accept="image/jpeg,image/png,image/webp" class="hidden" />
            
            <div class="relative flex-shrink-0">
              <img id="settings-avatar-preview" src="${avatarUrl}" class="w-28 h-28 rounded-full object-cover ring-4 ring-primary/20 shadow-md bg-surface-container" alt="Farmer Profile"/>
              <span class="absolute bottom-1 right-1 w-5 h-5 rounded-full bg-secondary ring-2 ring-white" title="Active"></span>
            </div>
            
            <div class="flex-1 flex flex-col gap-2 text-center md:text-left z-10">
              <div class="flex items-center justify-center md:justify-start gap-space-xs flex-wrap">
                <h2 class="font-headline-md text-on-surface font-extrabold">${name}</h2>
                <span class="px-space-xs py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm font-bold">
                  ${isHi ? 'सत्यापित किसान' : 'Verified Farmer'}
                </span>
              </div>
              <p class="font-body-md text-on-surface-variant">${email}</p>
              
              <!-- Avatar Actions -->
              <div class="flex flex-wrap items-center justify-center md:justify-start gap-space-sm mt-2">
                <button id="choose-avatar-btn" type="button" class="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-on-primary font-label-md font-bold hover:bg-primary-container shadow-xs transition-all">
                  <span class="material-symbols-outlined text-[18px]">photo_camera</span>
                  <span>${isHi ? 'अपनी फोटो लगाएं' : 'Upload Photo'}</span>
                </button>
                <button id="save-avatar-btn" type="button" class="hidden flex items-center gap-1.5 px-4 py-2 rounded-xl bg-secondary text-on-secondary font-label-md font-bold hover:bg-secondary-container hover:text-on-secondary-container transition-all">
                  <span class="material-symbols-outlined text-[18px]">save</span>
                  <span>${isHi ? 'फोटो सेव करें' : 'Save Photo'}</span>
                </button>
                ${currentUser && currentUser.profile_photo_url ? `
                  <button id="remove-avatar-btn" type="button" class="flex items-center gap-1 px-3 py-2 rounded-xl bg-surface-container hover:bg-error-container hover:text-error text-on-surface-variant font-label-md font-semibold transition-all">
                    <span class="material-symbols-outlined text-[16px]">delete</span>
                    <span>${isHi ? 'फोटो हटाएं' : 'Remove Photo'}</span>
                  </button>
                ` : ''}
              </div>
            </div>
          </div>

          <!-- 2. Profile Details Form -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-[0_4px_24px_rgba(0,0,0,0.03)] flex flex-col gap-space-lg">
            <div class="flex items-center justify-between pb-space-sm border-b border-surface-container">
              <div class="flex items-center gap-space-xs text-primary font-title-lg font-bold">
                <span class="material-symbols-outlined text-[24px]">manage_accounts</span>
                <span>${isHi ? 'प्रोफाइल व खेत का विवरण' : 'Edit Account & Farm Details'}</span>
              </div>
            </div>

            <form id="profile-edit-form" class="flex flex-col gap-space-lg">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                <!-- Full Name -->
                <div class="flex flex-col gap-space-xs">
                  <label class="font-label-md text-on-surface font-bold" for="input-fullname">${isHi ? 'पूरा नाम' : 'Full Name'}</label>
                  <input id="input-fullname" type="text" value="${name}" required
                    class="w-full px-4 py-3 rounded-2xl bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:bg-surface-container-lowest text-on-surface font-body-md transition-all outline-none" />
                </div>

                <!-- Email (Read-Only) -->
                <div class="flex flex-col gap-space-xs">
                  <div class="flex items-center justify-between">
                    <label class="font-label-md text-on-surface font-bold" for="input-email">${isHi ? 'ईमेल पता' : 'Email Address'}</label>
                    <span class="font-label-sm text-[11px] text-outline font-semibold">${isHi ? 'केवल पढ़ने के लिए' : 'Read-only'}</span>
                  </div>
                  <input id="input-email" type="email" value="${email}" readonly
                    class="w-full px-4 py-3 rounded-2xl bg-surface-container-high/60 border border-outline-variant/20 text-on-surface-variant font-body-md cursor-not-allowed outline-none" />
                </div>

                <!-- Farm Location -->
                <div class="flex flex-col gap-space-xs">
                  <label class="font-label-md text-on-surface font-bold" for="input-location">${isHi ? 'खेत का स्थान / पता' : 'Farm Location'}</label>
                  <input id="input-location" type="text" value="${location}" required
                    class="w-full px-4 py-3 rounded-2xl bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:bg-surface-container-lowest text-on-surface font-body-md transition-all outline-none" />
                  <span class="text-[12px] text-on-surface-variant">${isHi ? 'सटीक मौसम पूर्वानुमान के लिए उपयोगी.' : 'Used for local Open-Meteo weather lookups.'}</span>
                </div>

                <!-- Preferred Language -->
                <div class="flex flex-col gap-space-xs">
                  <label class="font-label-md text-on-surface font-bold" for="select-language">${isHi ? 'पसंदीदा भाषा' : 'Preferred Language'}</label>
                  <select id="select-language"
                    class="w-full px-4 py-3 rounded-2xl bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:bg-surface-container-lowest text-on-surface font-body-md transition-all outline-none">
                    <option value="Hindi (HI)" ${language.includes('Hindi') ? 'selected' : ''}>Hindi / हिन्दी (HI)</option>
                    <option value="English (EN)" ${language === 'English (EN)' ? 'selected' : ''}>English (EN)</option>
                  </select>
                </div>

                <!-- Farm Name -->
                <div class="flex flex-col gap-space-xs">
                  <label class="font-label-md text-on-surface font-bold" for="input-farm-name">${isHi ? 'खेत / फार्म का नाम' : 'Farm Name'}</label>
                  <input id="input-farm-name" type="text" value="${farmName}"
                    class="w-full px-4 py-3 rounded-2xl bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:bg-surface-container-lowest text-on-surface font-body-md transition-all outline-none" />
                </div>

                <!-- Main Crop -->
                <div class="flex flex-col gap-space-xs">
                  <label class="font-label-md text-on-surface font-bold" for="input-main-crop">${isHi ? 'मुख्य फसल' : 'Main Crop'}</label>
                  <input id="input-main-crop" type="text" value="${mainCrop}"
                    class="w-full px-4 py-3 rounded-2xl bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:bg-surface-container-lowest text-on-surface font-body-md transition-all outline-none" />
                </div>
              </div>

              <!-- Save Changes CTA -->
              <div class="flex items-center justify-end gap-space-sm pt-space-sm border-t border-surface-container">
                <button type="submit" id="save-profile-btn" class="flex items-center gap-space-xs px-space-lg py-3 rounded-2xl bg-primary text-on-primary font-label-lg font-bold hover:bg-primary-container transition-all shadow-xs">
                  <span class="material-symbols-outlined text-[20px]">save</span>
                  <span>${isHi ? 'जानकारी सेव करें' : 'Save Profile Updates'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    `;

    // Hook up elements
    const avatarInput = container.querySelector('#avatar-file-input');
    const chooseAvatarBtn = container.querySelector('#choose-avatar-btn');
    const saveAvatarBtn = container.querySelector('#save-avatar-btn');
    const removeAvatarBtn = container.querySelector('#remove-avatar-btn');
    const avatarPreview = container.querySelector('#settings-avatar-preview');
    const toast = container.querySelector('#settings-toast');
    const toastMsg = container.querySelector('#settings-toast-msg');

    let pendingAvatarFile = null;

    chooseAvatarBtn?.addEventListener('click', () => {
      avatarInput?.click();
    });

    avatarInput?.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        pendingAvatarFile = e.target.files[0];
        avatarPreview.src = URL.createObjectURL(pendingAvatarFile);
        if (saveAvatarBtn) saveAvatarBtn.classList.remove('hidden');
      }
    });

    saveAvatarBtn?.addEventListener('click', async () => {
      if (!pendingAvatarFile) return;
      const token = window.AgroAuth ? window.AgroAuth.getToken() : null;
      saveAvatarBtn.disabled = true;
      saveAvatarBtn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">sync</span><span>Uploading...</span>';

      try {
        const formData = new FormData();
        formData.append('file', pendingAvatarFile);
        const res = await fetch('http://127.0.0.1:8000/api/v1/auth/profile/photo', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });

        if (res.ok) {
          const updatedUser = await res.json();
          window.AgroAuth.setAuth(token, updatedUser);
          if (toast && toastMsg) {
            toastMsg.innerText = isHi ? 'प्रोफाइल फोटो सफलतापूर्वक अपडेट हुई!' : 'Profile photo updated successfully!';
            toast.classList.remove('hidden');
          }
          setTimeout(() => {
            window.AgroModules.settings.render(container, state);
          }, 600);
        } else {
          const err = await res.json();
          alert(err.detail || 'Photo upload failed');
        }
      } catch (e) {
        alert('Photo upload error: ' + e.message);
      } finally {
        saveAvatarBtn.disabled = false;
      }
    });

    removeAvatarBtn?.addEventListener('click', async () => {
      if (!confirm(isHi ? 'क्या आप फोटो हटाकर डिफ़ॉल्ट अवतार लगाना चाहते हैं?' : 'Remove photo and revert to default avatar?')) return;
      const token = window.AgroAuth ? window.AgroAuth.getToken() : null;
      try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/auth/profile/photo', {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const updatedUser = await res.json();
          window.AgroAuth.setAuth(token, updatedUser);
          setTimeout(() => {
            window.AgroModules.settings.render(container, state);
          }, 400);
        }
      } catch (e) {
        alert('Photo removal error: ' + e.message);
      }
    });

    // Profile form submission
    const profileForm = container.querySelector('#profile-edit-form');
    profileForm?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const token = window.AgroAuth ? window.AgroAuth.getToken() : null;
      const newName = container.querySelector('#input-fullname').value.trim();
      const newLocation = container.querySelector('#input-location').value.trim();
      const newLang = container.querySelector('#select-language').value;
      const newFarmName = container.querySelector('#input-farm-name').value.trim();
      const newMainCrop = container.querySelector('#input-main-crop').value.trim();

      const saveBtn = container.querySelector('#save-profile-btn');
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="material-symbols-outlined text-[20px] animate-spin">sync</span><span>Saving...</span>';
      }

      try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/auth/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            full_name: newName,
            location: newLocation,
            preferred_language: newLang,
            farm_name: newFarmName,
            main_crop: newMainCrop
          })
        });

        if (res.ok) {
          const updated = await res.json();
          window.AgroAuth.setAuth(token, updated);
          // Also sync language switcher if changed
          if (newLang.includes('Hindi')) {
            window.AgroI18n.setLanguage('hi');
          } else {
            window.AgroI18n.setLanguage('en');
          }
          if (toast && toastMsg) {
            toastMsg.innerText = isHi ? 'प्रोफाइल विवरण सेव हो गया!' : 'Profile details updated successfully!';
            toast.classList.remove('hidden');
          }
          setTimeout(() => {
            window.AgroModules.settings.render(container, state);
          }, 800);
        }
      } catch (err) {
        alert('Error saving profile: ' + err.message);
      } finally {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = `<span class="material-symbols-outlined text-[20px]">save</span><span>${isHi ? 'जानकारी सेव करें' : 'Save Profile Updates'}</span>`;
        }
      }
    });

    container.querySelector('#profile-logout-btn')?.addEventListener('click', () => {
      if (confirm(isHi ? 'क्या आप सचमुच लॉग आउट करना चाहते हैं?' : 'Are you sure you want to sign out?')) {
        window.AgroAuth.logout();
      }
    });
  }
};

window.AgroModules['help-and-support'] = {
  render: function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-5xl mx-auto w-full">
          <div class="flex flex-col gap-space-xs">
            <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
              <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Dashboard'}</a>
              <span class="material-symbols-outlined text-[14px]">chevron_right</span>
              <span class="text-primary font-semibold">${isHi ? 'मदद और सहायता' : 'Help & Support'}</span>
            </div>
            <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
              ${isHi ? 'किसान सहायता व मार्गदर्शन' : 'Agricultural Support & Guidance'}
            </h1>
            <p class="font-body-md text-on-surface-variant">
              ${isHi ? 'कृषि विभाग हेल्पलाइन, फसल रोग मार्गदर्शिका एवं तकनीकी सहायता.' : 'Government kisan extension helplines, pathology field guides, and system documentation.'}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-sm">
              <div class="w-12 h-12 rounded-2xl bg-secondary-container text-secondary flex items-center justify-center">
                <span class="material-symbols-outlined text-[24px]">call</span>
              </div>
              <h3 class="font-title-md font-bold text-on-surface mt-2">${isHi ? 'किसान कॉल सेंटर (टोल-फ्री हेल्पलाइन)' : 'Kisan Call Center Helpline'}</h3>
              <p class="font-body-md text-on-surface-variant">${isHi ? 'कृषि वैज्ञानिकों से सीधे बातचीत और सलाह के लिए निःशुल्क नंबर.' : 'Direct telephone advisory for Indian farmers.'}</p>
              <span class="font-title-lg font-bold text-primary mt-2">1800-180-1551</span>
            </div>

            <div class="bg-surface-container-lowest rounded-3xl p-space-lg border border-outline-variant/30 shadow-xs flex flex-col gap-space-sm">
              <div class="w-12 h-12 rounded-2xl bg-primary-fixed text-primary flex items-center justify-center">
                <span class="material-symbols-outlined text-[24px]">menu_book</span>
              </div>
              <h3 class="font-title-md font-bold text-on-surface mt-2">${isHi ? 'पत्ती रोग मार्गदर्शिका' : 'Leaf Pathology Atlas'}</h3>
              <p class="font-body-md text-on-surface-variant">${isHi ? 'अर्ली ब्लाइट, पाउडरी मिल्ड्यू और लीफ स्पॉट की फोटो देखकर पहचानें.' : 'Visual diagnostic guide for major crop diseases.'}</p>
              <button onclick="window.location.hash='#crop-scanner'" class="text-secondary font-bold hover:underline mt-2 text-left">${isHi ? 'रोग जांच शुरू करें →' : 'Open Crop Scanner →'}</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
