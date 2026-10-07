/* Situation finder: rule-based matching of a described situation to the laws. Rules live in data/editorial.json (situationFinder). */
(function () {
  'use strict';

  var page = document.querySelector('[data-page="situation"]');
  var LAI = window.LAI;
  if (!page || !LAI) return;

  var textEl = page.querySelector('#sit-text');
  var chipEls = Array.prototype.slice.call(page.querySelectorAll('[data-type]'));
  var findBtn = page.querySelector('[data-find]');
  var exportBtn = page.querySelector('[data-export]');
  var exampleBtn = page.querySelector('[data-example]');
  var resultsEl = page.querySelector('[data-results]');
  var noteEl = page.querySelector('[data-detect-note]');

  var EXAMPLE = LAI.situation.example;
  var FIT = { strong: 3, likely: 2, worth: 1 };
  var POINTS = { strong: 5, likely: 2, worth: 1 };
  var GROUPS = [
    { label: 'Start here', note: 'Strongest fit for your situation', size: 5 },
    { label: 'Also check', note: 'Likely to matter', size: 6 },
    { label: 'Worth a look', note: 'Check if time allows', size: Infinity }
  ];
  var LIMIT = 8;
  var userEdited = false;
  var last = null;
  var byNo = {};
  var labelOf = {};
  LAI.laws.forEach(function (l) { byNo[l.no] = l; });
  LAI.situation.types.forEach(function (t) { labelOf[t.id] = t.label; });

  function rx(src) { return new RegExp(src, 'i'); }
  function typo(s) { return String(s).replace(/(\w)'(\w)/g, '$1’$2'); }

  function detect(text) {
    return LAI.situation.types.filter(function (t) { return rx(t.detect).test(text); }).map(function (t) { return t.id; });
  }
  function active() {
    return chipEls.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.getAttribute('data-type'); });
  }
  function setChips(ids) {
    chipEls.forEach(function (c) { c.setAttribute('aria-pressed', String(ids.indexOf(c.getAttribute('data-type')) !== -1)); });
  }

  function compute(types) {
    var map = {};
    LAI.situation.types.forEach(function (t) {
      if (types.indexOf(t.id) === -1) return;
      t.laws.forEach(function (rule) {
        var f = FIT[rule.fit];
        var m = map[rule.no];
        if (!m) { map[rule.no] = { no: rule.no, fit: f, score: POINTS[rule.fit], why: rule.why, ask: rule.ask, from: [t.id] }; return; }
        m.score += POINTS[rule.fit];
        m.from.push(t.id);
        if (f > m.fit) { m.fit = f; m.why = rule.why; m.ask = rule.ask; }
      });
    });
    var out = Object.keys(map).map(function (k) { return map[k]; });
    out.sort(function (a, b) { return b.score - a.score || b.fit - a.fit || a.no.localeCompare(b.no); });
    var i = 0;
    GROUPS.forEach(function (g, gi) {
      for (var n = 0; n < g.size && i < out.length; n++, i++) out[i].group = gi;
    });
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
    h.id = 'sit-results-h';
    resultsEl.appendChild(h);
    resultsEl.appendChild(el('p', 'claim__empty', text));
    exportBtn.disabled = true;
    last = null;
  }

  function askFor(r) {
    var law = byNo[r.no];
    return law.questions[Math.min(r.ask, law.questions.length - 1)];
  }

  function show(results, text, types) {
    resultsEl.innerHTML = '';
    var counts = [0, 0, 0];
    results.forEach(function (r) { counts[r.group] += 1; });
    var head = el('div', 'result-head');
    var h2 = el('h2', '', results.length + (results.length === 1 ? ' law to check' : ' laws to check'));
    h2.id = 'sit-results-h';
    head.appendChild(h2);
    var parts = [];
    if (counts[0]) parts.push(counts[0] + ' to start with');
    if (counts[1]) parts.push(counts[1] + ' likely');
    if (counts[2]) parts.push(counts[2] + ' worth a look');
    head.appendChild(el('p', '', parts.join(' · ')));
    if (window.LAIC) {
      var nos = results.map(function (r) { return parseInt(r.no, 10); });
      var tools = el('div', 'result-tools');
      var addAll = el('button', 'btn btn--outline btn--sm', 'Add these ' + results.length + ' to My laws');
      addAll.type = 'button';
      addAll.addEventListener('click', function () {
        window.LAIC.addMany(nos);
        addAll.textContent = 'Added to My laws';
        window.LAIC.announce('Added ' + results.length + ' laws to My laws.');
      });
      var brief = el('a', 'btn btn--outline btn--sm', 'Quick brief of these');
      brief.href = 'brief.html?laws=' + nos.slice().sort(function (a, b) { return a - b; }).join(',');
      tools.appendChild(addAll);
      tools.appendChild(brief);
      head.appendChild(tools);
    }
    resultsEl.appendChild(head);

    var shown = 0;
    var more = null;
    GROUPS.forEach(function (g, gi) {
      var rows = results.filter(function (r) { return r.group === gi; });
      if (!rows.length) return;
      var gh = el('h3', 'result-group', g.label);
      gh.appendChild(el('span', '', g.note));
      var groupHidden = shown >= LIMIT;
      if (groupHidden) gh.hidden = true;
      resultsEl.appendChild(gh);
      rows.forEach(function (r) {
        var law = byNo[r.no];
        var row = el('div', 'result');
        if (shown >= LIMIT) row.hidden = true;
        shown += 1;
        var fit = el('div', 'result__fit', 'No. ' + r.no);
        row.appendChild(fit);
        var body = el('div');
        var title = el('div', 'result__law');
        var a = el('a', '', typo(law.name));
        a.href = 'laws/' + law.slug + '.html';
        title.appendChild(a);
        body.appendChild(title);
        body.appendChild(el('p', 'result__why', typo(r.why)));
        var ask = el('p', 'result__ask');
        ask.appendChild(el('b', '', 'ASK'));
        ask.appendChild(document.createTextNode(typo(askFor(r))));
        body.appendChild(ask);
        if (r.from.length > 1) {
          body.appendChild(el('p', 'result__from', 'Fits: ' + r.from.map(function (id) { return labelOf[id]; }).join(' · ')));
        }
        row.appendChild(body);
        resultsEl.appendChild(row);
      });
    });
    if (results.length > LIMIT) {
      more = el('button', 'btn btn--outline claim__more', 'Show ' + (results.length - LIMIT) + ' more');
      more.type = 'button';
      more.addEventListener('click', function () {
        Array.prototype.forEach.call(resultsEl.querySelectorAll('[hidden]'), function (r) { r.hidden = false; });
        more.remove();
      });
      resultsEl.appendChild(more);
    }
    exportBtn.disabled = false;
    last = { text: text, types: types, results: results };
  }

  function find() {
    var text = textEl.value.trim();
    if (!userEdited && text) setChips(detect(text));
    var types = active();
    if (!text && !types.length) { message('Describe your situation, or choose what applies below, then choose Find my laws.'); textEl.focus(); return; }
    if (!types.length) { message('We could not pick up a situation from that. Add detail about the stage (buying, building, launching), how you test it, or who it affects, or choose what applies above.'); return; }
    var results = compute(types);
    if (!results.length) { message('No laws matched. Try choosing a different situation above.'); return; }
    show(results, text, types);
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
    noteEl.textContent = 'Detected from your description, edit if wrong';
    find();
  });
  exportBtn.addEventListener('click', function () {
    if (!last) return;
    var lines = ['Situation:', last.text || '(chosen from the list)', '', 'Picked up: ' + last.types.map(function (id) { return labelOf[id]; }).join('; '), '', 'Laws to check and what to ask:', ''];
    last.results.forEach(function (r, i) {
      var law = byNo[r.no];
      var g = GROUPS[r.group];
      lines.push((i + 1) + '. No. ' + r.no + ' ' + law.name + ' (' + g.label + ')');
      lines.push('   Why: ' + r.why);
      lines.push('   Ask: ' + askFor(r));
      lines.push('   ' + LAI.site.baseUrl + '/laws/' + law.slug);
      lines.push('');
    });
    var blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'situation-questions.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
})();
