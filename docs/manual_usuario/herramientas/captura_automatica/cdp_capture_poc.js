const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PROJECT_ROOT = path.resolve(__dirname, '..', '..', '..', '..');
const DEMO_ROOT = path.join(PROJECT_ROOT, 'docs', 'manual_usuario', 'entorno_demo');
const OUT_DIR = path.join(PROJECT_ROOT, 'docs', 'manual_usuario', 'capturas', 'prueba');
const CREDENTIALS_PATH = path.join(DEMO_ROOT, 'credenciales_demo.local.json');
const WIDTH = 1440;
const HEIGHT = 900;
const PORT = 9225;
const BASE_URL = process.env.DEMO_BASE_URL || 'http://127.0.0.1:8765';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function expandEnv(value) {
  return value.replace(/%([^%]+)%/g, (_match, name) => process.env[name] || '');
}

function findBrowser() {
  const candidates = [
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    '%LOCALAPPDATA%\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    '%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Chromium\\Application\\chrome.exe',
  ];
  for (const item of candidates) {
    const candidate = expandEnv(item);
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  throw new Error('No se encontro Edge, Chrome o Chromium en rutas habituales.');
}

async function waitForJson(url, attempts = 80) {
  for (let i = 0; i < attempts; i += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch (_error) {
      // Browser is still starting.
    }
    await sleep(250);
  }
  throw new Error(`No hubo respuesta CDP en ${url}`);
}

class CdpClient {
  constructor(wsUrl) {
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.ws = new WebSocket(wsUrl);
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Timeout abriendo WebSocket CDP')), 10000);
      this.ws.addEventListener('open', () => { clearTimeout(timer); resolve(); }, { once: true });
      this.ws.addEventListener('error', (event) => { clearTimeout(timer); reject(event.error || new Error('Error WebSocket CDP')); }, { once: true });
    });
    this.ws.addEventListener('message', (event) => {
      const payload = JSON.parse(event.data);
      if (payload.id && this.pending.has(payload.id)) {
        const { resolve, reject } = this.pending.get(payload.id);
        this.pending.delete(payload.id);
        if (payload.error) reject(new Error(JSON.stringify(payload.error)));
        else resolve(payload.result || {});
      } else if (payload.method) {
        this.events.push(payload);
      }
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`Timeout CDP: ${method}`));
        }
      }, 20000);
    });
  }

  async waitForLoad() {
    for (let i = 0; i < 120; i += 1) {
      if (this.events.some((event) => event.method === 'Page.loadEventFired')) {
        this.events = this.events.filter((event) => event.method !== 'Page.loadEventFired');
        await sleep(500);
        return;
      }
      await sleep(250);
    }
    await sleep(1000);
  }

  close() {
    this.ws.close();
  }
}

async function navigate(client, url) {
  await client.send('Page.navigate', { url });
  await client.waitForLoad();
}

async function evaluate(client, expression, awaitPromise = false) {
  const result = await client.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(JSON.stringify(result.exceptionDetails));
  }
  return result.result ? result.result.value : undefined;
}

async function screenshot(client, filename) {
  const result = await client.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  fs.writeFileSync(path.join(OUT_DIR, filename), Buffer.from(result.data, 'base64'));
  console.log(`captured ${filename}`);
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const browser = findBrowser();
  const profileDir = path.join(DEMO_ROOT, 'edge-profile');
  fs.rmSync(profileDir, { recursive: true, force: true });
  fs.mkdirSync(profileDir, { recursive: true });

  const args = [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profileDir}`,
    `--window-size=${WIDTH},${HEIGHT}`,
    'about:blank',
  ];
  const proc = spawn(browser, args, { stdio: 'ignore' });
  let client;
  try {
    const version = await waitForJson(`http://127.0.0.1:${PORT}/json/version`);
    const tabs = await waitForJson(`http://127.0.0.1:${PORT}/json/list`);
    const page = tabs.find((tab) => tab.type === 'page') || tabs[0];
    client = new CdpClient(page.webSocketDebuggerUrl || version.webSocketDebuggerUrl);
    await client.open();
    await client.send('Page.enable');
    await client.send('Runtime.enable');
    await client.send('Emulation.setDeviceMetricsOverride', { width: WIDTH, height: HEIGHT, deviceScaleFactor: 1, mobile: false });

    await navigate(client, `${BASE_URL}/`);
    await screenshot(client, 'POC-001-inicio-publico.png');

    await navigate(client, `${BASE_URL}/registro/`);
    await screenshot(client, 'POC-002-registro.png');

    const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
    await navigate(client, `${BASE_URL}/torneo/control/login/`);
    await evaluate(client, `(() => {
      document.querySelector('input[name="username"]').value = ${JSON.stringify(credentials.username)};
      document.querySelector('input[name="password"]').value = ${JSON.stringify(credentials.password)};
      document.querySelector('form').submit();
      return true;
    })()`);
    await client.waitForLoad();
    await screenshot(client, 'POC-003-panel-autenticado.png');

    await navigate(client, `${BASE_URL}/comunicaciones/`);
    await screenshot(client, 'POC-007-comunicaciones.png');
    await navigate(client, `${BASE_URL}/torneo/control/`);

    const divisionUrl = await evaluate(client, `(() => {
      const link = document.querySelector('a[href*="/torneo/control/divisiones/"]');
      return link ? link.href : '';
    })()`);
    if (!divisionUrl) throw new Error('No se encontro enlace de division en panel autenticado.');
    await navigate(client, divisionUrl);
    await screenshot(client, 'POC-004-control-torneo.png');

    const openedModal = await evaluate(client, `new Promise((resolve) => {
      const trigger = document.querySelector('.participant-trigger[data-participant-state-id]');
      if (!trigger) { resolve(false); return; }
      trigger.click();
      setTimeout(() => resolve(!document.querySelector('[data-participant-modal]')?.hidden), 1200);
    })`, true);
    if (openedModal) {
      await screenshot(client, 'POC-005-modal.png');
    }

    const stageUrl = await evaluate(client, `(() => {
      const link = Array.from(document.querySelectorAll('a[href*="/fases/"]')).find((item) => item.href.includes('/groups/'));
      return link ? link.href : '';
    })()`);
    if (stageUrl) {
      await navigate(client, stageUrl);
      await screenshot(client, 'POC-006-estado-visual.png');
      const openedStageModal = await evaluate(client, `new Promise((resolve) => {
        const trigger = document.querySelector('.participant-trigger[data-participant-state-id]');
        if (!trigger) { resolve(false); return; }
        trigger.click();
        setTimeout(() => resolve(!document.querySelector('[data-participant-modal]')?.hidden), 1500);
      })`, true);
      if (openedStageModal) {
        await screenshot(client, 'POC-005-modal.png');
      }
    }

    fs.writeFileSync(path.join(OUT_DIR, 'metadata_poc.json'), JSON.stringify({ browser, baseUrl: BASE_URL, width: WIDTH, height: HEIGHT }, null, 2));
  } finally {
    if (client) client.close();
    proc.kill('SIGTERM');
    await sleep(1000);
    if (!proc.killed) proc.kill('SIGKILL');
  }
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exit(1);
});
