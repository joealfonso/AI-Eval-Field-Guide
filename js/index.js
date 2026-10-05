/* Laws index: Grid / By category view, role filter, since-last-visit markers. */
(function () {
  'use strict';

  var main = document.querySelector('[data-page="index"]');
  if (!main) return;

  var params = new URLSearchParams(window.location.search);
  var state = {
    view: params.get('view') === 'category' ? 'category' : 'grid',
    role: ['building', 'buying', 'designing'].indexOf(params.get('role')) !== -1 ? params.get('role') : 'all'
  };

  var viewBtns = main.querySelectorAll('[data-view-btn]');
  var roleBtns = main.querySelectorAll('[data-role-btn]');
  var panels = main.querySelectorAll('[data-view-panel]');
  var heroes = main.querySelectorAll('[data-hero]');
  var jump = main.querySelector('[data-jump]');
  var status = main.querySelector('[data-status]');
  var items = main.querySelectorAll('[data-roles]');

  function matches(el) {
    return state.role === 'all' || el.getAttribute('data-roles').split(' ').indexOf(state.role) !== -1;
  }

  function updateUrl() {
    var p = new URLSearchParams();
    if (state.view !== 'grid') p.set('view', state.view);
    if (state.role !== 'all') p.set('role', state.role);
    var q = p.toString();
    try { window.history.replaceState(null, '', window.location.pathname + (q ? '?' + q : '') + window.location.hash); } catch (e) { /* file:// */ }
  }

  function apply() {
    Array.prototype.forEach.call(viewBtns, function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view-btn') === state.view)); });
    Array.prototype.forEach.call(roleBtns, function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-role-btn') === state.role)); });
    Array.prototype.forEach.call(panels, function (p) { p.hidden = p.getAttribute('data-view-panel') !== state.view; });
    Array.prototype.forEach.call(heroes, function (h) { h.hidden = h.getAttribute('data-hero') !== state.view; });
    if (jump) jump.hidden = state.view !== 'grid';

    var visible = 0;
    Array.prototype.forEach.call(items, function (el) {
      var show = matches(el);
      var holder = el.closest('li') || el;
      holder.hidden = !show;
      if (show && el.closest('[data-view-panel="' + state.view + '"]')) visible++;
    });

    // per-category counts and empty categories
    Array.prototype.forEach.call(main.querySelectorAll('.category'), function (sec) {
      var cards = sec.querySelectorAll('.law-card');
      var shown = Array.prototype.filter.call(cards, matches).length;
      sec.hidden = shown === 0;
      var count = sec.querySelector('[data-count]');
      count.textContent = state.role === 'all' ? cards.length + ' of ' + cards.length + ' published' : shown + ' of ' + cards.length + ' shown';
    });
    Array.prototype.forEach.call(main.querySelectorAll('.catcol'), function (col) {
      var entries = col.querySelectorAll('.catcol__entry');
      var shown = Array.prototype.filter.call(entries, matches).length;
      col.hidden = shown === 0;
      col.querySelector('[data-count]').textContent = shown + ' of ' + entries.length;
    });

    if (status) {
      status.textContent = state.role === 'all'
        ? 'Showing all ' + main.getAttribute('data-total') + ' laws.'
        : 'Showing ' + visible + ' laws for ' + state.role + '.';
    }
  }

  Array.prototype.forEach.call(viewBtns, function (b) {
    b.addEventListener('click', function () { state.view = b.getAttribute('data-view-btn'); apply(); updateUrl(); });
  });
  Array.prototype.forEach.call(roleBtns, function (b) {
    b.addEventListener('click', function () { state.role = b.getAttribute('data-role-btn'); apply(); updateUrl(); });
  });

  /* ---------- since last visit ---------- */
  var KEY = 'lai.seenThrough';
  var latest = main.getAttribute('data-updated');
  var bar = main.querySelector('[data-since]');
  var months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

  function store(get, value) {
    try {
      if (get) return window.localStorage.getItem(KEY);
      window.localStorage.setItem(KEY, value);
    } catch (e) { /* storage unavailable */ }
    return null;
  }

  function clearMarkers() {
    Array.prototype.forEach.call(main.querySelectorAll('[data-badge]'), function (b) { b.hidden = true; b.textContent = ''; });
  }

  function sinceVisit() {
    var seen = store(true);
    if (!seen) { store(false, latest); return; }
    var added = 0, revised = 0;
    Array.prototype.forEach.call(main.querySelectorAll('.law-card'), function (card) {
      var pub = card.getAttribute('data-published'), rev = card.getAttribute('data-revised');
      var kind = pub > seen ? 'New' : (rev && rev > seen ? 'Revised' : '');
      if (!kind) return;
      if (kind === 'New') added++; else revised++;
      var no = card.getAttribute('data-no');
      Array.prototype.forEach.call(main.querySelectorAll('[data-no="' + no + '"] [data-badge]'), function (b) { b.textContent = kind; b.hidden = false; });
    });
    if (!added && !revised) return;
    var parts = [];
    if (added) parts.push(added + (added === 1 ? ' new law' : ' new laws'));
    if (revised) parts.push(revised + ' revised');
    var d = new Date(seen + 'T00:00:00');
    bar.querySelector('[data-since-badge]').textContent = 'Since ' + d.getDate() + ' ' + months[d.getMonth()];
    bar.querySelector('[data-since-text]').textContent = parts.join(', ') + '.';
    bar.hidden = false;
    bar.querySelector('[data-since-dismiss]').addEventListener('click', function () {
      store(false, latest);
      bar.hidden = true;
      clearMarkers();
    });
  }

  apply();
  if (bar) sinceVisit();
})();
