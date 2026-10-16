import fs from 'fs';
import path from 'path';

const target = path.join(process.cwd(), 'node_modules', 'google-play-scraper', 'lib', 'search.js');

if (!fs.existsSync(target)) {
  console.log('[patch-gplay-search] target file not found, skip');
  process.exit(0);
}

const src = fs.readFileSync(target, 'utf8');
if (src.includes('/store/search')) {
  console.log('[patch-gplay-search] already patched');
  process.exit(0);
}

if (!src.includes('/work/search')) {
  console.log('[patch-gplay-search] marker not found, skip');
  process.exit(0);
}

const next = src.replace('/work/search', '/store/search');
fs.writeFileSync(target, next, 'utf8');
console.log('[patch-gplay-search] patched /work/search -> /store/search');
