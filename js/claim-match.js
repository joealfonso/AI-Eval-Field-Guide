/* Claim matching: the scoring used by the claim checker, kept free of the DOM so it can be tested.
   Rules live in data/editorial.json (claimChecker) and reach the page as LAI.claim via js/data.js.
   build/test_claim_checker.py holds a Python port of these functions and checks it against this file with node.
   If you change the scoring here, change the port there. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.LAIMatch = api;
})(this, function () {
  'use strict';

  var FIT = { strong: 3, likely: 2, worth: 1 };
  var LIMIT = 8;      // most results shown before "show more"
  var MIN_SHOWN = 4;  // if fewer than this are strong or likely, pad with lower-fit ones up to this many

  function rx(src) { return new RegExp(src, 'i'); }

  // Curly quotes to straight, so "can’t" matches a rule written with "can't".
  function norm(text) { return String(text || '').replace(/[‘’]/g, "'"); }

  // Ids of the claim types whose detect pattern appears in the text.
  function detect(claim, text) {
    var t = norm(text);
    return claim.types.filter(function (ty) { return rx(ty.detect).test(t); }).map(function (ty) { return ty.id; });
  }

  // Patterns worth checking, best first: by fit, then by how many rules reached the pattern, then by how central
  // the rule is to its claim type. A pattern reached more than once moves up one step (never above strong).
  // Returns [{ no, fit (3|2|1), why, ask, hits, pos }].
  function compute(claim, text, types) {
    var t = norm(text);
    var map = {};
    // pos is the rule's place in its claim type's list, which is written most important first.
    // Phrase rules (modifiers) count as position 1: specific, but not the core of a claim type.
    function add(rule, pos) {
      var f = FIT[rule.fit];
      var m = map[rule.no];
      if (!m) { map[rule.no] = { no: rule.no, fit: f, why: rule.why, ask: rule.ask, hits: 1, pos: pos }; return; }
      m.hits += 1;
      if (pos < m.pos) m.pos = pos;
      if (f > m.fit) { m.fit = f; m.why = rule.why; m.ask = rule.ask; }
    }
    claim.types.forEach(function (ty) {
      if (types.indexOf(ty.id) !== -1) ty.laws.forEach(function (rule, i) { add(rule, i); });
    });
    claim.modifiers.forEach(function (m) { if (rx(m.detect).test(t)) add(m, 1); });
    var out = Object.keys(map).map(function (k) { return map[k]; });
    out.forEach(function (r) { if (r.hits >= 2 && r.fit < 3) r.fit += 1; });
    out.sort(function (a, b) { return b.fit - a.fit || b.hits - a.hits || a.pos - b.pos || (a.no < b.no ? -1 : a.no > b.no ? 1 : 0); });
    return out;
  }

  // How many of the sorted results to show before "show more": every strong and likely
  // match up to LIMIT, padded with the best lower-fit ones so a result is never nearly empty.
  function visibleCount(results) {
    var firm = results.filter(function (r) { return r.fit >= 2; }).length;
    var n = Math.min(firm, LIMIT);
    if (n < MIN_SHOWN) n = Math.min(results.length, MIN_SHOWN);
    return n;
  }

  return { FIT: FIT, LIMIT: LIMIT, MIN_SHOWN: MIN_SHOWN, norm: norm, detect: detect, compute: compute, visibleCount: visibleCount };
});
