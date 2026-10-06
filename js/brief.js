/* Quick brief: a short overview of the chosen laws, assembled in the browser from each law's own text.
   The selection comes from ?laws=1,2,3 (a shared link) or from My laws (the collection). */
(function () {
  'use strict';

  var page = document.querySelector('[data-page="brief"]');
  var LAI = window.LAI;
  var LAIC = window.LAIC;
  if (!page || !LAI || !LAIC) return;

  var outEl = page.querySelector('[data-brief-out]');
  var presetsEl = page.querySelector('[data-brief-presets]');
  var gridEl = page.querySelector('[data-brief-grid]');
  var pickerEl = page.querySelector('[data-brief-picker]');
  var pickerSummary = page.querySelector('[data-picker-summary]');

  var byNo = {};
  LAI.laws.forEach(function (l) { byNo[parseInt(l.no, 10)] = l; });
  var cats = {};
  LAI.categories.forEach(function (c) { cats[c.id] = c; });

  function typo(s) {
    return String(s)
      .replace(/(\w)'(\w)/g, '$1’$2')
      .replace(/(^|[\s(\[—-])"/g, '$1“').replace(/"/g, '”')
      .replace(/(^|[\s(\[—-])'/g, '$1‘').replace(/'/g, '’');
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  /* ---------- state ---------- */
  var params = new URLSearchParams(window.location.search);
  var linked = false;
  var dirty = false;
  var state = { laws: [], detail: params.get('detail') === 'full' ? 'full' : 'gist' };

  function parseLaws(str) {
    var seen = {}, out = [];
    String(str || '').split(',').forEach(function (x) {
      var n = parseInt(x, 10);
      if (byNo[n] && !seen[n]) { seen[n] = true; out.push(n); }
    });
    return out.sort(function (a, b) { return a - b; });
  }
  var linkedLaws = parseLaws(params.get('laws'));
  linked = linkedLaws.length > 0;
  state.laws = linked ? linkedLaws : LAIC.get().filter(function (n) { return byNo[n]; });

  function sameList(a, b) {
    return a.length === b.length && a.every(function (x, i) { return x === b[i]; });
  }

  function updateUrl() {
    var q = [];
    if ((linked || dirty) && state.laws.length) q.push('laws=' + state.laws.join(','));
    if (state.detail === 'full') q.push('detail=full');
    try { window.history.replaceState(null, '', window.location.pathname + (q.length ? '?' + q.join('&') : '')); } catch (e) { /* file:// */ }
  }

  function setLaws(list) {
    state.laws = list.slice().sort(function (a, b) { return a - b; });
    dirty = true;
    updateUrl();
    renderPicker();
    renderBrief();
  }

  // The brief is a working set: editing it never changes My laws. Until the visitor edits it,
  // it follows My laws; afterwards it only refreshes so the Save button reflects the collection.
  LAIC.onChange(function (list) {
    if (linked || dirty) { renderBrief(); return; }
    var mine = list.filter(function (n) { return byNo[n]; });
    if (!sameList(mine, state.laws)) { state.laws = mine; renderPicker(); renderBrief(); }
  });

  /* ---------- picker ---------- */
  function renderPresets() {
    presetsEl.innerHTML = '';
    LAI.briefPresets.forEach(function (p) {
      var nums = p.laws.map(function (n) { return parseInt(n, 10); });
      var b = el('button', 'btn btn--outline btn--sm', p.label + ' (' + nums.length + ')');
      b.type = 'button';
      b.setAttribute('aria-pressed', String(sameList(nums, state.laws)));
      b.addEventListener('click', function () { setLaws(nums); });
      presetsEl.appendChild(b);
    });
    var clear = el('button', 'btn btn--ghost btn--sm', 'Clear');
    clear.type = 'button';
    clear.addEventListener('click', function () { setLaws([]); });
    presetsEl.appendChild(clear);
  }

  function renderPicker() {
    renderPresets();
    var sel = {};
    state.laws.forEach(function (n) { sel[n] = true; });
    gridEl.innerHTML = '';
    LAI.categories.forEach(function (c) {
      var group = el('fieldset', 'picker__group');
      group.appendChild(el('legend', '', c.id + '. ' + typo(c.name)));
      LAI.laws.filter(function (l) { return l.cat === c.id; }).forEach(function (l) {
        var n = parseInt(l.no, 10);
        var label = el('label');
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = !!sel[n];
        cb.addEventListener('change', function () {
          var set = {};
          state.laws.forEach(function (x) { set[x] = true; });
          if (cb.checked) set[n] = true; else delete set[n];
          var list = Object.keys(set).map(Number);
          state.laws = list.sort(function (a, b) { return a - b; });
          dirty = true;
          updateUrl();
          renderBrief();
          renderPresets();
          pickerSummary.textContent = summaryText();
        });
        label.appendChild(cb);
        label.appendChild(el('span', '', l.no + ' ' + typo(l.name)));
        group.appendChild(label);
      });
      gridEl.appendChild(group);
    });
    pickerSummary.textContent = summaryText();
  }
  function summaryText() {
    return 'Choose laws · ' + state.laws.length + ' of ' + LAI.laws.length + ' selected';
  }

  /* ---------- building blocks ---------- */
  function partsIn(laws) {
    return LAI.categories.filter(function (c) { return laws.some(function (l) { return l.cat === c.id; }); });
  }

  function degree(law, laws) {
    var set = {};
    laws.forEach(function (l) { set[parseInt(l.no, 10)] = true; });
    return law.shared.filter(function (s) { return set[parseInt(s[0], 10)]; }).length;
  }

  function overview(laws) {
    var parts = partsIn(laws);
    var box = el('section', 'brief__summary');
    box.setAttribute('aria-labelledby', 'brief-short');
    var h = el('h2', 'brief__label', 'The short version');
    h.id = 'brief-short';
    box.appendChild(h);
    var words = 0;
    if (laws.length === 1) {
      var only = laws[0];
      var p = el('p', 'brief__lead', 'One law: ' + typo(only.name) + '. ' + only.plain);
      words += p.textContent.split(/\s+/).length;
      box.appendChild(p);
      return { node: box, words: words };
    }
    var lead = 'You picked ' + plural(laws.length, 'law', 'laws') + ' from ' + plural(parts.length, 'part', 'parts') + ' of an evaluation.';
    var pl = el('p', 'brief__lead', lead);
    words += lead.split(/\s+/).length;
    box.appendChild(pl);
    var ul = el('ul', 'brief__threads');
    parts.forEach(function (c) {
      var inPart = laws.filter(function (l) { return l.cat === c.id; }).map(function (l) { return typo(l.name); });
      var li = el('li');
      var strong = el('strong', '', c.id + '. ' + typo(c.name) + '. ');
      li.appendChild(strong);
      var txt = c.thread + ' In your set: ' + inPart.join(', ') + '.';
      li.appendChild(document.createTextNode(txt));
      words += (strong.textContent + txt).split(/\s+/).length;
      ul.appendChild(li);
    });
    box.appendChild(ul);
    if (laws.length >= 3) {
      var best = null, bestDeg = 0;
      laws.forEach(function (l) {
        var d = degree(l, laws);
        if (d > bestDeg) { best = l; bestDeg = d; }
      });
      if (best) {
        var start = 'Start with ' + typo(best.name) + ': it shares research with ' + plural(bestDeg, 'other law', 'other laws') + ' in your set.';
        box.appendChild(el('p', 'brief__start', start));
        words += start.split(/\s+/).length;
      }
    }
    return { node: box, words: words };
  }

  function lawCard(l) {
    var c = cats[l.cat];
    var art = el('article', 'brief-law cat-' + c.n);
    var head = el('div', 'brief-law__head');
    head.appendChild(el('span', 'brief-law__no', 'No. ' + l.no));
    head.appendChild(el('h4', 'brief-law__name', typo(l.name)));
    var rm = el('button', 'link-btn', 'Remove');
    rm.type = 'button';
    rm.setAttribute('aria-label', 'Remove ' + typo(l.name) + ' from this brief');
    rm.addEventListener('click', function () {
      setLaws(state.laws.filter(function (n) { return n !== parseInt(l.no, 10); }));
      LAIC.announce('Removed ' + typo(l.name) + ' from this brief.');
      var count = outEl.querySelector('.brief__count');
      if (count) { count.tabIndex = -1; count.focus(); }
    });
    head.appendChild(rm);
    art.appendChild(head);
    art.appendChild(el('p', 'brief-law__quote', '“' + typo(l.aphorism) + '”'));
    art.appendChild(el('p', 'brief-law__plain', l.plain));
    var words = (l.aphorism + ' ' + l.plain).split(/\s+/).length;
    if (state.detail === 'full') {
      var dl = el('dl', 'brief-law__more');
      [['Evidence', l.evidence], ['Do this', l.doIt], ['Ask', typo(l.questions[0])]].forEach(function (row) {
        dl.appendChild(el('dt', '', row[0]));
        dl.appendChild(el('dd', '', row[1]));
        words += row[1].split(/\s+/).length;
      });
      art.appendChild(dl);
    }
    var a = el('a', 'brief-law__read', 'Read the full law →');
    a.href = 'laws/' + l.slug + '.html';
    art.appendChild(a);
    return { node: art, words: words };
  }

  function connections(laws) {
    var pairs = [];
    laws.forEach(function (a, i) {
      laws.slice(i + 1).forEach(function (b) {
        var hit = a.shared.filter(function (s) { return parseInt(s[0], 10) === parseInt(b.no, 10); })[0];
        if (hit) pairs.push({ a: a, b: b, n: hit[1] });
      });
    });
    pairs.sort(function (x, y) { return y.n - x.n || parseInt(x.a.no, 10) - parseInt(y.a.no, 10) || parseInt(x.b.no, 10) - parseInt(y.b.no, 10); });
    return pairs.slice(0, 6);
  }

  function readNext(laws) {
    var chosen = {};
    laws.forEach(function (l) { chosen[parseInt(l.no, 10)] = true; });
    var score = {};
    laws.forEach(function (l) {
      l.shared.forEach(function (s) {
        var n = parseInt(s[0], 10);
        if (!chosen[n]) score[n] = (score[n] || 0) + s[1];
      });
    });
    var list = Object.keys(score).map(Number).sort(function (a, b) { return score[b] - score[a] || a - b; });
    if (list.length < 3) {
      var partIds = {};
      laws.forEach(function (l) { partIds[l.cat] = true; });
      LAI.laws.forEach(function (l) {
        var n = parseInt(l.no, 10);
        if (list.length < 3 && !chosen[n] && partIds[l.cat] && list.indexOf(n) === -1) list.push(n);
      });
    }
    return list.slice(0, 3).map(function (n) { return byNo[n]; });
  }

  /* ---------- text export ---------- */
  function asText(laws) {
    var base = LAI.site.baseUrl;
    var lines = ['Quick brief: ' + plural(laws.length, 'law', 'laws') + ' (Laws of AI Evaluation)', ''];
    partsIn(laws).forEach(function (c) {
      lines.push(c.id + '. ' + typo(c.name));
      lines.push(c.thread);
      lines.push('');
      laws.filter(function (l) { return l.cat === c.id; }).forEach(function (l) {
        lines.push('No. ' + l.no + ' ' + typo(l.name) + ': “' + typo(l.aphorism) + '”');
        lines.push('  In plain terms: ' + l.plain);
        if (state.detail === 'full') {
          lines.push('  Evidence: ' + l.evidence);
          lines.push('  Do this: ' + l.doIt);
        }
        lines.push('  Ask: ' + typo(l.questions[0]));
        lines.push('  ' + base + '/laws/' + l.slug + '.html');
        lines.push('');
      });
    });
    return lines.join('\n');
  }

  function flash(btn, text) {
    var old = btn.getAttribute('data-label') || btn.textContent;
    btn.setAttribute('data-label', old);
    btn.textContent = text;
    window.setTimeout(function () { btn.textContent = old; }, 2000);
  }

  /* ---------- render ---------- */
  function renderBrief() {
    outEl.innerHTML = '';
    var laws = state.laws.map(function (n) { return byNo[n]; }).filter(Boolean);
    if (!laws.length) {
      var empty = el('div', 'brief__empty');
      empty.appendChild(el('h2', '', 'Nothing selected yet'));
      empty.appendChild(el('p', '', 'Pick a starting set above, choose laws from the list, or collect laws with the + Add buttons on the laws index. Your brief appears here.'));
      outEl.appendChild(empty);
      pickerEl.open = true;
      return;
    }

    var total = 0;
    var sum = overview(laws);
    total += sum.words;

    var cards = el('div', 'brief__laws');
    partsIn(laws).forEach(function (c) {
      var sec = el('section', 'brief__part cat-' + c.n);
      sec.setAttribute('aria-labelledby', 'part-' + c.id);
      var h3 = el('h3', 'brief__part-title');
      h3.id = 'part-' + c.id;
      h3.appendChild(el('span', '', c.id + '.'));
      h3.appendChild(document.createTextNode(' ' + typo(c.name)));
      sec.appendChild(h3);
      laws.filter(function (l) { return l.cat === c.id; }).forEach(function (l) {
        var card = lawCard(l);
        total += card.words;
        sec.appendChild(card.node);
      });
      cards.appendChild(sec);
    });

    var minutes = Math.max(1, Math.round(total / 200));
    var bar = el('div', 'brief__bar');
    bar.appendChild(el('p', 'brief__count', plural(laws.length, 'law', 'laws') + ' · about ' + plural(minutes, 'minute', 'minutes') + ' to read'));

    var seg = el('div', 'seg seg--rule');
    seg.setAttribute('role', 'group');
    seg.setAttribute('aria-label', 'Level of detail');
    [['gist', 'Just the gist'], ['full', 'With evidence and actions']].forEach(function (d) {
      var b = el('button', '', d[1]);
      b.type = 'button';
      b.setAttribute('aria-pressed', String(state.detail === d[0]));
      b.addEventListener('click', function () { state.detail = d[0]; updateUrl(); renderBrief(); });
      seg.appendChild(b);
    });
    bar.appendChild(seg);

    var actions = el('div', 'brief__actions');
    var copyLink = el('button', 'btn btn--outline btn--sm', 'Copy link');
    copyLink.type = 'button';
    copyLink.addEventListener('click', function () {
      var q = 'laws=' + state.laws.join(',') + (state.detail === 'full' ? '&detail=full' : '');
      LAIC.copy(window.location.origin + window.location.pathname + '?' + q).then(function () { flash(copyLink, 'Copied'); LAIC.announce('Link copied'); }, function () { flash(copyLink, 'Press Ctrl+C'); });
    });
    var copyText = el('button', 'btn btn--outline btn--sm', 'Copy as text');
    copyText.type = 'button';
    copyText.addEventListener('click', function () {
      LAIC.copy(asText(laws)).then(function () { flash(copyText, 'Copied'); LAIC.announce('Brief copied as text'); }, function () { flash(copyText, 'Copy failed'); });
    });
    actions.appendChild(copyLink);
    actions.appendChild(copyText);
    if (state.laws.some(function (n) { return !LAIC.has(n); })) {
      var save = el('button', 'btn btn--outline btn--sm', 'Save to My laws');
      save.type = 'button';
      save.addEventListener('click', function () {
        LAIC.addMany(state.laws);
        LAIC.announce('Saved to My laws.');
        var count = outEl.querySelector('.brief__count');
        if (count) { count.tabIndex = -1; count.focus(); }
      });
      actions.appendChild(save);
    }
    bar.appendChild(actions);
    outEl.appendChild(bar);
    outEl.appendChild(sum.node);
    outEl.appendChild(cards);

    var pairs = connections(laws);
    if (pairs.length) {
      var conn = el('section', 'brief__block');
      conn.setAttribute('aria-labelledby', 'brief-conn');
      var ch = el('h2', 'brief__label', 'How they connect');
      ch.id = 'brief-conn';
      conn.appendChild(ch);
      conn.appendChild(el('p', 'brief__sub', 'Pairs that cite some of the same research.'));
      var ul = el('ul', 'brief__pairs');
      pairs.forEach(function (p) {
        var li = el('li');
        var a1 = el('a', '', typo(p.a.name)); a1.href = 'laws/' + p.a.slug + '.html';
        var a2 = el('a', '', typo(p.b.name)); a2.href = 'laws/' + p.b.slug + '.html';
        li.appendChild(a1);
        li.appendChild(document.createTextNode(' ↔ '));
        li.appendChild(a2);
        li.appendChild(el('span', 'brief__pair-n', plural(p.n, 'shared source', 'shared sources')));
        ul.appendChild(li);
      });
      conn.appendChild(ul);
      outEl.appendChild(conn);
    }

    var next = readNext(laws);
    if (next.length) {
      var nb = el('section', 'brief__block');
      nb.setAttribute('aria-labelledby', 'brief-next');
      var nh = el('h2', 'brief__label', 'Read next');
      nh.id = 'brief-next';
      nb.appendChild(nh);
      nb.appendChild(el('p', 'brief__sub', 'Closest to your set by shared research, or from the same part.'));
      var nl = el('ul', 'brief__next');
      next.forEach(function (l) {
        var li = el('li');
        var a = el('a', 'brief__next-name', typo(l.name)); a.href = 'laws/' + l.slug + '.html';
        li.appendChild(a);
        li.appendChild(el('span', 'brief__next-quote', '“' + typo(l.aphorism) + '”'));
        var add = el('button', 'pick pick--inline', '+ Add to brief');
        add.type = 'button';
        add.appendChild(el('span', 'visually-hidden', ' (' + typo(l.name) + ')'));
        add.addEventListener('click', function () {
          setLaws(state.laws.concat([parseInt(l.no, 10)]));
          LAIC.announce('Added ' + typo(l.name) + ' to this brief.');
        });
        li.appendChild(add);
        nl.appendChild(li);
      });
      nb.appendChild(nl);
      outEl.appendChild(nb);
    }

    var ask = el('section', 'brief__block');
    ask.setAttribute('aria-labelledby', 'brief-ask');
    var ah = el('h2', 'brief__label', 'Questions to take with you');
    ah.id = 'brief-ask';
    ask.appendChild(ah);
    var ol = el('ol', 'brief__questions');
    laws.forEach(function (l) { ol.appendChild(el('li', '', typo(l.questions[0]))); });
    ask.appendChild(ol);
    var cl = el('a', 'btn btn--ink', 'Build a printable checklist from these');
    cl.href = 'checklist.html?preset=custom&laws=' + state.laws.join(',');
    ask.appendChild(cl);
    outEl.appendChild(ask);
  }

  renderPicker();
  renderBrief();
  if (!state.laws.length) pickerEl.open = true;
})();
