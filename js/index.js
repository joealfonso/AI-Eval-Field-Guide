/* Home page: Grid / By category layout of the one pattern list, role filter, since-last-visit markers. */
(function () {
  'use strict';

  var main = document.querySelector('[data-page="index"]');
  if (!main) return;

  var params = new URLSearchParams(window.location.search);
  var state = {
    view: params.get('view') === 'category' ? 'category' : 'grid',
    role: ['building', 'buying', 'designing'].indexOf(params.get('role')) !== -1 ? params.get('role') : 'all'
  };

  var list = main.querySelector('#patterns');
  var viewBtns = main.querySelectorAll('[data-view-btn]');
  var roleBtns = main.querySelectorAll('[data-role-btn]');
  var jump = main.querySelector('[data-jump]');
  var status = main.querySelector('[data-status]');
  var items = list.querySelectorAll('[data-roles]');

  // Controls that need script are hidden in the HTML so they do not show up dead without it.
  Array.prototype.forEach.call(main.querySelectorAll('[data-js-only]'), function (el) { el.hidden = false; });

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
    main.setAttribute('data-view', state.view);
    if (jump) jump.hidden = state.view !== 'grid';

    var visible = 0;
    Array.prototype.forEach.call(items, function (el) {
      var show = matches(el);
      var holder = el.closest('li') || el;
      holder.hidden = !show;
      if (show) visible++;
    });

    // per-category counts and empty categories
    Array.prototype.forEach.call(main.querySelectorAll('.category'), function (sec) {
      var cards = sec.querySelectorAll('.law-card');
      var shown = Array.prototype.filter.call(cards, matches).length;
      sec.hidden = shown === 0;
      var count = sec.querySelector('[data-count]');
      count.textContent = state.role === 'all' ? cards.length + ' of ' + cards.length + ' published' : shown + ' of ' + cards.length + ' shown';
    });
    if (status) {
      status.textContent = state.role === 'all'
        ? 'Showing all ' + main.getAttribute('data-total') + ' patterns.'
        : 'Showing ' + visible + ' patterns for ' + state.role + '.';
    }
  }

  Array.prototype.forEach.call(viewBtns, function (b) {
    b.addEventListener('click', function () { state.view = b.getAttribute('data-view-btn'); apply(); updateUrl(); });
  });
  Array.prototype.forEach.call(roleBtns, function (b) {
    b.addEventListener('click', function () { state.role = b.getAttribute('data-role-btn'); apply(); updateUrl(); });
  });

  // "All patterns for building" links in Start here: filter in place when script runs, plain link otherwise.
  Array.prototype.forEach.call(main.querySelectorAll('[data-role-link]'), function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      state.role = a.getAttribute('data-role-link');
      apply();
      updateUrl();
      list.scrollIntoView();
    });
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
    if (added) parts.push(added + (added === 1 ? ' new pattern' : ' new patterns'));
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
