/* Claim checker: a keyword matcher that lists the patterns usually worth checking for a pasted claim.
   It is not an assessment of the claim. Scoring is in claim-match.js; rules live in data/editorial.json. */
(function () {
  'use strict';

  var page = document.querySelector('[data-page="claim"]');
  var LAI = window.LAI;
  var M = window.LAIMatch;
  if (!page || !LAI || !M) return;

  var textEl = page.querySelector('#claim-text');
  var chipEls = Array.prototype.slice.call(page.querySelectorAll('[data-type]'));
  var findBtn = page.querySelector('[data-find]');
  var exportBtn = page.querySelector('[data-export]');
  var exampleBtn = page.querySelector('[data-example]');
  var resultsEl = page.querySelector('[data-results]');
  var noteEl = page.querySelector('[data-detect-note]');

  var EXAMPLE = 'Our assistant scores 94% on MMLU-Pro and beats leading models on our internal benchmark.';
  var FIT_LABEL = { 3: 'Strong match', 2: 'Likely', 1: 'Worth checking' };
  var userEdited = false;
  var last = null;
  var byNo = {};
  LAI.laws.forEach(function (l) { byNo[l.no] = l; });

  function typo(s) { return String(s).replace(/(\w)'(\w)/g, '$1’$2'); }

  function detect(text) { return M.detect(LAI.claim, text); }
  function active() {
    return chipEls.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.getAttribute('data-type'); });
  }
  function setChips(ids) {
    chipEls.forEach(function (c) { c.setAttribute('aria-pressed', String(ids.indexOf(c.getAttribute('data-type')) !== -1)); });
  }
  // Say what the matcher did, and only say "Detected" when it detected something.
  function setNote(ids, text) {
    if (userEdited) { noteEl.textContent = 'Edited by you'; return; }
    if (ids.length) noteEl.textContent = 'Detected from the text, edit if wrong';
    else if (text && text.trim()) noteEl.textContent = 'No claim type detected, choose one';
    else noteEl.textContent = 'Choose one, or paste a claim and we will suggest some';
  }
  function syncFromText(text) {
    var ids = detect(text);
    setChips(ids);
    setNote(ids, text);
    return ids;
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

  function show(results, text, typed) {
    resultsEl.innerHTML = '';
    var shownN = M.visibleCount(results);
    var counts = { 3: 0, 2: 0, 1: 0 };
    results.forEach(function (r) { counts[r.fit] += 1; });
    var head = el('div', 'result-head');
    var h2 = el('h2', '', results.length + (results.length === 1 ? ' pattern worth checking' : ' patterns worth checking'));
    h2.id = 'results-h';
    head.appendChild(h2);
    var parts = [];
    if (counts[3]) parts.push(counts[3] + ' strong');
    if (counts[2]) parts.push(counts[2] + ' likely');
    if (counts[1]) parts.push(counts[1] + ' worth checking');
    head.appendChild(el('p', '', parts.join(' · ')));
    head.appendChild(el('p', 'result-head__caveat', typed
      ? 'Keyword matches, not a verdict on the claim. The strongest matches come first.'
      : 'No claim type detected. These came from specific phrases only. Choose a claim type above for a fuller list. Keyword matches, not a verdict.'));
    var tools = null, addAll = null, brief = null;
    if (window.LAIC) {
      tools = el('div', 'result-tools');
      addAll = el('button', 'btn btn--outline btn--sm', '');
      addAll.type = 'button';
      addAll.addEventListener('click', function () {
        var nos = shownNos();
        window.LAIC.addMany(nos);
        addAll.textContent = 'Added to My patterns';
        window.LAIC.announce('Added ' + nos.length + ' patterns to My patterns.');
      });
      brief = el('a', 'btn btn--outline btn--sm', 'Quick brief of these');
      tools.appendChild(addAll);
      tools.appendChild(brief);
      head.appendChild(tools);
    }
    resultsEl.appendChild(head);

    function shownNos() {
      var nos = [];
      Array.prototype.forEach.call(resultsEl.querySelectorAll('.result[data-no]'), function (r) {
        if (!r.hidden) nos.push(parseInt(r.getAttribute('data-no'), 10));
      });
      return nos;
    }
    function refreshTools() {
      if (!tools) return;
      var nos = shownNos();
      addAll.textContent = 'Add these ' + nos.length + ' to My patterns';
      brief.href = 'brief.html?patterns=' + nos.slice().sort(function (a, b) { return a - b; }).join(',');
    }

    var more = null;
    results.forEach(function (r, idx) {
      var law = byNo[r.no];
      var row = el('div', 'result');
      row.setAttribute('data-no', r.no);
      if (idx >= shownN) row.hidden = true;
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
    if (results.length > shownN) {
      more = el('button', 'btn btn--outline claim__more', 'Show ' + (results.length - shownN) + ' lower-fit ' + (results.length - shownN === 1 ? 'pattern' : 'patterns'));
      more.type = 'button';
      more.addEventListener('click', function () {
        Array.prototype.forEach.call(resultsEl.querySelectorAll('.result[hidden]'), function (r) { r.hidden = false; });
        more.remove();
        refreshTools();
      });
      resultsEl.appendChild(more);
    }
    refreshTools();
    exportBtn.disabled = false;
    last = { text: text, results: results };
  }

  function find() {
    var text = textEl.value.trim();
    if (!text) { message('Paste a claim first, then choose Find patterns that apply.'); textEl.focus(); return; }
    if (!userEdited) syncFromText(text);
    var types = active();
    var results = M.compute(LAI.claim, text, types);
    if (!results.length) {
      message(types.length
        ? 'No patterns matched this claim and the claim types chosen. Try choosing a different type above.'
        : 'No claim type detected. This is a keyword matcher, so it needs something to match. Choose a claim type above, or add detail such as a score, a comparison, who graded it, or where it was measured.');
      return;
    }
    show(results, text, types.length > 0);
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
      if (!userEdited) syncFromText(textEl.value);
    }, 150);
  });
  findBtn.addEventListener('click', find);
  exampleBtn.addEventListener('click', function () {
    textEl.value = EXAMPLE;
    userEdited = false;
    find();
  });
  exportBtn.addEventListener('click', function () {
    if (!last) return;
    var lines = ['Claim under review:', last.text, '', 'Patterns worth checking and what to ask (keyword matches, not an assessment of the claim):', ''];
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
