/* My laws: a set of laws saved in this browser. Shared by the index, law pages, claim checker, quick brief and checklist.
   Markup hooks: [data-pick], [data-collection-link], [data-collection-count], [data-tray], [data-tray-clear]. */
(function () {
  'use strict';

  var KEY = 'lai.collection';
  var OLD_KEY = 'lai.checklist';
  var memory = [];
  var listeners = [];
  var live = null;

  function clean(list) {
    var seen = {}, out = [];
    (Array.isArray(list) ? list : []).forEach(function (n) {
      n = parseInt(n, 10);
      if (n > 0 && n < 1000 && !seen[n]) { seen[n] = true; out.push(n); }
    });
    return out.sort(function (a, b) { return a - b; });
  }

  function load() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (raw === null) {
        var old = window.localStorage.getItem(OLD_KEY);
        if (old !== null) { raw = old; window.localStorage.setItem(KEY, old); }
      }
      memory = clean(JSON.parse(raw || '[]'));
    } catch (e) { /* storage unavailable or corrupt: keep the in-memory list */ }
  }

  function save() {
    try { window.localStorage.setItem(KEY, JSON.stringify(memory)); } catch (e) { /* storage unavailable */ }
  }

  function announce(msg) {
    if (!live) {
      live = document.createElement('p');
      live.className = 'visually-hidden';
      live.setAttribute('role', 'status');
      live.setAttribute('aria-live', 'polite');
      document.body.appendChild(live);
    }
    live.textContent = '';
    window.setTimeout(function () { live.textContent = msg; }, 30);
  }

  function lawsParam(list) { return list.length ? 'laws=' + list.join(',') : ''; }

  function linkFor(base, extra) {
    var list = clean(memory.concat(extra || []));
    var p = lawsParam(list);
    if (!p) return base;
    return base + (base.indexOf('?') === -1 ? '?' : '&') + p;
  }

  function render() {
    var count = memory.length;
    Array.prototype.forEach.call(document.querySelectorAll('[data-pick]'), function (b) {
      var n = parseInt(b.getAttribute('data-pick'), 10);
      var on = memory.indexOf(n) !== -1;
      b.setAttribute('aria-pressed', String(on));
      var mark = b.querySelector('.pick__mark');
      var text = b.querySelector('.pick__text');
      if (mark) mark.textContent = on ? '✓' : '+';
      if (text) text.textContent = on ? (b.getAttribute('data-label-on') || 'Added') : (b.getAttribute('data-label-off') || 'Add');
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-collection-link]'), function (a) {
      var extra = a.getAttribute('data-collection-extra');
      a.href = linkFor(a.getAttribute('data-collection-link'), extra ? [extra] : []);
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-collection-count]'), function (el) {
      el.textContent = String(count);
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-collection-badge]'), function (el) {
      el.hidden = count === 0;
    });
    var tray = document.querySelector('[data-tray]');
    if (tray) {
      tray.hidden = count === 0;
      document.body.classList.toggle('has-tray', count > 0);
      var word = tray.querySelector('[data-tray-word]');
      if (word) word.textContent = count === 1 ? 'pattern' : 'patterns';
    }
    listeners.forEach(function (f) { f(memory.slice()); });
  }

  function set(list) { memory = clean(list); save(); render(); }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.className = 'visually-hidden';
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      ta.remove();
      if (ok) resolve(); else reject(new Error('copy failed'));
    });
  }

  var api = {
    get: function () { return memory.slice(); },
    has: function (n) { return memory.indexOf(parseInt(n, 10)) !== -1; },
    set: set,
    add: function (n) { set(memory.concat([n])); },
    addMany: function (list) { set(memory.concat(list)); },
    remove: function (n) { n = parseInt(n, 10); set(memory.filter(function (x) { return x !== n; })); },
    toggle: function (n) { if (api.has(n)) { api.remove(n); return false; } api.add(n); return true; },
    clear: function () { set([]); },
    linkFor: linkFor,
    copy: copy,
    lawsParam: lawsParam,
    announce: announce,
    onChange: function (f) { listeners.push(f); }
  };
  window.LAIC = api;

  load();

  document.addEventListener('click', function (e) {
    var pick = e.target.closest ? e.target.closest('[data-pick]') : null;
    if (pick) {
      e.preventDefault();
      var name = pick.getAttribute('data-name') || 'Pattern';
      var added = api.toggle(pick.getAttribute('data-pick'));
      announce((added ? 'Added ' : 'Removed ') + name + '. ' + memory.length + (memory.length === 1 ? ' pattern' : ' patterns') + ' in My patterns.');
      return;
    }
    if (e.target.closest && e.target.closest('[data-tray-clear]')) {
      if (memory.length > 1 && !window.confirm('Remove all ' + memory.length + ' patterns from My patterns?')) return;
      api.clear();
      announce('My patterns cleared.');
    }
  });

  window.addEventListener('storage', function (e) {
    if (e.key === KEY) { load(); render(); }
  });

  render();
})();
