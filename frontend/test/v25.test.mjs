import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const src=fs.readFileSync(new URL('../src/main.jsx',import.meta.url),'utf8');
test('V25 dashboard calls V25 API',()=>{assert.match(src,/\/v25\/status/);assert.match(src,/\/v25\/dataset/);assert.match(src,/\/v25\/analytics/);});
test('V25 dashboard keeps scientific status visible',()=>{assert.match(src,/NOT_DETERMINED/);});
