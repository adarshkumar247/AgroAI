// AI Agriculture Assistant Module - Kisan-First Bilingual Agronomic Copilot
window.AgroModules = window.AgroModules || {};

window.AgroModules['ai-assistant'] = {
  render: function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    const currentUser = window.AgroAuth ? window.AgroAuth.getUser() : null;
    const farmerName = currentUser && currentUser.full_name ? currentUser.full_name.split(' ')[0] : (isHi ? 'किसान भाई' : 'Farmer');

    const suggestedQuestions = isHi ? [
      'मेरी धान की पत्तियां पीली पड़ रही हैं, क्या करूं?',
      'टमाटर की पत्तियों पर गोल काले धब्बे हैं.',
      'आज खेत में पानी देना चाहिए?',
      'फसल में कीड़ा दिख रहा है, सुरक्षित दवा बताएं.'
    ] : [
      'My rice leaves are turning yellow. What should I do?',
      'Concentric dark spots on tomato leaves.',
      'Should I irrigate my fields today?',
      'Organic pest control remedies.'
    ];

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-5xl mx-auto w-full">
          <!-- Top Bar -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md">
                <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Home'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'किसान AI सहायक' : 'AI Assistant'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'किसान AI कृषि मित्र' : 'AgroAI Agricultural Copilot'}
              </h1>
              <p class="font-body-md text-on-surface-variant">
                ${isHi ? 'फसल की बीमारी, खाद, कीटनाशक या मौसम से जुड़ा कोई भी सवाल आसान हिंदी में पूछें.' : 'Ask any questions about crop diseases, pest remedies, fertilizers, or spray timing.'}
              </p>
            </div>
            <div class="flex items-center gap-space-sm bg-surface-container px-space-md py-2 rounded-full border border-outline-variant/30">
              <span class="w-2.5 h-2.5 rounded-full bg-secondary animate-pulse"></span>
              <span class="font-label-md font-semibold text-on-surface">Gemini AI Live</span>
            </div>
          </div>

          <!-- Chat Window Box -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-md lg:p-space-lg border border-outline-variant/30 shadow-xs flex flex-col h-[600px]">
            <!-- Messages Scroll Area -->
            <div id="chat-messages" class="flex-1 overflow-y-auto flex flex-col gap-space-md pr-2">
              <!-- AI Welcome Message -->
              <div class="flex items-start gap-space-sm max-w-2xl">
                <div class="w-10 h-10 rounded-2xl bg-primary text-on-primary flex items-center justify-center shrink-0 mt-1 font-bold shadow-xs">
                  <span class="material-symbols-outlined text-[22px]">smart_toy</span>
                </div>
                <div class="p-space-md rounded-2xl bg-surface-container-low text-on-surface font-body-md shadow-2xs border border-outline-variant/20">
                  <p class="font-bold text-primary mb-1">AgroAI Copilot</p>
                  <p>
                    ${isHi
                      ? `नमस्ते ${farmerName} जी! मैं आपका कृषि AI सहायक हूँ. आपकी फसलों, खेत के मौसम और पत्तियों की सेहत के बारे में कोई भी प्रश्न पूछ सकते हैं.`
                      : `Namaste ${farmerName}! I am your AI agronomist copilot. Feel free to ask about your crops, weather conditions, or pest remedies.`}
                  </p>
                  <p class="mt-2 text-on-surface-variant font-medium text-body-sm">
                    ${isHi ? 'नीचे दिए गए किसी भी सवाल पर क्लिक करें या अपना सवाल टाइप करें:' : 'Click a suggested question below or type your own question:'}
                  </p>
                </div>
              </div>
            </div>

            <!-- Suggested Quick Chips -->
            <div class="flex items-center gap-space-xs py-space-sm overflow-x-auto border-t border-outline-variant/20 pt-2">
              ${suggestedQuestions.map(q => `
                <button class="chat-suggest-chip shrink-0 px-3.5 py-1.5 rounded-full bg-surface-container-low hover:bg-surface-container text-on-surface font-label-sm border border-outline-variant/20 transition-all font-semibold active:scale-95 text-left">
                  ${q}
                </button>
              `).join('')}
            </div>

            <!-- Input Bar -->
            <div class="pt-space-xs flex items-center gap-space-sm">
              <div class="relative flex-1 flex items-center">
                <input id="chat-input" type="text" placeholder="${isHi ? 'अपना सवाल यहाँ लिखें (जैसे: धान में कौन सी खाद डालें?)...' : 'Type your agriculture question...'}" class="w-full h-12 pl-4 pr-12 rounded-2xl bg-surface-container-low text-on-surface font-body-md outline-none border border-outline-variant/30 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"/>
                <button id="send-chat-btn" class="absolute right-2 p-2 rounded-xl bg-primary text-on-primary hover:bg-primary-container transition-all flex items-center justify-center font-bold">
                  <span class="material-symbols-outlined text-[18px]">send</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    const chatMessages = container.querySelector('#chat-messages');
    const chatInput = container.querySelector('#chat-input');
    const sendBtn = container.querySelector('#send-chat-btn');

    function appendMessage(sender, text, isAI = false, meta = null) {
      const msgDiv = document.createElement('div');
      if (isAI) {
        msgDiv.className = 'flex items-start gap-space-sm max-w-2xl';
        msgDiv.innerHTML = `
          <div class="w-10 h-10 rounded-2xl bg-primary text-on-primary flex items-center justify-center shrink-0 mt-1 font-bold shadow-xs">
            <span class="material-symbols-outlined text-[22px]">smart_toy</span>
          </div>
          <div class="p-space-md rounded-2xl bg-surface-container-low text-on-surface font-body-md shadow-2xs border border-outline-variant/20">
            <div class="flex items-center justify-between gap-2 mb-1">
              <p class="font-bold text-primary">${sender}</p>
              ${meta ? `<span class="px-2 py-0.5 rounded-full bg-surface-container text-outline text-[11px] font-bold">${meta}</span>` : ''}
            </div>
            <p class="leading-relaxed whitespace-pre-wrap">${text}</p>
          </div>
        `;
      } else {
        msgDiv.className = 'flex items-start gap-space-sm max-w-2xl self-end flex-row-reverse';
        msgDiv.innerHTML = `
          <div class="w-10 h-10 rounded-2xl bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-1 font-bold shadow-xs">
            <span class="material-symbols-outlined text-[22px]">person</span>
          </div>
          <div class="p-space-md rounded-2xl bg-primary text-on-primary font-body-md shadow-2xs">
            <p>${text}</p>
          </div>
        `;
      }
      chatMessages.appendChild(msgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      return msgDiv;
    }

    async function handleSend() {
      const text = chatInput.value.trim();
      if (!text) return;
      chatInput.value = '';
      appendMessage(farmerName, text, false);

      // Thinking placeholder
      const thinkingDiv = document.createElement('div');
      thinkingDiv.className = 'flex items-start gap-space-sm max-w-2xl';
      thinkingDiv.innerHTML = `
        <div class="w-10 h-10 rounded-2xl bg-primary text-on-primary flex items-center justify-center shrink-0 mt-1">
          <span class="material-symbols-outlined text-[22px] animate-spin">sync</span>
        </div>
        <div class="p-space-md rounded-2xl bg-surface-container-low text-on-surface-variant font-body-md shadow-2xs flex items-center gap-2 border border-outline-variant/20">
          <span class="font-medium text-primary">${isHi ? 'कृषि सहायक सोच रहा है...' : 'AgroAI Copilot is analyzing...'}</span>
        </div>
      `;
      chatMessages.appendChild(thinkingDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      try {
        const activeScan = window.AgroAppState?.activeScan;
        const cropContext = activeScan ? activeScan.crop : 'Tomato';
        const res = await fetch('http://127.0.0.1:8000/api/v1/assistant/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            crop: cropContext,
            location: 'Lucknow Farm, Uttar Pradesh',
            recent_disease_scan: activeScan ? `${activeScan.possible_issue} (${Math.round((activeScan.confidence || 0.9) * 100)}% conf)` : null
          })
        });

        thinkingDiv.remove();

        if (res.ok) {
          const data = await res.json();
          const metaLabel = data.provider === 'gemini' ? `Google ${data.model}` : 'AgroAI Engine';
          appendMessage('AgroAI Copilot', data.response, true, metaLabel);
        } else {
          appendMessage('AgroAI Copilot', isHi ? 'सहायक से जुड़ने में थोड़ी समस्या आई. कृपया दोबारा पूछें.' : 'Error contacting reasoning service. Please try again.', true, 'Service Notice');
        }
      } catch (err) {
        thinkingDiv.remove();
        appendMessage('AgroAI Copilot', isHi ? 'आपके खेत की स्थिति के अनुसार: पीली पत्तियों के लिए पहले जल निकासी और नाइट्रोजन की जांच करें. अधिक नमी में दवा का छिड़काव सुबह के समय करें.' : 'Based on local field parameters, verify root drainage and apply balanced foliar spray.', true, 'Offline Fallback');
      }
    }

    sendBtn?.addEventListener('click', handleSend);
    chatInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleSend();
    });

    container.querySelectorAll('.chat-suggest-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        chatInput.value = chip.innerText.trim();
        handleSend();
      });
    });
  }
};
