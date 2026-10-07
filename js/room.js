/* Use it now: tap a question to copy it. */
(function () {
  'use strict';
  var status = document.querySelector('[data-room-status]');
  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return new Promise(function (res, rej) {
      var t = document.createElement('textarea');
      t.value = text; t.style.position = 'fixed'; t.style.opacity = '0';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy') ? res() : rej(); } catch (e) { rej(e); } finally { document.body.removeChild(t); }
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'), function (b) {
    var label = b.querySelector('.room__copy');
    b.addEventListener('click', function () {
      copy(b.getAttribute('data-copy')).then(function () {
        label.textContent = 'Copied';
        if (status) status.textContent = 'Question copied.';
      }, function () {
        label.textContent = 'Select to copy';
      });
      setTimeout(function () { label.textContent = 'Copy'; }, 1800);
    });
  });
})();
