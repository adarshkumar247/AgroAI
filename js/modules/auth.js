// AgroAI Authentication Module - Login & Sign Up Views
window.AgroModules = window.AgroModules || {};

window.AgroModules.auth = {
  render: function(container, state, mode = 'login') {
    const isSignup = (mode === 'signup') || (window.location.hash === '#signup');

    container.innerHTML = `
      <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-8 bg-surface">
        <div class="w-full max-w-md flex flex-col gap-space-lg">
          <!-- Logo & Brand Header -->
          <div class="flex flex-col items-center text-center gap-space-xs">
            <div class="w-14 h-14 rounded-2xl bg-primary-container/20 border border-primary/20 flex items-center justify-center p-2.5 shadow-sm">
              <img src="assets/agroai-logo.png" alt="AgroAI Logo" class="w-full h-full object-contain" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
              <span class="material-symbols-outlined text-primary text-[32px] hidden">potted_plant</span>
            </div>
            <h1 class="font-headline-md text-headline-md text-on-surface font-bold tracking-tight mt-2">
              ${isSignup ? 'Create your AgroAI Account' : 'Welcome to AgroAI'}
            </h1>
            <p class="font-body-md text-body-md text-on-surface-variant max-w-xs">
              ${isSignup ? 'Join thousands of modern growers with AI precision crop health & farm diagnostics.' : 'Sign in to access your farm diagnostics, field telemetry, and AI agronomic copilot.'}
            </p>
          </div>

          <!-- Card Surface with Elevation -->
          <div class="bg-surface-container-lowest rounded-3xl p-6 sm:p-8 shadow-[0_4px_24px_-4px_rgba(26,28,25,0.06),0_1px_2px_rgba(26,28,25,0.04)] border border-outline/10 flex flex-col gap-space-md">
            
            <!-- Alert Banner (Hidden by default) -->
            <div id="auth-alert" class="hidden p-3 rounded-xl font-label-md text-label-md flex items-center gap-2"></div>

            <!-- Demo quick-fill card removed per user preference -->

            <!-- Form -->
            <form id="auth-form" class="flex flex-col gap-space-md">
              ${isSignup ? `
                <!-- Full Name -->
                <div class="flex flex-col gap-1.5">
                  <label class="font-label-md text-label-md font-semibold text-on-surface">Full Name</label>
                  <div class="relative flex items-center">
                    <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">person</span>
                    <input id="auth-name" type="text" required placeholder="e.g. Ramesh Patel" class="w-full pl-11 pr-4 py-3 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-transparent focus:border-primary focus:bg-surface-container transition-all" />
                  </div>
                </div>
              ` : ''}

              <!-- Email -->
              <div class="flex flex-col gap-1.5">
                <label class="font-label-md text-label-md font-semibold text-on-surface">Email Address</label>
                <div class="relative flex items-center">
                  <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">mail</span>
                  <input id="auth-email" type="email" required placeholder="farmer@example.com" class="w-full pl-11 pr-4 py-3 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-transparent focus:border-primary focus:bg-surface-container transition-all" />
                </div>
              </div>

              <!-- Password -->
              <div class="flex flex-col gap-1.5">
                <div class="flex items-center justify-between">
                  <label class="font-label-md text-label-md font-semibold text-on-surface">Password</label>
                  ${!isSignup ? `
                    <button type="button" onclick="alert('Password reset instructions will be sent to your registered email.')" class="font-label-sm text-label-sm text-primary hover:underline">
                      Forgot password?
                    </button>
                  ` : ''}
                </div>
                <div class="relative flex items-center">
                  <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">lock</span>
                  <input id="auth-password" type="password" required placeholder="••••••••" minlength="6" class="w-full pl-11 pr-11 py-3 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-transparent focus:border-primary focus:bg-surface-container transition-all" />
                  <button type="button" id="toggle-pw-btn" class="absolute right-3.5 text-outline hover:text-on-surface transition-colors">
                    <span class="material-symbols-outlined text-[20px]">visibility</span>
                  </button>
                </div>
              </div>

              ${isSignup ? `
                <!-- Confirm Password -->
                <div class="flex flex-col gap-1.5">
                  <label class="font-label-md text-label-md font-semibold text-on-surface">Confirm Password</label>
                  <div class="relative flex items-center">
                    <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">lock_reset</span>
                    <input id="auth-confirm-password" type="password" required placeholder="••••••••" minlength="6" class="w-full pl-11 pr-4 py-3 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-transparent focus:border-primary focus:bg-surface-container transition-all" />
                  </div>
                </div>

                <!-- Location -->
                <div class="flex flex-col gap-1.5">
                  <label class="font-label-md text-label-md font-semibold text-on-surface">Farm Location</label>
                  <div class="relative flex items-center">
                    <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">location_on</span>
                    <input id="auth-location" type="text" placeholder="e.g. Lucknow Farm, Uttar Pradesh" value="Lucknow Farm, Uttar Pradesh" class="w-full pl-11 pr-4 py-3 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-transparent focus:border-primary focus:bg-surface-container transition-all" />
                  </div>
                </div>

                <!-- Preferred Language -->
                <div class="flex flex-col gap-1.5">
                  <label class="font-label-md text-label-md font-semibold text-on-surface">Preferred Language</label>
                  <div class="relative flex items-center">
                    <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">translate</span>
                    <select id="auth-language" class="w-full pl-11 pr-4 py-3 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-transparent focus:border-primary focus:bg-surface-container transition-all cursor-pointer">
                      <option value="English (EN)" selected>English (EN)</option>
                      <option value="Hindi (HI)">Hindi (हिन्दी)</option>
                      <option value="Bengali (BN)">Bengali (বাংলা)</option>
                      <option value="Telugu (TE)">Telugu (తెలుగు)</option>
                      <option value="Punjabi (PA)">Punjabi (ਪੰਜਾਬੀ)</option>
                    </select>
                  </div>
                </div>
              ` : `
                <!-- Remember me -->
                <div class="flex items-center gap-2 pt-1">
                  <input id="remember-me" type="checkbox" checked class="w-4 h-4 rounded text-primary focus:ring-primary accent-primary cursor-pointer" />
                  <label for="remember-me" class="font-label-md text-label-md text-on-surface-variant cursor-pointer">Remember this browser</label>
                </div>
              `}

              <!-- Submit Button -->
              <button id="auth-submit-btn" type="submit" class="mt-2 w-full py-3.5 rounded-2xl bg-primary text-on-primary font-label-lg text-label-lg font-semibold hover:bg-primary-container transition-all shadow-[0_2px_8px_rgba(0,69,13,0.25)] flex items-center justify-center gap-2 active:scale-[0.99]">
                <span>${isSignup ? 'Create Account' : 'Sign In'}</span>
                <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
              </button>
            </form>

            <!-- Switch Mode Footer -->
            <div class="pt-2 border-t border-outline/10 text-center font-body-sm text-body-sm text-on-surface-variant">
              ${isSignup ? `
                Already have an account?
                <a href="#login" class="text-primary font-semibold hover:underline ml-1">Sign In</a>
              ` : `
                Don't have an account yet?
                <a href="#signup" class="text-primary font-semibold hover:underline ml-1">Create an Account</a>
              `}
            </div>
          </div>
        </div>
      </div>
    `;

    // Elements & Handlers
    const form = container.querySelector('#auth-form');
    const alertBox = container.querySelector('#auth-alert');
    const submitBtn = container.querySelector('#auth-submit-btn');
    const fillDemoBtn = container.querySelector('#fill-demo-btn');
    const togglePwBtn = container.querySelector('#toggle-pw-btn');
    const pwInput = container.querySelector('#auth-password');

    function showAlert(msg, isError = true) {
      if (!alertBox) return;
      alertBox.className = `p-3 rounded-xl font-label-md text-label-md flex items-center gap-2 ${
        isError ? 'bg-error-container text-on-error-container' : 'bg-secondary-container text-on-secondary-container'
      }`;
      alertBox.innerHTML = `
        <span class="material-symbols-outlined text-[18px]">${isError ? 'error' : 'check_circle'}</span>
        <span>${msg}</span>
      `;
      alertBox.classList.remove('hidden');
    }

    fillDemoBtn?.addEventListener('click', () => {
      const emailInput = container.querySelector('#auth-email');
      if (emailInput) emailInput.value = 'ramesh@agrofield.ai';
      if (pwInput) pwInput.value = 'Password123!';
      showAlert('Demo credentials filled. Click Sign In to continue.', false);
    });

    togglePwBtn?.addEventListener('click', () => {
      if (!pwInput) return;
      const isPw = pwInput.type === 'password';
      pwInput.type = isPw ? 'text' : 'password';
      togglePwBtn.querySelector('span').innerText = isPw ? 'visibility_off' : 'visibility';
    });

    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      alertBox?.classList.add('hidden');

      const email = container.querySelector('#auth-email').value.trim();
      const password = pwInput.value;

      if (isSignup) {
        const fullName = container.querySelector('#auth-name').value.trim();
        const confirmPw = container.querySelector('#auth-confirm-password').value;
        const location = container.querySelector('#auth-location').value.trim();
        const lang = container.querySelector('#auth-language').value;

        if (password !== confirmPw) {
          showAlert('Passwords do not match. Please verify.', true);
          return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">sync</span><span>Creating Account...</span>`;

        try {
          const res = await fetch('http://127.0.0.1:8000/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              full_name: fullName,
              email: email,
              password: password,
              confirm_password: confirmPw,
              location: location || 'Lucknow Farm, Uttar Pradesh',
              preferred_language: lang
            })
          });

          const data = await res.json();
          if (res.ok && data.access_token) {
            window.AgroAuth.setAuth(data.access_token, data.user);
            showAlert('Account created successfully! Redirecting...', false);
            setTimeout(() => {
              window.location.hash = '#dashboard';
            }, 500);
          } else {
            showAlert(data.detail || 'Registration failed. Please try again.', true);
          }
        } catch (err) {
          showAlert('Failed to connect to backend server. Ensure API is running.', true);
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<span>Create Account</span><span class="material-symbols-outlined text-[18px]">arrow_forward</span>`;
        }

      } else {
        // Sign In
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">sync</span><span>Signing In...</span>`;

        try {
          const res = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: email,
              password: password
            })
          });

          const data = await res.json();
          if (res.ok && data.access_token) {
            window.AgroAuth.setAuth(data.access_token, data.user);
            showAlert('Signed in successfully! Redirecting...', false);
            setTimeout(() => {
              window.location.hash = '#dashboard';
            }, 400);
          } else {
            showAlert(data.detail || 'Invalid email or password.', true);
          }
        } catch (err) {
          showAlert('Failed to connect to backend server. Ensure API is running.', true);
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<span>Sign In</span><span class="material-symbols-outlined text-[18px]">arrow_forward</span>`;
        }
      }
    });
  }
};
