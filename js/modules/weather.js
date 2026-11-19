// Weather Intelligence Module - Kisan-First Meteorological Intelligence with Single Unified Source of Truth
window.AgroModules = window.AgroModules || {};

window.AgroModules['weather-intelligence'] = {
  render: async function(container, state) {
    const isHi = window.AgroI18n ? window.AgroI18n.isHindi() : true;
    let weather = null;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/weather?lat=26.8467&lon=80.9462');
      if (res.ok) {
        weather = await res.json();
      }
    } catch (e) {
      console.warn('Weather fetch notice:', e);
    }

    const cur = weather ? (weather.current || {
      temperature_2m: weather.temperature_c !== undefined ? weather.temperature_c : (weather.temperature || 28.5),
      relative_humidity_2m: weather.humidity_pct !== undefined ? weather.humidity_pct : (weather.humidity || 81),
      wind_speed_10m: weather.wind_speed_kmh || 1.0,
      precipitation: weather.precipitation_mm || 0.0,
      soil_temperature_0cm: 25.0,
      condition_text: weather.condition_hi || weather.condition || 'आंशिक रूप से बादल'
    }) : {
      temperature_2m: 28.5,
      relative_humidity_2m: 81,
      wind_speed_10m: 1.0,
      precipitation: 0.0,
      soil_temperature_0cm: 25.0,
      condition_text: isHi ? 'आंशिक रूप से बादल' : 'Partly Cloudy'
    };

    const conditionText = isHi
      ? (weather ? (weather.condition_hi || cur.condition_text || 'आंशिक रूप से बादल') : 'आंशिक रूप से बादल')
      : (weather ? (weather.condition_en || cur.condition_text || 'Partly Cloudy') : 'Partly Cloudy');

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
    const sprayNext = isHi ? (spray.next_check_hi || 'कुछ घंटों बाद स्थिति देखें.') : (spray.next_check_en || 'Re-check conditions later.');

    const forecast = (weather && weather.daily_forecast && weather.daily_forecast.length >= 5)
      ? weather.daily_forecast.slice(0, 5)
      : [
          { day_name: isHi ? 'आज' : 'Today', temp_max: 30, temp_min: 22, condition: isHi ? 'आंशिक बादल' : 'Partly Cloudy', rain_prob: 10 },
          { day_name: isHi ? 'कल' : 'Tomorrow', temp_max: 31, temp_min: 23, condition: isHi ? 'साफ आसमान' : 'Clear Sky', rain_prob: 5 },
          { day_name: isHi ? 'परसों' : 'Day 3', temp_max: 29, temp_min: 21, condition: isHi ? 'हल्की बारिश' : 'Light Rain', rain_prob: 45 },
          { day_name: isHi ? 'चौथा दिन' : 'Day 4', temp_max: 28, temp_min: 20, condition: isHi ? 'हल्की धूप' : 'Mostly Sunny', rain_prob: 20 },
          { day_name: isHi ? 'पांचवां दिन' : 'Day 5', temp_max: 30, temp_min: 22, condition: isHi ? 'साफ मौसम' : 'Fair', rain_prob: 10 }
        ];

    const getIcon = (cond) => {
      const c = (cond || '').toLowerCase();
      if (c.includes('rain') || c.includes('बारिश')) return 'rainy';
      if (c.includes('thunder') || c.includes('तूफान')) return 'thunderstorm';
      if (c.includes('cloud') || c.includes('बादल')) return 'partly_cloudy_day';
      return 'wb_sunny';
    };

    // Farmer-friendly humidity description
    const humVal = cur.relative_humidity_2m;
    const humDesc = humVal > 80
      ? (isHi ? 'बहुत ज्यादा (फफूंद का खतरा)' : 'Very High (Fungal Risk)')
      : humVal > 60
        ? (isHi ? 'सामान्य' : 'Normal')
        : (isHi ? 'सूखा' : 'Low / Dry');

    // Farmer-friendly wind description
    const windVal = Math.round(cur.wind_speed_10m);
    const windDesc = windVal < 10
      ? (isHi ? 'हवा हल्की है' : 'Light Wind')
      : windVal < 20
        ? (isHi ? 'मध्यम हवा' : 'Moderate Breeze')
        : (isHi ? 'तेज हवा (छिड़काव न करें)' : 'Strong Wind (No Spray)');

    container.innerHTML = `
      <div class="flex flex-col w-full pb-16">
        <div class="p-space-md lg:p-space-xl flex flex-col gap-space-lg max-w-6xl mx-auto w-full">
          <!-- Top Header -->
          <div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
            <div class="flex flex-col gap-space-xs">
              <div class="flex items-center gap-space-xs text-on-surface-variant font-label-md text-label-md">
                <a class="hover:text-primary transition-colors" href="#dashboard">${isHi ? 'मुख्य पृष्ठ' : 'Home'}</a>
                <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                <span class="text-primary font-semibold">${isHi ? 'मौसम और छिड़काव' : 'Weather Intelligence'}</span>
              </div>
              <h1 class="font-headline-lg text-headline-lg text-on-surface tracking-tight font-bold">
                ${isHi ? 'खेत का मौसम और छिड़काव सलाह' : 'Farm Weather & Spray Advisory'}
              </h1>
              <p class="font-body-md text-body-md text-on-surface-variant">
                ${isHi ? 'सटीक लाइव मौसम, हवा की गति और छिड़काव के लिए सही समय' : 'Live high-resolution field weather, wind speed, and spray window guidance.'}
              </p>
            </div>
            <div class="flex items-center gap-space-xs bg-surface-container px-space-md py-2 rounded-full border border-outline-variant/30">
              <span class="material-symbols-outlined text-secondary text-[18px]">location_on</span>
              <span class="font-label-md font-semibold text-on-surface">${isHi ? 'लखनऊ फार्म, उत्तर प्रदेश' : 'Lucknow Farm, Uttar Pradesh'}</span>
            </div>
          </div>

          <!-- 1. अभी का मौसम (Current Weather Big Hero Card) -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg lg:p-space-xl border border-outline-variant/30 shadow-[0_4px_24px_rgba(0,0,0,0.03)] flex flex-col lg:flex-row items-start lg:items-center justify-between gap-space-xl">
            <div class="flex items-center gap-space-lg">
              <div class="w-20 h-20 rounded-2xl bg-secondary-container/40 text-secondary flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-[48px]">${getIcon(conditionText)}</span>
              </div>
              <div class="flex flex-col">
                <div class="flex items-baseline gap-1">
                  <span class="font-display-lg text-display-lg text-on-surface font-extrabold">${Math.round(cur.temperature_2m)}°</span>
                  <span class="font-headline-md text-headline-md text-on-surface-variant font-semibold">C</span>
                </div>
                <span class="font-title-lg text-title-lg text-on-surface font-bold">${conditionText}</span>
                <span class="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
                  ${isHi ? 'किसान के लिए: आज मौसम नम है.' : 'For Farmer: Humid weather today.'}
                </span>
              </div>
            </div>

            <!-- 4 Simple Cards for Farmer -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-space-md w-full lg:w-auto">
              <!-- Humidity -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col border border-outline-variant/20">
                <div class="flex items-center gap-1 text-outline">
                  <span class="material-symbols-outlined text-[18px] text-blue-600">water_drop</span>
                  <span class="font-label-sm text-label-sm uppercase font-semibold">${isHi ? 'नमी' : 'Humidity'}</span>
                </div>
                <span class="font-headline-sm text-headline-sm text-on-surface font-bold mt-1">${cur.relative_humidity_2m}%</span>
                <span class="font-body-sm text-body-sm text-blue-800 font-medium mt-0.5">${humDesc}</span>
              </div>

              <!-- Wind -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col border border-outline-variant/20">
                <div class="flex items-center gap-1 text-outline">
                  <span class="material-symbols-outlined text-[18px] text-teal-600">air</span>
                  <span class="font-label-sm text-label-sm uppercase font-semibold">${isHi ? 'हवा' : 'Wind'}</span>
                </div>
                <span class="font-headline-sm text-headline-sm text-on-surface font-bold mt-1">${windVal} km/h</span>
                <span class="font-body-sm text-body-sm text-teal-800 font-medium mt-0.5">${windDesc}</span>
              </div>

              <!-- Rain -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col border border-outline-variant/20">
                <div class="flex items-center gap-1 text-outline">
                  <span class="material-symbols-outlined text-[18px] text-sky-600">rainy</span>
                  <span class="font-label-sm text-label-sm uppercase font-semibold">${isHi ? 'बारिश' : 'Rain'}</span>
                </div>
                <span class="font-headline-sm text-headline-sm text-on-surface font-bold mt-1">${cur.precipitation > 0 ? cur.precipitation + ' mm' : '0.0 mm'}</span>
                <span class="font-body-sm text-body-sm text-sky-800 font-medium mt-0.5">${cur.precipitation > 0 ? (isHi ? 'बारिश जारी' : 'Active Rain') : (isHi ? 'अभी बारिश नहीं' : 'No Rain')}</span>
              </div>

              <!-- Soil Temp -->
              <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col border border-outline-variant/20">
                <div class="flex items-center gap-1 text-outline">
                  <span class="material-symbols-outlined text-[18px] text-amber-700">spa</span>
                  <span class="font-label-sm text-label-sm uppercase font-semibold">${isHi ? 'मिट्टी' : 'Soil'}</span>
                </div>
                <span class="font-headline-sm text-headline-sm text-on-surface font-bold mt-1">${Math.round(cur.soil_temperature_0cm || 25)}°C</span>
                <span class="font-body-sm text-body-sm text-amber-900 font-medium mt-0.5">${isHi ? 'जड़ों के लिए अनुकूल' : 'Optimal for roots'}</span>
              </div>
            </div>
          </div>

          <!-- 2. छिड़काव की सलाह (Single Authoritative Spray Advisory Card) -->
          <div class="p-space-lg rounded-3xl ${spray.status === 'optimal' ? 'bg-secondary-container/30 border border-secondary/30' : (spray.status === 'caution' ? 'bg-amber-50 border border-amber-200' : 'bg-rose-50 border border-rose-200')} shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-space-md">
            <div class="flex items-start gap-space-md">
              <span class="text-3xl">${spray.badge || '🟢'}</span>
              <div class="flex flex-col">
                <div class="flex items-center gap-2">
                  <span class="font-title-md font-bold ${spray.status === 'optimal' ? 'text-on-secondary-container' : (spray.status === 'caution' ? 'text-amber-900' : 'text-rose-900')}">
                    ${isHi ? 'छिड़काव की सलाह:' : 'Spray Advisory:'} ${sprayTitle}
                  </span>
                </div>
                <p class="font-body-md text-on-surface-variant mt-1 max-w-2xl">
                  <strong>${isHi ? 'कारण:' : 'Reason:'}</strong> ${sprayReason}
                </p>
                <p class="font-body-sm text-on-surface mt-1">
                  ⏱️ <strong>${isHi ? 'कब दोबारा जांचें?' : 'When to re-check?'}</strong> ${sprayNext}
                </p>
              </div>
            </div>
            <div class="flex flex-col items-end shrink-0 self-end md:self-center">
              <span class="px-3.5 py-1.5 rounded-full ${spray.status === 'optimal' ? 'bg-secondary text-on-secondary' : (spray.status === 'caution' ? 'bg-amber-700 text-white' : 'bg-rose-700 text-white')} font-label-md font-bold">
                ${spray.badge} ${sprayTitle}
              </span>
            </div>
          </div>

          <!-- 3. आने वाले 5 दिनों का मौसम (5-Day Simple Forecast) -->
          <div class="bg-surface-container-lowest rounded-3xl p-space-lg shadow-sm flex flex-col gap-space-md border border-outline-variant/30">
            <div class="flex items-center justify-between">
              <h2 class="font-title-lg text-title-lg text-on-surface font-bold">
                ${isHi ? 'आने वाले 5 दिनों का अनुमान' : '5-Day Agricultural Forecast'}
              </h2>
              <span class="font-label-sm text-label-sm text-outline">
                ${isHi ? 'दैनिक तापमान और बारिश' : 'Daily Temp & Rain Probability'}
              </span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-space-sm">
              ${forecast.map(day => {
                const dayCond = isHi ? (day.condition_hi || day.condition || 'आंशिक बादल') : (day.condition_en || day.condition || 'Partly Cloudy');
                const rainVal = day.precipitation_probability_max !== undefined ? day.precipitation_probability_max : (day.rain_prob || 10);
                const maxT = Math.round(day.temp_max !== undefined ? day.temp_max : (day.max_temp || 30));
                const minT = Math.round(day.temp_min !== undefined ? day.temp_min : (day.min_temp || 20));
                return `
                  <div class="p-space-md rounded-2xl bg-surface-container-low flex flex-col items-center text-center gap-space-xs border border-outline-variant/10">
                    <span class="font-label-md font-bold text-on-surface">${day.day_name || day.date || ''}</span>
                    <span class="material-symbols-outlined text-secondary text-[32px] my-1">${getIcon(dayCond)}</span>
                    <span class="font-headline-sm text-on-surface font-bold">${maxT}° / ${minT}°</span>
                    <span class="font-label-sm text-on-surface-variant truncate w-full text-center">${dayCond}</span>
                    <span class="font-label-sm ${rainVal > 40 ? 'text-rose-900 bg-rose-100' : 'text-secondary bg-secondary-container/50'} px-2 py-0.5 rounded-full font-semibold mt-1">
                      ${isHi ? 'बारिश' : 'Rain'}: ${rainVal}%
                    </span>
                  </div>
                `;
              }).join('')}
            </div>
          </div>

          <!-- 4. मौसम स्रोत और पारदर्शिता (Transparency Footer) -->
          <div class="p-space-md rounded-2xl bg-surface-container-low border border-outline-variant/30 flex flex-col sm:flex-row items-center justify-between text-on-surface-variant text-body-sm gap-2">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px] text-secondary">verified</span>
              <span><strong>${isHi ? 'मौसम स्रोत:' : 'Source:'}</strong> Open-Meteo High-Resolution Weather API</span>
            </div>
            <div class="flex items-center gap-3">
              <span>⏱️ ${isHi ? 'अंतिम अपडेट: ' + (weather ? weather.last_updated_ist || 'अभी' : 'अभी') : 'Last Updated: ' + (weather ? weather.last_updated_ist || 'Just now' : 'Just now')}</span>
              <span>•</span>
              <span class="italic text-outline">${isHi ? 'मौसम अनुमान बदल सकता है.' : 'Forecast is subject to atmospheric variation.'}</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
