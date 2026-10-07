/* Claim checker: rule-based matching of a pasted claim to the laws. Rules live in data/editorial.json. */
(function () {
  'use strict';

  var page = document.querySelector('[data-page="claim"]');
  var LAI = window.LAI;
  if (!page || !LAI) return;

  var textEl = page.querySelector('#claim-text');
  var chipEls = Array.prototype.slice.call(page.querySelectorAll('[data-type]'));
  var findBtn = page.querySelector('[data-find]');
  var exportBtn = page.querySelector('[data-export]');
  var exampleBtn = page.querySelector('[data-example]');
  var resultsEl = page.querySelector('[data-results]');
  var noteEl = page.querySelector('[data-detect-note]');

  var EXAMPLE = 'Our assistant scores 94% on MMLU-Pro and beats leading models on our internal benchmark.';
  var FIT = { strong: 3, likely: 2, worth: 1 };
  var FIT_LABEL = { 3: 'Strong match', 2: 'Likely', 1: 'Worth checking' };
  var LIMIT = 8;
  var userEdited = false;
  var last = null;
  var byNo = {};
  LAI.laws.forEach(function (l) { byNo[l.no] = l; });

  function rx(src) { return new RegExp(src, 'i'); }
  function typo(s) { return String(s).replace(/(\w)'(\w)/g, '$1’$2'); }

  function detect(text) {
    return LAI.claim.types.filter(function (t) { return rx(t.detect).test(text); }).map(function (t) { return t.id; });
  }
  function active() {
    return chipEls.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.getAttribute('data-type'); });
  }
  function setChips(ids) {
    chipEls.forEach(function (c) { c.setAttribute('aria-pressed', String(ids.indexOf(c.getAttribute('data-type')) !== -1)); });
  }

  function compute(text, types) {
    var map = {};
    function add(rule) {
      var f = FIT[rule.fit];
      var m = map[rule.no];
      if (!m) { map[rule.no] = { no: rule.no, fit: f, why: rule.why, ask: rule.ask, hits: 1 }; return; }
      m.hits += 1;
      if (f > m.fit) { m.fit = f; m.why = rule.why; m.ask = rule.ask; }
    }
    LAI.claim.types.forEach(function (t) {
      if (types.indexOf(t.id) !== -1) t.laws.forEach(add);
    });
    LAI.claim.modifiers.forEach(function (m) { if (rx(m.detect).test(text)) add(m); });
    var out = Object.keys(map).map(function (k) { return map[k]; });
    out.forEach(function (r) { if (r.hits >= 2 && r.fit < 3) r.fit += 1; });
    out.sort(function (a, b) { return b.fit - a.fit || a.no.localeCompare(b.no); });
    return out;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function message(text) {
    resultsEl.innerHTML = '';
    var h = el('h2', 'visually-hidden', 'Results');
    h.id = 'results-h';
    resultsEl.appendChild(h);
    resultsEl.appendChild(el('p', 'claim__empty', text));
    exportBtn.disabled = true;
    last = null;
  }

  function show(results, text) {
    resultsEl.innerHTML = '';
    var counts = { 3: 0, 2: 0, 1: 0 };
    results.forEach(function (r) { counts[r.fit] += 1; });
    var head = el('div', 'result-head');
    var h2 = el('h2', '', results.length + (results.length === 1 ? ' pattern applies' : ' patterns apply'));
    h2.id = 'results-h';
    head.appendChild(h2);
    var parts = [];
    if (counts[3]) parts.push(counts[3] + ' strong');
    if (counts[2]) parts.push(counts[2] + ' likely');
    if (counts[1]) parts.push(counts[1] + ' worth checking');
    head.appendChild(el('p', '', parts.join(' · ')));
    if (window.LAIC) {
      var nos = results.map(function (r) { return parseInt(r.no, 10); });
      var tools = el('div', 'result-tools');
      var addAll = el('button', 'btn btn--outline btn--sm', 'Add these ' + results.length + ' to My patterns');
      addAll.type = 'button';
      addAll.addEventListener('click', function () {
        window.LAIC.addMany(nos);
        addAll.textContent = 'Added to My patterns';
        window.LAIC.announce('Added ' + results.length + ' patterns to My patterns.');
      });
      var brief = el('a', 'btn btn--outline btn--sm', 'Quick brief of these');
      brief.href = 'brief.html?laws=' + nos.slice().sort(function (a, b) { return a - b; }).join(',');
      tools.appendChild(addAll);
      tools.appendChild(brief);
      head.appendChild(tools);
    }
    resultsEl.appendChild(head);
    var more = null;
    results.forEach(function (r, idx) {
      var law = byNo[r.no];
      var row = el('div', 'result');
      if (idx >= LIMIT) row.hidden = true;
      var fit = el('div', 'result__fit', 'No. ' + r.no);
      fit.appendChild(el('span', '', FIT_LABEL[r.fit]));
      row.appendChild(fit);
      var body = el('div');
      var title = el('div', 'result__law');
      var a = el('a', '', typo(law.name));
      a.href = 'patterns/' + law.slug + '.html';
      title.appendChild(a);
      body.appendChild(title);
      body.appendChild(el('p', 'result__why', typo(r.why)));
      var ask = el('p', 'result__ask');
      ask.appendChild(el('b', '', 'ASK'));
      ask.appendChild(document.createTextNode(typo(law.questions[Math.min(r.ask, law.questions.length - 1)])));
      body.appendChild(ask);
      row.appendChild(body);
      resultsEl.appendChild(row);
    });
    if (results.length > LIMIT) {
      more = el('button', 'btn btn--outline claim__more', 'Show ' + (results.length - LIMIT) + ' more');
      more.type = 'button';
      more.addEventListener('click', function () {
        Array.prototype.forEach.call(resultsEl.querySelectorAll('.result[hidden]'), function (r) { r.hidden = false; });
        more.remove();
      });
      resultsEl.appendChild(more);
    }
    exportBtn.disabled = false;
    last = { text: text, results: results };
  }

  function find() {
    var text = textEl.value.trim();
    if (!text) { message('Paste a claim first, then choose Find patterns that apply.'); textEl.focus(); return; }
    if (!userEdited) setChips(detect(text));
    var types = active();
    var results = compute(text, types);
    if (!types.length && !results.length) { message('Choose at least one kind of claim above, then try again.'); return; }
    if (!results.length) { message('No patterns matched this claim. Try choosing a claim type above.'); return; }
    show(results, text);
  }

  chipEls.forEach(function (c) {
    c.addEventListener('click', function () {
      userEdited = true;
      c.setAttribute('aria-pressed', String(c.getAttribute('aria-pressed') !== 'true'));
      noteEl.textContent = 'Edited by you';
    });
  });
  var timer = null;
  textEl.addEventListener('input', function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(function () {
      if (!userEdited) setChips(detect(textEl.value));
    }, 150);
  });
  findBtn.addEventListener('click', find);
  exampleBtn.addEventListener('click', function () {
    textEl.value = EXAMPLE;
    userEdited = false;
    noteEl.textContent = 'Detected from the text, edit if wrong';
    find();
  });
  exportBtn.addEventListener('click', function () {
    if (!last) return;
    var lines = ['Claim under review:', last.text, '', 'Patterns that apply and what to ask:', ''];
    last.results.forEach(function (r, i) {
      var law = byNo[r.no];
      lines.push((i + 1) + '. No. ' + r.no + ' ' + law.name + ' (' + FIT_LABEL[r.fit] + ')');
      lines.push('   Why: ' + r.why);
      lines.push('   Ask: ' + law.questions[Math.min(r.ask, law.questions.length - 1)]);
      lines.push('   ' + LAI.site.baseUrl + '/patterns/' + law.slug);
      lines.push('');
    });
    var blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'claim-questions.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
})();
