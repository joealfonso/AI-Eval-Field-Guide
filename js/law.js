/* Law page: scroll-spy, permalinks, cite box, add to checklist. */
(function () {
  'use strict';

  var main = document.querySelector('[data-page="law"]');
  if (!main) return;

  var live = document.createElement('p');
  live.className = 'visually-hidden';
  live.setAttribute('role', 'status');
  live.setAttribute('aria-live', 'polite');
  document.body.appendChild(live);
  function announce(msg) { live.textContent = ''; window.setTimeout(function () { live.textContent = msg; }, 30); }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (resolve, reject) {
      var t = document.createElement('textarea');
      t.value = text;
      t.className = 'visually-hidden';
      document.body.appendChild(t);
      t.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      t.remove();
      if (ok) resolve(); else reject(new Error('copy failed'));
    });
  }

  /* ---------- scroll-spy ---------- */
  var links = {};
  Array.prototype.forEach.call(document.querySelectorAll('[data-toc]'), function (a) { links[a.getAttribute('data-toc')] = a; });
  var targets = Object.keys(links).map(function (id) { return document.getElementById(id); }).filter(Boolean);
  var current = null;
  function setCurrent(id) {
    if (id === current) return;
    current = id;
    Object.keys(links).forEach(function (k) {
      if (k === id) links[k].setAttribute('aria-current', 'location'); else links[k].removeAttribute('aria-current');
    });
    targets.forEach(function (t) { t.classList.toggle('is-current', t.id === id); });
  }
  if (targets.length) {
    var ticking = false;
    var spy = function () {
      ticking = false;
      var cur = targets[0];
      targets.forEach(function (t) { if (t.getBoundingClientRect().top <= 140) cur = t; });
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) cur = targets[targets.length - 1];
      setCurrent(cur.id);
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(spy); }
    }, { passive: true });
    window.addEventListener('resize', spy);
    spy();
  }

  /* ---------- permalinks ---------- */
  Array.prototype.forEach.call(document.querySelectorAll('.permalink'), function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href').slice(1);
      var url = window.location.origin + window.location.pathname + '#' + id;
      e.preventDefault();
      var el = document.getElementById(id);
      if (el) el.scrollIntoView();
      try { window.history.replaceState(null, '', '#' + id); } catch (err) { /* file:// */ }
      copy(url).then(function () { announce('Link copied'); }, function () { announce('Link ready in the address bar'); });
    });
  });

  /* ---------- cite box ---------- */
  var cite = document.querySelector('[data-cite]');
  if (cite) {
    var tabs = Array.prototype.slice.call(cite.querySelectorAll('[role="tab"]'));
    var copyBtn = cite.querySelector('[data-copy]');
    var select = function (tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        cite.querySelector('[data-panel="' + t.getAttribute('data-tab') + '"]').hidden = !on;
      });
      if (focus) tab.focus();
    };
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t, false); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        else if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === 'Home') n = tabs[0];
        else if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    var timer = null;
    copyBtn.addEventListener('click', function () {
      var tab = tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0];
      var text = cite.querySelector('[data-panel="' + tab.getAttribute('data-tab') + '"] code').textContent;
      copy(text).then(function () {
        copyBtn.textContent = 'Copied';
        announce('Copied to clipboard');
      }, function () {
        copyBtn.textContent = 'Press Ctrl+C';
      });
      window.clearTimeout(timer);
      timer = window.setTimeout(function () { copyBtn.textContent = 'Copy'; }, 2000);
    });
  }

  /* ---------- add to checklist ---------- */
  var KEY = 'lai.checklist';
  var no = parseInt(main.getAttribute('data-no'), 10);
  var addBtn = document.querySelector('[data-add-checklist]');
  var printLinks = document.querySelectorAll('[data-print-link]');
  function read() {
    try { return JSON.parse(window.localStorage.getItem(KEY) || '[]').filter(Number.isInteger); } catch (e) { return []; }
  }
  function write(list) {
    try { window.localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* storage unavailable */ }
  }
  function refresh() {
    var list = read();
    var has = list.indexOf(no) !== -1;
    if (addBtn) {
      addBtn.textContent = has ? 'Added ✓ (' + list.length + ')' : '+ Add to checklist';
      addBtn.setAttribute('aria-pressed', String(has));
    }
    var set = has ? list : list.concat([no]);
    set.sort(function (a, b) { return a - b; });
    Array.prototype.forEach.call(printLinks, function (a) { a.href = '../checklist.html?preset=custom&laws=' + set.join(','); });
  }
  if (addBtn) {
    addBtn.addEventListener('click', function () {
      var list = read();
      var i = list.indexOf(no);
      if (i === -1) list.push(no); else list.splice(i, 1);
      write(list);
      refresh();
      announce(i === -1 ? 'Added to checklist' : 'Removed from checklist');
    });
  }
  refresh();
})();
