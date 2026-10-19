/* Sample size and error bars: small calculators. Nothing is sent anywhere.
   The formulas match build/sample_stats.py; build/test_sample_size.py checks that they agree. */
(function () {
  'use strict';

  var Z_CONF = { '90': 1.6448536269514722, '95': 1.959963984540054, '99': 2.5758293035489004 };
  var Z_POWER = { '80': 0.8416212335729143, '90': 1.2815515655446004, '95': 1.6448536269514722 };

  /* Wilson score interval for proportion p observed on n items. */
  function wilson(p, n, z) {
    var denom = 1 + z * z / n;
    var centre = (p + z * z / (2 * n)) / denom;
    var half = z / denom * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
    return { low: Math.max(0, centre - half), high: Math.min(1, centre + half) };
  }

  /* Items needed so the usual interval has half-width e at expected accuracy p. */
  function nForMargin(p, e, z) {
    return Math.ceil(z * z * p * (1 - p) / (e * e) - 1e-9);
  }

  /* Items per system, two separate item samples (Fleiss, Levin and Paik). */
  function nIndependent(p1, p2, za, zb) {
    var d = p1 - p2;
    var pbar = (p1 + p2) / 2;
    var a = za * Math.sqrt(2 * pbar * (1 - pbar)) + zb * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2));
    return Math.ceil(a * a / (d * d) - 1e-9);
  }

  /* Items needed when both systems run on the same items (Connor 1987). pd = share of items where exactly one is right. */
  function nPaired(pd, delta, za, zb) {
    var a = za * Math.sqrt(pd) + zb * Math.sqrt(pd - delta * delta);
    return Math.ceil(a * a / (delta * delta) - 1e-9);
  }

  /* A minus B on the same n items. b = only A right, c = only B right (Miller 2024, eq. 7). */
  function pairedDifference(n, b, c, z) {
    var d = (b - c) / n;
    var ss = (b + c) - Math.pow(b - c, 2) / n;
    var se = Math.sqrt(Math.max(ss, 0) / (n - 1) / n);
    return { diff: d, se: se, low: d - z * se, high: d + z * se };
  }

  var api = { wilson: wilson, nForMargin: nForMargin, nIndependent: nIndependent, nPaired: nPaired, pairedDifference: pairedDifference, Z_CONF: Z_CONF, Z_POWER: Z_POWER };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  if (typeof document === 'undefined') { return; }

  /* ---------- page wiring ---------- */
  function pct(x, digits) { return (x * 100).toFixed(digits === undefined ? 1 : digits) + '%'; }
  function points(x) { return (x * 100).toFixed(1); }
  function int(x) { return Math.round(x).toLocaleString('en-US'); }
  function num(form, name) {
    var el = form.elements[name];
    if (!el || el.value === '') { return NaN; }
    return Number(el.value);
  }

  var calcs = {
    ci: function (f) {
      var n = num(f, 'n'), acc = num(f, 'acc'), z = Z_CONF[f.elements.conf.value];
      if (!(n >= 1) || n !== Math.floor(n)) { return { error: 'Enter the number of items as a whole number, 1 or more.' }; }
      if (!(acc >= 0 && acc <= 100)) { return { error: 'Enter accuracy as a percentage between 0 and 100.' }; }
      var p = acc / 100, w = wilson(p, n, z);
      var text = 'With ' + int(n) + ' items and ' + pct(p) + ' observed, the ' + f.elements.conf.value + '% Wilson interval runs from ' + pct(w.low) + ' to ' + pct(w.high) + '.';
      var extra = 'A claim that the true accuracy is above ' + pct(w.high, 0) + ' or below ' + pct(w.low, 0) + ' is not supported by this sample alone.';
      if (n < 30) { extra += ' With fewer than about 30 items, treat even this interval as rough.'; }
      return { text: text, extra: extra };
    },
    margin: function (f) {
      var acc = num(f, 'acc'), e = num(f, 'e'), z = Z_CONF[f.elements.conf.value];
      if (!(acc > 0 && acc < 100)) { return { error: 'Enter expected accuracy as a percentage above 0 and below 100. If you do not know, use 50.' }; }
      if (!(e > 0 && e < 50)) { return { error: 'Enter a margin of error in percentage points, above 0 and below 50.' }; }
      var p = acc / 100, n = nForMargin(p, e / 100, z);
      return { text: 'You need about ' + int(n) + ' items for a ' + f.elements.conf.value + '% interval of plus or minus ' + e + ' points around ' + acc + '% accuracy.', extra: 'This is the planning figure from the usual normal approximation. It assumes items are independent and each is scored right or wrong.' };
    },
    independent: function (f) {
      var base = num(f, 'base'), diff = num(f, 'diff'), za = Z_CONF[f.elements.conf.value], zb = Z_POWER[f.elements.power.value];
      if (!(base > 0 && base < 100)) { return { error: 'Enter the baseline accuracy as a percentage above 0 and below 100.' }; }
      if (!(diff !== 0 && Math.abs(diff) < 100)) { return { error: 'Enter the difference you want to detect in percentage points, not zero.' }; }
      var p1 = base / 100, p2 = p1 + diff / 100;
      if (!(p2 > 0 && p2 < 1)) { return { error: 'The baseline plus the difference must stay between 0% and 100%.' }; }
      var n = nIndependent(p1, p2, za, zb);
      return { text: 'About ' + int(n) + ' items per system (' + int(2 * n) + ' item scores in all) to detect ' + base + '% against ' + (p2 * 100).toFixed(1).replace(/\.0$/, '') + '%, at ' + f.elements.conf.value + '% confidence and ' + f.elements.power.value + '% power.', extra: 'This is for two different samples of items. If both systems can run on the same items, the paired calculator below can need far fewer, depending on how often the systems disagree.' };
    },
    paired: function (f) {
      var diff = num(f, 'diff'), dis = num(f, 'dis'), za = Z_CONF[f.elements.conf.value], zb = Z_POWER[f.elements.power.value];
      if (!(diff !== 0 && Math.abs(diff) < 100)) { return { error: 'Enter the difference you want to detect in percentage points, not zero.' }; }
      if (!(dis > 0 && dis <= 100)) { return { error: 'Enter the disagreement rate as a percentage above 0 and up to 100.' }; }
      if (dis < Math.abs(diff)) { return { error: 'The disagreement rate cannot be smaller than the difference. If the difference is ' + Math.abs(diff) + ' points, the systems must disagree on at least ' + Math.abs(diff) + '% of items.' }; }
      var n = nPaired(dis / 100, diff / 100, za, zb);
      return { text: 'About ' + int(n) + ' items, each scored on both systems, to detect a ' + Math.abs(diff) + '-point difference when the systems disagree on ' + dis + '% of items, at ' + f.elements.conf.value + '% confidence and ' + f.elements.power.value + '% power.', extra: 'The disagreement rate is the main input and is usually unknown in advance. Run both systems on a pilot of 50 to 100 items, count the items where exactly one is right, and use that share.' };
    },
    pairedci: function (f) {
      var n = num(f, 'n'), b = num(f, 'b'), c = num(f, 'c'), z = Z_CONF[f.elements.conf.value];
      if (!(n >= 2) || n !== Math.floor(n)) { return { error: 'Enter the number of items as a whole number, 2 or more.' }; }
      if (!(b >= 0 && c >= 0) || b !== Math.floor(b) || c !== Math.floor(c)) { return { error: 'Enter the two disagreement counts as whole numbers, 0 or more.' }; }
      if (b + c > n) { return { error: 'The two disagreement counts cannot add up to more than the number of items.' }; }
      if (b + c === 0) { return { text: 'The systems agreed on every item, so this sample shows no difference between them.', extra: 'That is not proof they are equal. It only means these items cannot tell them apart.' }; }
      var r = pairedDifference(n, b, c, z);
      var text = 'System A minus system B: ' + (r.diff >= 0 ? '+' : '−') + points(Math.abs(r.diff)) + ' points, ' + f.elements.conf.value + '% interval ' + (r.low >= 0 ? '+' : '−') + points(Math.abs(r.low)) + ' to ' + (r.high >= 0 ? '+' : '−') + points(Math.abs(r.high)) + '.';
      var extra = (r.low > 0 || r.high < 0) ? 'The interval does not include zero, so on these items the gap is larger than the sampling noise.' : 'The interval includes zero, so on these items the gap is within the sampling noise. Treat it as a tie.';
      if (b + c < 25) { extra += ' With so few disagreements the normal approximation is rough; an exact test on the disagreements is safer.'; }
      return { text: text, extra: extra };
    }
  };

  Array.prototype.forEach.call(document.querySelectorAll('form[data-calc]'), function (form) {
    var fn = calcs[form.getAttribute('data-calc')];
    var out = form.querySelector('[data-out]');
    if (!fn || !out) { return; }
    function run() {
      var r = fn(form);
      out.textContent = '';
      var p = document.createElement('p');
      if (r.error) {
        p.className = 'calc__err';
        p.textContent = r.error;
        out.appendChild(p);
        return;
      }
      p.className = 'calc__result';
      p.textContent = r.text;
      out.appendChild(p);
      if (r.extra) {
        var q = document.createElement('p');
        q.className = 'calc__extra';
        q.textContent = r.extra;
        out.appendChild(q);
      }
    }
    form.addEventListener('input', run);
    form.addEventListener('change', run);
    form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
    run();
  });
})();
