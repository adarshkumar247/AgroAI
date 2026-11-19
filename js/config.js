// AgroAI central API configuration.
//
// Local development (localhost / 127.0.0.1) automatically uses the FastAPI
// server at http://127.0.0.1:8000.
//
// Leave this empty when FastAPI serves both the frontend and the API from the
// same Render service. For a split deployment, set it to the public backend URL.
var PRODUCTION_API_BASE = '';

(function () {
  var LOCAL_API = 'http://127.0.0.1:8000';
  var host = window.location.hostname;
  var isLocal = host === 'localhost' || host === '127.0.0.1' || host === '';
  var base = window.AGROAI_API_BASE || (isLocal ? LOCAL_API : (PRODUCTION_API_BASE || window.location.origin));
  base = String(base).replace(/\/+$/, '');
  window.AGROAI_API_BASE = base;

  // Older modules still contain hard-coded localhost URLs. Rewrite them at
  // runtime so the same source works locally and in production.
  var originalFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    if (typeof input === 'string' && input.indexOf(LOCAL_API) === 0) {
      input = base + input.slice(LOCAL_API.length);
    } else if (typeof Request !== 'undefined' && input instanceof Request && input.url.indexOf(LOCAL_API) === 0) {
      input = new Request(base + input.url.slice(LOCAL_API.length), input);
    }
    return originalFetch(input, init);
  };

  function fixImages(root) {
    var scope = root || document;
    if (!scope.querySelectorAll) return;
    var images = scope.querySelectorAll('img[src]');
    for (var i = 0; i < images.length; i++) {
      var img = images[i];
      var raw = img.getAttribute('src') || '';
      var fixed = null;

      if (raw.indexOf(LOCAL_API) === 0) {
        fixed = base + raw.slice(LOCAL_API.length);
      } else if (raw.indexOf('/uploads/') === 0) {
        // Uploaded scans and profile photos are served by the backend.
        fixed = base + raw;
      }

      if (fixed && img.src !== fixed) {
        img.src = fixed;
      }
    }
  }

  function startImageFixer() {
    fixImages(document);
    if (typeof MutationObserver === 'undefined') return;
    var observer = new MutationObserver(function () {
      fixImages(document);
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['src']
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startImageFixer);
  } else {
    startImageFixer();
  }
})();
