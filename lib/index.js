'use strict';

import express from 'express';
import gplay from "google-play-scraper";
import path from 'path';
import qs from 'querystring';
import https from 'https';

const router = express.Router();

const toList = (apps) => ({ results: apps });
const SEARCH_TIMEOUT_MS = 12000;

const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const withTimeout = (promise, ms, label) =>
  Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error(`${label} timeout`)), ms))
  ]);

async function fallbackSearch(opts) {
  const term = opts.term || '';
  const lang = opts.lang || 'en';
  const country = opts.country || 'us';
  const num = Math.min(parseInt(opts.num || '20', 10), 50);
  const price = (opts.price || 'all').toLowerCase();

  const priceParam = price === 'free' ? '1' : price === 'paid' ? '2' : '0';
  const url = `https://play.google.com/store/search?q=${encodeURIComponent(term)}&c=apps&hl=${lang}&gl=${country}&price=${priceParam}`;
  const html = await new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: { 'user-agent': 'Mozilla/5.0' }
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(data));
    });
    req.setTimeout(SEARCH_TIMEOUT_MS, () => {
      req.destroy(new Error('search page timeout'));
    });
    req.on('error', reject);
  }).catch(() => '');

  if (!html) return [];

  const re = /\/store\/apps\/details\?id=([A-Za-z0-9._-]+)/g;
  const appIds = [];
  const seen = new Set();
  let m;
  while ((m = re.exec(html)) !== null) {
    const appId = m[1];
    if (seen.has(appId)) continue;
    seen.add(appId);
    appIds.push(appId);
    if (appIds.length >= num) break;
  }

  if (!appIds.length) return [];

  const appIdPattern = appIds.map(escapeRegExp).join('|');
  const ordered = html.match(new RegExp(appIdPattern, 'g')) || [];
  const orderedIds = [...new Set(ordered)].filter((id) => seen.has(id));

  const apps = await Promise.allSettled(
    orderedIds.map((appId) =>
      withTimeout(gplay.app({ appId, lang, country }), SEARCH_TIMEOUT_MS, `gplay.app(${appId})`)
    )
  );

  return apps
    .filter((r) => r.status === 'fulfilled')
    .map((r) => r.value);
}

const cleanUrls = (req) => (app) => Object.assign({}, app, {
  playstoreUrl: app.url,
  url: buildUrl(req, 'apps/' + app.appId),
  permissions: buildUrl(req, 'apps/' + app.appId + '/permissions'),
  similar: buildUrl(req, 'apps/' + app.appId + '/similar'),
  reviews: buildUrl(req, 'apps/' + app.appId + '/reviews'),
  datasafety: buildUrl(req, 'apps/' + app.appId + '/datasafety'),
  developer: {
    devId: app.developer,
    url: buildUrl(req, 'developers/' + qs.escape(app.developer))
  },
  categories: buildUrl(req, 'categories/')
});

const buildUrl = (req, subpath) =>
  req.protocol + '://' + path.join(req.get('host'), req.baseUrl, subpath);

/* Index */
router.get('/', (req, res) =>
  res.json({
    apps: buildUrl(req, 'apps'),
    developers: buildUrl(req, 'developers'),
    categories: buildUrl(req, 'categories')
  }));

/* App search */
router.get('/apps/', function (req, res, next) {
  if (!req.query.q) {
    return next();
  }

  const opts = Object.assign({ term: req.query.q }, req.query);

  fallbackSearch(opts)
    .then(async (apps) => {
      if (apps && apps.length) return apps;
      return withTimeout(gplay.search(opts), SEARCH_TIMEOUT_MS, 'gplay.search')
        .catch(() => []);
    })
    .then((apps) => apps.map(cleanUrls(req)))
    .then(toList)
    .then(res.json.bind(res))
    .catch(next);
});

/* Search suggest */
router.get('/apps/', function (req, res, next) {
  if (!req.query.suggest) {
    return next();
  }

  const toJSON = (term) => ({
    term,
    url: buildUrl(req, '/apps/') + '?' + qs.stringify({ q: term })
  });

  gplay.suggest({ term: req.query.suggest })
    .then((terms) => terms.map(toJSON))
    .then(toList)
    .then(res.json.bind(res))
    .catch(next);
});

/* App list */
router.get('/apps/', function (req, res, next) {
  function paginate(apps) {
    const num = parseInt(req.query.num || '60');
    const start = parseInt(req.query.start || '0');

    if (start - num >= 0) {
      req.query.start = start - num;
      apps.prev = buildUrl(req, '/apps/') + '?' + qs.stringify(req.query);
    }

    if (start + num <= 500) {
      req.query.start = start + num;
      apps.next = buildUrl(req, '/apps/') + '?' + qs.stringify(req.query);
    }

    return apps;
  }

  gplay.list(req.query)
    .then((apps) => apps.map(cleanUrls(req)))
    .then(toList).then(paginate)
    .then(res.json.bind(res))
    .catch(next);
});

/* App detail*/
router.get('/apps/:appId', function (req, res, next) {
  const opts = Object.assign({ appId: req.params.appId }, req.query);
  gplay.app(opts)
    .then(cleanUrls(req))
    .then(res.json.bind(res))
    .catch(next);
});

/* Similar apps */
router.get('/apps/:appId/similar', function (req, res, next) {
  const opts = Object.assign({ appId: req.params.appId }, req.query);
  gplay.similar(opts)
    .then((apps) => apps.map(cleanUrls(req)))
    .then(toList)
    .then(res.json.bind(res))
    .catch(next);
});

/* Data Safety */
router.get('/apps/:appId/datasafety', function (req, res, next) {
  const opts = Object.assign({ appId: req.params.appId }, req.query);
  gplay.datasafety(opts)
    .then(toList)
    .then(res.json.bind(res))
    .catch(next);
});

/* App permissions */
router.get('/apps/:appId/permissions', function (req, res, next) {
  const opts = Object.assign({ appId: req.params.appId }, req.query);
  gplay.permissions(opts)
    .then(toList)
    .then(res.json.bind(res))
    .catch(next);
});

/* App reviews */
router.get('/apps/:appId/reviews', function (req, res, next) {
  function paginate(apps) {
    const page = parseInt(req.query.page || '0');

    const subpath = '/apps/' + req.params.appId + '/reviews/';
    if (page > 0) {
      req.query.page = page - 1;
      apps.prev = buildUrl(req, subpath) + '?' + qs.stringify(req.query);
    }

    if (apps.results.length) {
      req.query.page = page + 1;
      apps.next = buildUrl(req, subpath) + '?' + qs.stringify(req.query);
    }

    return apps;
  }

  const opts = Object.assign({ appId: req.params.appId }, req.query);
  gplay.reviews(opts)
    .then(toList)
    .then(paginate)
    .then(res.json.bind(res))
    .catch(next);
});

/* Apps by developer */
router.get('/developers/:devId/', function (req, res, next) {
  const opts = Object.assign({ devId: req.params.devId }, req.query);

  gplay.developer(opts)
    .then((apps) => apps.map(cleanUrls(req)))
    .then((apps) => ({
      devId: req.params.devId,
      apps
    }))
    .then(res.json.bind(res))
    .catch(next);
});

/* Developer list (not supported) */
router.get('/developers/', (req, res) =>
  res.status(400).json({
    message: 'Please specify a developer id.',
    example: buildUrl(req, '/developers/' + qs.escape('Wikimedia Foundation'))
  }));

/* Category list */
router.get('/categories/', function (req, res, next) {
  gplay.categories()
    .then(res.json.bind(res))
    .catch(next);
});


function errorHandler(err, req, res, next) {
  res.status(400).json({ message: err.message });
  next();
}

router.use(errorHandler);

export default router;
