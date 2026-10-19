/* Printable checklist builder. State lives in the URL: ?preset=buying&stakes=medium or ?preset=custom&patterns=1,2,3&stakes=high
   (the older ?laws= form is still read). Questions are grouped by phase and scaled by stakes; see checklist in data/editorial.json. */
(function () {
  'use strict';

  var page = document.querySelector('[data-page="checklist"]');
  var LAI = window.LAI;
  var CL = window.LAICL;
  if (!page || !LAI || !CL) return;

  var presetsEl = page.querySelector('[data-presets]');
  var gridEl = page.querySelector('[data-law-grid]');
  var summaryEl = page.querySelector('[data-customise-summary]');
  var sheetEl = page.querySelector('[data-sheet]');
  var printBtn = page.querySelector('[data-print]');
  var emptyEl = page.querySelector('[data-empty]');
  var stakesEl = page.querySelector('[data-stakes]');
  var stakesNoteEl = page.querySelector('[data-stakes-note]');
  var stakesById = {};
  CL.stakes.forEach(function (s) { stakesById[s.id] = s; });
  var byNo = {};
  LAI.laws.forEach(function (l) { byNo[parseInt(l.no, 10)] = l; });
  var allNos = LAI.laws.map(function (l) { return parseInt(l.no, 10); });
  var presetKeys = Object.keys(LAI.presets);

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function toNums(list) { return list.map(function (n) { return parseInt(n, 10); }); }

  function readStored() {
    return window.LAIC ? window.LAIC.get() : [];
  }

  var params = new URLSearchParams(window.location.search);
  var state = { preset: 'buying', selected: [], stakes: 'medium' };
  (function init() {
    var p = params.get('preset');
    var sk = params.get('stakes');
    if (sk && Object.prototype.hasOwnProperty.call(stakesById, sk)) state.stakes = sk;
    var laws = (window.LAIC ? window.LAIC.readPatternsParam(params) : (params.get('patterns') || params.get('laws') || '')).split(',').map(function (x) { return parseInt(x, 10); }).filter(function (n) { return byNo[n]; });
    if (p && Object.prototype.hasOwnProperty.call(LAI.presets, p)) {
      state.preset = p;
      state.selected = toNums(LAI.presets[p].laws);
    } else if (laws.length) {
      state.preset = 'custom';
      state.selected = laws;
    } else if (p === 'custom' && readStored().length) {
      state.preset = 'custom';
      state.selected = readStored().filter(function (n) { return byNo[n]; });
    } else {
      state.selected = toNums(LAI.presets.buying.laws);
    }
    if (p === 'custom' && laws.length) { state.preset = 'custom'; state.selected = laws; }
  })();

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function typo(s) { return String(s).replace(/(\w)'(\w)/g, '$1’$2'); }

  function questionsFor(no) {
    return byNo[no].questions.slice(0, stakesById[state.stakes].perPattern);
  }

  function questionCount() {
    return state.selected.reduce(function (n, no) { return n + questionsFor(no).length; }, 0);
  }

  function updateUrl() {
    var q = 'preset=' + state.preset + '&stakes=' + state.stakes;
    if (state.preset === 'custom') q += '&patterns=' + state.selected.slice().sort(function (a, b) { return a - b; }).join(',');
    try { window.history.replaceState(null, '', window.location.pathname + '?' + q); } catch (e) { /* file:// */ }
  }

  function renderPresets() {
    presetsEl.innerHTML = '';
    var keys = presetKeys.slice();
    if (state.preset === 'custom') keys.push('custom');
    keys.forEach(function (k) {
      var b = el('button', '', k === 'custom' ? 'Custom set' : LAI.presets[k].label);
      b.type = 'button';
      b.setAttribute('aria-pressed', String(k === state.preset));
      b.addEventListener('click', function () {
        if (k === 'custom') return;
        state.preset = k;
        state.selected = toNums(LAI.presets[k].laws);
        refresh();
      });
      presetsEl.appendChild(b);
    });
  }

  function renderStakes() {
    stakesEl.innerHTML = '';
    CL.stakes.forEach(function (st) {
      var b = el('button', '', st.label);
      b.type = 'button';
      b.setAttribute('aria-pressed', String(st.id === state.stakes));
      b.addEventListener('click', function () {
        state.stakes = st.id;
        renderStakes();
        renderCounts();
        renderSheet();
        updateUrl();
      });
      stakesEl.appendChild(b);
    });
    stakesNoteEl.textContent = stakesById[state.stakes].note;
  }

  function renderGrid() {
    gridEl.innerHTML = '';
    var sel = {};
    state.selected.forEach(function (n) { sel[n] = true; });
    LAI.laws.forEach(function (l) {
      var n = parseInt(l.no, 10);
      var label = el('label');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = !!sel[n];
      cb.addEventListener('change', function () {
        var set = {};
        state.selected.forEach(function (x) { set[x] = true; });
        if (cb.checked) set[n] = true; else delete set[n];
        state.selected = Object.keys(set).map(Number).sort(function (a, b) { return a - b; });
        state.preset = 'custom';
        renderPresets();
        renderCounts();
        renderSheet();
        updateUrl();
      });
      label.appendChild(cb);
      label.appendChild(el('span', '', l.no + ' ' + typo(l.name)));
      gridEl.appendChild(label);
    });
  }

  function renderCounts() {
    summaryEl.textContent = 'Customise patterns · ' + state.selected.length + ' of ' + LAI.laws.length + ' selected';

    var q = questionCount();
    printBtn.textContent = 'Print / save PDF · ' + q + (q === 1 ? ' question' : ' questions');
    printBtn.disabled = !state.selected.length;
    emptyEl.hidden = !!state.selected.length;
  }

  function dateText() {
    var d = new Date();
    return d.getDate() + ' ' + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getMonth()] + ' ' + d.getFullYear();
  }

  function renderSheet() {
    sheetEl.innerHTML = '';
    if (!state.selected.length) return;
    var label = state.preset === 'custom' ? 'Custom set' : LAI.presets[state.preset].label;
    var base = LAI.site.baseUrl.replace(/^https?:\/\//, '');
    var q = questionCount();

    var table = el('table', 'sheet__table');
    var tbody = el('tbody');
    var cell = el('td');
    var row = el('tr');
    var inner = el('div');

    var top = el('div', 'sheet__top');
    var left = el('div');
    var brand = el('div', 'sheet__brand');
    brand.appendChild(el('span', 'sheet__mark', '§'));
    brand.appendChild(el('span', '', 'AI Evaluation Field Guide'));
    left.appendChild(brand);
    left.appendChild(el('h2', '', 'Evaluation checklist'));
    left.appendChild(el('p', 'sheet__sub', label + ' · ' + stakesById[state.stakes].label + ' · ' + state.selected.length + (state.selected.length === 1 ? ' pattern' : ' patterns') + ' · ' + q + (q === 1 ? ' question' : ' questions')));
    var right = el('p', 'sheet__gen');
    right.appendChild(document.createTextNode('Generated ' + dateText()));
    right.appendChild(document.createElement('br'));
    right.appendChild(document.createTextNode('Patterns as of ' + LAI.site.version));
    top.appendChild(left);
    top.appendChild(right);
    inner.appendChild(top);

    var fields = el('div', 'sheet__fields');
    ['System or claim under review', 'Reviewer', 'Date'].forEach(function (f) { fields.appendChild(el('div', 'sheet__field', f)); });
    inner.appendChild(fields);
    inner.appendChild(el('p', 'sheet__intro', 'For each question, write down the evidence you were given, then mark Yes, No, or N/A. A No or an N/A is a finding: note what would change your decision. Questions marked Must ask are the ones to settle before you decide. Each pattern is explained at the address shown under its name.'));

    var n = 0;
    var mustAsk = stakesById[state.stakes].mustAsk;
    CL.phases.forEach(function (ph) {
      var laws = state.selected.filter(function (no) { return CL.phaseOf[byNo[no].no] === ph.id; });
      if (!laws.length) return;
      var head = el('h3', 'sheet__cat');
      head.appendChild(document.createTextNode(ph.label));
      head.appendChild(el('span', 'sheet__phasenote', ph.note));
      inner.appendChild(head);
      laws.forEach(function (no) {
        var l = byNo[no];
        var block = el('div', 'sheet__law');
        var lh = el('div', 'sheet__lawhead');
        lh.appendChild(el('span', 'sheet__lawno', 'No. ' + l.no));
        lh.appendChild(el('span', 'sheet__lawname', typo(l.name)));
        block.appendChild(lh);
        block.appendChild(el('p', 'sheet__quote', '“' + typo(l.aphorism) + '”'));
        block.appendChild(el('p', 'sheet__url', base + '/patterns/' + l.slug));
        questionsFor(no).forEach(function (text, qi) {
          n += 1;
          var qrow = el('div', 'sheet__q');
          qrow.appendChild(el('span', 'sheet__qn', String(n)));
          var qt = el('div');
          var qtext = el('div', 'sheet__qt');
          if (qi < mustAsk) qtext.appendChild(el('b', 'sheet__must', 'Must ask'));
          qtext.appendChild(document.createTextNode(typo(text)));
          qt.appendChild(qtext);
          qt.appendChild(el('div', 'sheet__notes'));
          qrow.appendChild(qt);
          var yn = el('div', 'sheet__yn');
          ['Yes', 'No', 'N/A'].forEach(function (t) {
            var s = el('span');
            s.appendChild(el('i'));
            s.appendChild(document.createTextNode(t));
            yn.appendChild(s);
          });
          qrow.appendChild(yn);
          block.appendChild(qrow);
        });
        inner.appendChild(block);
      });
    });

    var dec = el('div', 'sheet__decision');
    dec.appendChild(el('h3', '', 'Decision'));
    var opts = el('div', 'sheet__opts');
    ['Proceed', 'Proceed with conditions', 'Do not proceed'].forEach(function (t) {
      var s = el('span');
      s.appendChild(el('i'));
      s.appendChild(document.createTextNode(t));
      opts.appendChild(s);
    });
    dec.appendChild(opts);
    dec.appendChild(el('div', 'sheet__field', 'Conditions'));
    dec.appendChild(el('div', 'sheet__line'));
    dec.appendChild(el('div', 'sheet__line'));
    var sign = el('div', 'sheet__sign');
    sign.appendChild(el('div', '', 'Signed'));
    sign.appendChild(el('div', '', 'Date'));
    dec.appendChild(sign);
    inner.appendChild(dec);

    cell.appendChild(inner);
    row.appendChild(cell);
    tbody.appendChild(row);
    table.appendChild(tbody);

    var tfoot = el('tfoot');
    var frow = el('tr');
    var fcell = el('td');
    var foot = el('div', 'sheet__foot');
    foot.appendChild(el('span', '', 'AI Evaluation Field Guide · Evaluation checklist · ' + label));
    foot.appendChild(el('span', '', base + '/checklist · ' + LAI.site.version));
    fcell.appendChild(foot);
    frow.appendChild(fcell);
    tfoot.appendChild(frow);
    table.appendChild(tfoot);
    sheetEl.appendChild(table);
  }

  function refresh() {
    renderPresets();
    renderStakes();
    renderGrid();
    renderCounts();
    renderSheet();
    updateUrl();
  }

  printBtn.addEventListener('click', function () { window.print(); });
  refresh();
})();
