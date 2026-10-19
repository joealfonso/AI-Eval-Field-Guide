#!/usr/bin/env node
/* Runs the real claim-matching code (js/claim-match.js) against the real rules (js/data.js).
   Used by build/test_claim_checker.py to check that its Python port gives identical answers.

   Input on stdin:  {"texts": ["claim one", "claim two"]}
   Output on stdout: [{"types": [...], "results": [[no, fit, hits], ...], "visible": n}, ...]
*/
'use strict';
var fs = require('fs');
var path = require('path');
var vm = require('vm');

var root = path.resolve(__dirname, '..');
var sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(root, 'js/data.js'), 'utf8'), sandbox);
var LAI = sandbox.window.LAI;
var M = require(path.join(root, 'js/claim-match.js'));

var input = JSON.parse(fs.readFileSync(0, 'utf8'));
var out = input.texts.map(function (text) {
  var types = M.detect(LAI.claim, text);
  var results = M.compute(LAI.claim, text, types);
  return {
    types: types,
    results: results.map(function (r) { return [r.no, r.fit, r.hits]; }),
    visible: M.visibleCount(results)
  };
});
process.stdout.write(JSON.stringify(out));
