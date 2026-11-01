const { chromium } = require('playwright');
(async () => { const [,, url, out, w, h] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
  await p.goto(url); await p.waitForTimeout(400); await p.screenshot({ path: out }); await b.close(); })();
