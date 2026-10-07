/* Shared chrome: menu, responsive <details>, and the search dialog. */
(function () {
  'use strict';

  var root = document.body.getAttribute('data-root') || '';
  var isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || '');

  Array.prototype.forEach.call(document.querySelectorAll('[data-kbd]'), function (k) {
    k.textContent = isMac ? '⌘K' : 'Ctrl K';
  });

  /* ---------- mobile menu ---------- */
  var menuBtn = document.querySelector('[data-menu-toggle]');
  var nav = document.getElementById('site-nav');
  if (menuBtn && nav) {
    var setMenu = function (open) {
      nav.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
    };
    menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('is-open')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { setMenu(false); menuBtn.focus(); }
    });
    window.matchMedia('(min-width: 1181px)').addEventListener('change', function (e) { if (e.matches) setMenu(false); });
  }

  /* ---------- Tools group in the nav ---------- */
  var group = document.querySelector('.nav-group');
  var groupBtn = group && group.querySelector('[data-nav-group]');
  if (groupBtn) {
    var setGroup = function (open) {
      group.classList.toggle('is-open', open);
      groupBtn.setAttribute('aria-expanded', String(open));
    };
    groupBtn.addEventListener('click', function () { setGroup(!group.classList.contains('is-open')); });
    document.addEventListener('click', function (e) { if (!group.contains(e.target)) setGroup(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && group.classList.contains('is-open')) { setGroup(false); groupBtn.focus(); }
    });
    group.addEventListener('focusout', function (e) { if (!group.contains(e.relatedTarget)) setGroup(false); });
  }

  /* ---------- <details> that are always open on wide screens ---------- */
  function syncDetails(selector, query, mobileFirstOpen) {
    var items = document.querySelectorAll(selector);
    if (!items.length) return;
    var mq = window.matchMedia(query);
    Array.prototype.forEach.call(items, function (d) {
      var summary = d.querySelector('summary');
      if (summary) summary.addEventListener('click', function (e) { if (mq.matches) e.preventDefault(); });
    });
    var apply = function () {
      Array.prototype.forEach.call(items, function (d, i) {
        d.open = mq.matches ? true : (mobileFirstOpen && i === 0);
        var summary = d.querySelector('summary');
        if (summary) { if (mq.matches) summary.tabIndex = -1; else summary.removeAttribute('tabindex'); }
      });
    };
    apply();
    mq.addEventListener('change', apply);
  }
  syncDetails('.catcol details', '(min-width: 900px)', false);
  syncDetails('.toc', '(min-width: 1100px)', false);
  syncDetails('.aside-block', '(min-width: 700px)', true);

  /* ---------- search ---------- */
  var KIND_ORDER = { Law: 0, Section: 1, Rubric: 2, Review: 3, Changelog: 4 };
  var TYPE_FILTERS = [
    { id: 'all', label: 'All', kinds: null },
    { id: 'laws', label: 'Laws', kinds: ['Law'] },
    { id: 'sections', label: 'Sections', kinds: ['Section'] },
    { id: 'tools', label: 'Tools', kinds: ['Rubric', 'Review'] },
    { id: 'changelog', label: 'Changelog', kinds: ['Changelog'] }
  ];
  var dlg = null;
  var searchData = null;
  var loading = false;
  var state = { query: '', type: 'all', active: 0, results: [] };
  var returnFocus = null;

  function norm(s) {
    return String(s).toLowerCase().replace(/[‘’]/g, "'").replace(/[“”]/g, '"');
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function highlight(text, tokens) {
    var lower = norm(text), ranges = [];
    tokens.forEach(function (t) {
      if (!t) return;
      var from = 0, i;
      while ((i = lower.indexOf(t, from)) !== -1) { ranges.push([i, i + t.length]); from = i + t.length; }
    });
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [];
    ranges.forEach(function (r) {
      var last = merged[merged.length - 1];
      if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]); else merged.push(r.slice());
    });
    var out = '', pos = 0;
    merged.forEach(function (r) {
      out += escapeHtml(text.slice(pos, r[0])) + '<mark>' + escapeHtml(text.slice(r[0], r[1])) + '</mark>';
      pos = r[1];
    });
    return out + escapeHtml(text.slice(pos));
  }
  function snippet(text, tokens) {
    var lower = norm(text), idx = -1;
    for (var i = 0; i < tokens.length; i++) {
      var j = lower.indexOf(tokens[i]);
      if (j !== -1 && (idx === -1 || j < idx)) idx = j;
    }
    if (idx === -1) return text.slice(0, 140) + (text.length > 140 ? '…' : '');
    var start = Math.max(0, idx - 60), end = Math.min(text.length, idx + 120);
    if (start > 0) { var sp = text.indexOf(' ', start); if (sp !== -1 && sp < idx) start = sp + 1; }
    if (end < text.length) { var ep = text.lastIndexOf(' ', end); if (ep > idx) end = ep; }
    return (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');
  }

  function run() {
    var tokens = norm(state.query).split(/\s+/).filter(Boolean);
    var all = [];
    if (!tokens.length) {
      all = searchData.filter(function (e) { return e.k === 'Law'; }).map(function (e) { return { e: e, score: 0 }; });
    } else {
      searchData.forEach(function (e) {
        var title = norm(e.t), sub = norm(e.s || ''), body = norm(e.x || '');
        var hay = title + ' ' + sub + ' ' + body;
        for (var i = 0; i < tokens.length; i++) if (hay.indexOf(tokens[i]) === -1) return;
        var score = 1;
        if (title.indexOf(norm(state.query).trim()) !== -1) score += 100;
        tokens.forEach(function (t) { if (title.indexOf(t) !== -1) score += 20; if (sub.indexOf(t) !== -1) score += 5; });
        if (e.k === 'Law') score += 10;
        all.push({ e: e, score: score });
      });
    }
    all.sort(function (a, b) {
      return b.score - a.score || KIND_ORDER[a.e.k] - KIND_ORDER[b.e.k] || String(a.e.n).localeCompare(String(b.e.n));
    });
    var counts = {};
    TYPE_FILTERS.forEach(function (f) {
      counts[f.id] = f.kinds ? all.filter(function (r) { return f.kinds.indexOf(r.e.k) !== -1; }).length : all.length;
    });
    var filter = TYPE_FILTERS.filter(function (f) { return f.id === state.type; })[0];
    var shown = filter.kinds ? all.filter(function (r) { return filter.kinds.indexOf(r.e.k) !== -1; }) : all;
    state.results = shown.slice(0, 40);
    state.active = 0;
    render(tokens, counts);
  }

  function render(tokens, counts) {
    var chips = dlg.querySelector('.search-types');
    chips.innerHTML = '';
    TYPE_FILTERS.forEach(function (f) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-pressed', String(f.id === state.type));
      b.textContent = f.label + (f.id === 'all' ? ' ' + counts.all : ' ' + counts[f.id]);
      b.addEventListener('click', function () { state.type = f.id; run(); dlg.querySelector('input').focus(); });
      chips.appendChild(b);
    });
    var list = dlg.querySelector('.search-results');
    if (!state.results.length) {
      list.innerHTML = '<p class="search-empty">No matches for “' + escapeHtml(state.query) + '”. Try a law name or a word from its text.</p>';
      dlg.querySelector('input').removeAttribute('aria-activedescendant');
      return;
    }
    list.innerHTML = state.results.map(function (r, i) {
      var e = r.e;
      var title = highlight(e.t, tokens);
      var sub = e.x ? highlight(snippet(e.x, tokens), tokens) : (e.s ? highlight(e.s, tokens) : '');
      return '<a class="search-row" role="option" id="sr-' + i + '" href="' + escapeHtml(root + e.u) + '" aria-selected="' + (i === state.active) + '" data-i="' + i + '">' +
        '<span class="search-row__kind">' + escapeHtml(e.k) + ' ' + escapeHtml(e.n) + '</span>' +
        '<span><span class="search-row__title">' + title + '</span>' + (sub ? '<span class="search-row__sub">' + sub + '</span>' : '') + '</span>' +
        '<span class="search-row__go">↵ open</span></a>';
    }).join('');
    dlg.querySelector('input').setAttribute('aria-activedescendant', 'sr-' + state.active);
    Array.prototype.forEach.call(list.querySelectorAll('.search-row'), function (a) {
      a.addEventListener('mousemove', function () { setActive(+a.getAttribute('data-i'), false); });
    });
  }

  function setActive(i, scroll) {
    var rows = dlg.querySelectorAll('.search-row');
    if (!rows.length) return;
    state.active = (i + rows.length) % rows.length;
    Array.prototype.forEach.call(rows, function (r, n) { r.setAttribute('aria-selected', String(n === state.active)); });
    dlg.querySelector('input').setAttribute('aria-activedescendant', 'sr-' + state.active);
    if (scroll) rows[state.active].scrollIntoView({ block: 'nearest' });
  }

  function build() {
    var wrap = document.createElement('div');
    wrap.className = 'search-overlay';
    wrap.innerHTML =
      '<div class="search-dialog" role="dialog" aria-modal="true" aria-label="Search the laws">' +
      '<div class="search-dialog__input"><input type="text" role="combobox" aria-expanded="true" aria-controls="search-list" aria-autocomplete="list" ' +
      'placeholder="Search laws, sections, tools" autocomplete="off" spellcheck="false" aria-label="Search"><kbd>esc</kbd></div>' +
      '<div class="search-types" role="group" aria-label="Result type"></div>' +
      '<div class="search-results" id="search-list" role="listbox" aria-label="Results"></div>' +
      '<div class="search-hints"><span>↑↓ move</span><span>↵ open</span><span>' + (isMac ? '⌘' : 'Ctrl') + '↵ new tab</span></div></div>';
    document.body.appendChild(wrap);
    wrap.addEventListener('mousedown', function (e) { if (e.target === wrap) closeSearch(); });
    var input = wrap.querySelector('input');
    input.addEventListener('input', function () { state.query = input.value; run(); });
    wrap.addEventListener('keydown', onKey);
    return wrap;
  }

  function onKey(e) {
    if (e.key === 'Escape') { e.preventDefault(); closeSearch(); return; }
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive(state.active + 1, true); return; }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActive(state.active - 1, true); return; }
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
      var row = dlg.querySelectorAll('.search-row')[state.active];
      if (row) {
        e.preventDefault();
        if (e.metaKey || e.ctrlKey) window.open(row.href, '_blank', 'noopener'); else window.location.href = row.href;
      }
      return;
    }
    if (e.key === 'Tab') {
      var f = dlg.querySelectorAll('input, button');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  }

  function openSearch(trigger) {
    if (dlg) return;
    returnFocus = trigger || document.activeElement;
    dlg = build();
    document.body.classList.add('is-locked');
    var input = dlg.querySelector('input');
    input.focus();
    var start = function () { run(); };
    if (window.LAI_SEARCH) { searchData = window.LAI_SEARCH; start(); return; }
    if (loading) return;
    loading = true;
    dlg.querySelector('.search-results').innerHTML = '<p class="search-empty">Loading…</p>';
    var s = document.createElement('script');
    s.src = root + 'js/search-index.js';
    s.onload = function () { loading = false; searchData = window.LAI_SEARCH; if (dlg) { state.query = input.value; start(); } };
    s.onerror = function () { loading = false; if (dlg) dlg.querySelector('.search-results').innerHTML = '<p class="search-empty">Search could not load. Use the laws index instead.</p>'; };
    document.head.appendChild(s);
  }

  function closeSearch() {
    if (!dlg) return;
    dlg.remove();
    dlg = null;
    state.query = '';
    state.type = 'all';
    document.body.classList.remove('is-locked');
    if (returnFocus && returnFocus.focus) returnFocus.focus();
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-search-open]'), function (b) {
    b.addEventListener('click', function () { openSearch(b); });
  });
  document.addEventListener('keydown', function (e) {
    var t = e.target, typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable);
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); if (dlg) closeSearch(); else openSearch(); }
    else if (e.key === '/' && !typing && !dlg && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); openSearch(); }
  });
})();
