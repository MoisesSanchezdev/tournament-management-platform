const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..", "..");
const MANUAL_ROOT = path.join(PROJECT_ROOT, "docs", "manual_usuario");
const DEMO_ROOT = path.join(MANUAL_ROOT, "entorno_demo");
const OUT_DIR = path.join(MANUAL_ROOT, "capturas", "base");
const REVIEW_DIR = path.join(MANUAL_ROOT, "capturas", "revision");
const DISCARDED_DIR = path.join(MANUAL_ROOT, "capturas", "descartadas");
const CREDENTIALS_PATH = path.join(DEMO_ROOT, "credenciales_demo.local.json");
const SUMMARY_PATH = path.join(DEMO_ROOT, "datos", "resumen_banco_capturas.json");
const MANIFEST_PATH = path.join(REVIEW_DIR, "metadata_banco_capturas.json");
const WIDTH = 1440;
const HEIGHT = 900;
const PORT = Number(process.env.DEMO_CDP_PORT || "9225");
const BASE_URL = process.env.DEMO_BASE_URL || "http://127.0.0.1:8765";

const capturePlan = [
  ["MU-001", "MU-001-inicio-publico.png", "Sitio publico", "/"],
  ["MU-002", "MU-002-reglas-publicas.png", "Reglas", "/reglas/"],
  ["MU-003", "MU-003-patrocinadores.png", "Patrocinadores", "/patrocinadores/"],
  ["MU-004", "MU-004-seleccion-registro.png", "Seleccion de registro", "/registro/"],
  ["MU-005", "MU-005-registro-escolar.png", "Registro escolar diligenciado", "/registro/colegios/"],
  ["MU-006", "MU-006-registro-escolar-error.png", "Validacion de registro escolar", "/registro/colegios/"],
  ["MU-007", "MU-007-registro-universitario.png", "Registro universitario diligenciado", "/registro/universidades/"],
  ["MU-008", "MU-008-registro-exito.png", "Confirmacion de registro", "/registro/exito/colegio/"],
  ["MU-009", "MU-009-confirmacion-asistencia.png", "Confirmacion de asistencia", ""],
  ["MU-010", "MU-010-asistencia-confirmada.png", "Asistencia ya confirmada", ""],
  ["MU-011", "MU-011-token-invalido.png", "Token invalido", "/registro/confirmar-asistencia/00000000-0000-0000-0000-000000000000/"],
  ["MU-012", "MU-012-login-panel.png", "Login interno", "/torneo/control/login/"],
  ["MU-013", "MU-013-panel-torneo.png", "Panel de torneo", "/torneo/control/"],
  ["MU-014", "MU-014-generar-competencia.png", "Generar competencia", "/torneo/control/"],
  ["MU-015", "MU-015-configuracion-division.png", "Configuracion de division", ""],
  ["MU-016", "MU-016-formato-manual.png", "Formato manual", ""],
  ["MU-017", "MU-017-distribucion-grupos.png", "Distribucion de grupos", ""],
  ["MU-018", "MU-018-clasificados-grupo.png", "Clasificados de grupo", ""],
  ["MU-019", "MU-019-guardar-grupo.png", "Guardar grupo", ""],
  ["MU-020", "MU-020-guardar-todos.png", "Guardar todos", ""],
  ["MU-021", "MU-021-modal-siguiente-fase.png", "Modal siguiente fase", ""],
  ["MU-022", "MU-022-crear-fase-recomendada.png", "Crear fase recomendada", ""],
  ["MU-023", "MU-023-repechaje.png", "Repechaje", ""],
  ["MU-024", "MU-024-asistente-manual.png", "Asistente manual", ""],
  ["MU-025", "MU-025-propuesta-manual.png", "Propuesta manual", ""],
  ["MU-026", "MU-026-batalla-ganador.png", "Batalla con ganador", ""],
  ["MU-027", "MU-027-batalla-clasificados.png", "Batalla con clasificados", ""],
  ["MU-028", "MU-028-confirmacion-correccion.png", "Confirmacion de correccion", ""],
  ["MU-029", "MU-029-modal-participante.png", "Modal participante", ""],
  ["MU-030", "MU-030-edicion-participante.png", "Edicion participante", ""],
  ["MU-031", "MU-031-podio-final.png", "Podio final", ""],
  ["MU-032", "MU-032-dashboard-comunicaciones.png", "Dashboard comunicaciones", "/comunicaciones/"],
  ["MU-033", "MU-033-lista-plantillas.png", "Lista plantillas", "/comunicaciones/plantillas/"],
  ["MU-034", "MU-034-nueva-plantilla.png", "Nueva plantilla", "/comunicaciones/plantillas/nueva/"],
  ["MU-035", "MU-035-preview-plantilla.png", "Preview plantilla", ""],
  ["MU-036", "MU-036-invitaciones-lote.png", "Invitaciones por lote", "/comunicaciones/invitaciones/"],
  ["MU-037", "MU-037-destinatario-manual.png", "Destinatario manual", "/comunicaciones/invitaciones/"],
  ["MU-038", "MU-038-confirmaciones-asistencia.png", "Confirmaciones de asistencia", "/comunicaciones/confirmaciones/"],
  ["MU-039", "MU-039-historial-comunicaciones.png", "Historial comunicaciones", "/comunicaciones/historial/"],
  ["MU-040", "MU-040-admin-modelos.png", "Admin modelos", "/admin/"],
  ["MU-041", "MU-041-admin-registros.png", "Admin registros", "/admin/participants/schoolregistration/"],
  ["MU-042", "MU-042-admin-torneo.png", "Admin torneo", "/admin/tournament/divisioncompetition/"],
];

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function expandEnv(value) {
  return value.replace(/%([^%]+)%/g, (_match, name) => process.env[name] || "");
}

function findBrowser() {
  const candidates = [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "%LOCALAPPDATA%\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe",
  ];
  for (const item of candidates) {
    const candidate = expandEnv(item);
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error("No se encontro Edge o Chrome en rutas habituales.");
}

async function waitForJson(url, attempts = 100) {
  for (let i = 0; i < attempts; i += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch (_error) {
      // Browser is still starting.
    }
    await sleep(200);
  }
  throw new Error(`No hubo respuesta CDP en ${url}`);
}

class CdpClient {
  constructor(wsUrl) {
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
    this.dialogs = [];
    this.ws = new WebSocket(wsUrl);
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("Timeout abriendo WebSocket CDP")), 10000);
      this.ws.addEventListener("open", () => { clearTimeout(timer); resolve(); }, { once: true });
      this.ws.addEventListener("error", (event) => { clearTimeout(timer); reject(event.error || new Error("Error WebSocket CDP")); }, { once: true });
    });
    this.ws.addEventListener("message", (event) => {
      const payload = JSON.parse(event.data);
      if (payload.id && this.pending.has(payload.id)) {
        const { resolve, reject } = this.pending.get(payload.id);
        this.pending.delete(payload.id);
        if (payload.error) reject(new Error(JSON.stringify(payload.error)));
        else resolve(payload.result || {});
        return;
      }
      if (payload.method === "Page.javascriptDialogOpening") {
        this.dialogs.push(payload.params);
        this.send("Page.handleJavaScriptDialog", { accept: true }).catch(() => {});
      }
      if (payload.method) this.events.push(payload);
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
      }, 25000);
    });
  }

  async waitForLoad() {
    for (let i = 0; i < 100; i += 1) {
      if (this.events.some((event) => event.method === "Page.loadEventFired")) {
        this.events = this.events.filter((event) => event.method !== "Page.loadEventFired");
        await sleep(350);
        return;
      }
      await sleep(150);
    }
    await sleep(800);
  }

  close() {
    this.ws.close();
  }
}

async function evaluate(client, expression, awaitPromise = false) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result ? result.result.value : undefined;
}

async function navigate(client, relativeOrAbsolute) {
  const url = relativeOrAbsolute.startsWith("http") ? relativeOrAbsolute : `${BASE_URL}${relativeOrAbsolute}`;
  await client.send("Page.navigate", { url });
  await client.waitForLoad();
  await waitForDom(client);
}

async function waitForDom(client) {
  await evaluate(client, `new Promise((resolve) => {
    const done = () => requestAnimationFrame(() => requestAnimationFrame(resolve));
    if (document.readyState === "complete" || document.readyState === "interactive") done();
    else document.addEventListener("DOMContentLoaded", done, { once: true });
  })`, true);
}

async function setViewport(client) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: WIDTH,
    height: HEIGHT,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await evaluate(client, "document.body.style.zoom = '100%'");
}

async function scrollTo(client, y) {
  await evaluate(client, `window.scrollTo({ top: ${Number(y)}, behavior: "instant" }); true`);
  await sleep(250);
}

async function capture(client, item, extras = {}) {
  await setViewport(client);
  const result = await client.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  const filePath = path.join(OUT_DIR, item.file);
  fs.writeFileSync(filePath, Buffer.from(result.data, "base64"));
  const pageInfo = await evaluate(client, `(() => ({
    title: document.title,
    url: location.href,
    text: document.body.innerText.slice(0, 5000),
    width: innerWidth,
    height: innerHeight
  }))()`);
  const privacyIssues = privacyScan(pageInfo.text, pageInfo.url);
  const isErrorPage = /(?:ValueError|Error|Exception) at \//i.test(pageInfo.title || "") || /Traceback|Request Method:/i.test(pageInfo.text || "");
  const status = isErrorPage ? "ERROR" : (privacyIssues.length ? "DESCARTADA" : (extras.status || "GENERADA"));
  console.log(`${status} ${item.id} ${item.file}`);
  return {
    id: item.id,
    file: item.file,
    title: pageInfo.title,
    url: pageInfo.url,
    path: filePath,
    width: WIDTH,
    height: HEIGHT,
    privacy: privacyIssues.length ? privacyIssues.join("; ") : "OK",
    status,
    note: extras.note || "",
    dialogs: extras.dialogs || [],
  };
}

function privacyScan(text, url) {
  const issues = [];
  const visible = text || "";
  if (/@(gmail|hotmail|outlook|yahoo)\./i.test(visible)) issues.push("correo no demo visible");
  if (/admin123|demo-password|password-demo/i.test(visible)) issues.push("posible credencial visible");
  if (/127\.0\.0\.1:\d+\/registro\/confirmar-asistencia\/[0-9a-f-]{36}/i.test(visible)) issues.push("token visible en contenido");
  if (/token=[0-9a-f-]{16,}/i.test(`${visible} ${url}`)) issues.push("token en querystring");
  return issues;
}

async function fillForm(client, values) {
  await evaluate(client, `(() => {
    const values = ${JSON.stringify(values)};
    for (const [name, value] of Object.entries(values)) {
      const el = document.querySelector('[name="' + CSS.escape(name) + '"]');
      if (!el) continue;
      el.focus();
      el.value = value;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
    return true;
  })()`);
  await sleep(250);
}

async function submitFirstForm(client) {
  await evaluate(client, `(() => {
    const form = document.querySelector("form");
    if (!form) return false;
    form.requestSubmit ? form.requestSubmit() : form.submit();
    return true;
  })()`);
  await client.waitForLoad();
}

async function login(client) {
  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf8"));
  await navigate(client, "/torneo/control/login/");
  await fillForm(client, { username: credentials.username, password: credentials.password });
  await submitFirstForm(client);
  await navigate(client, "/torneo/control/");
}

async function openDetails(client, selector) {
  await evaluate(client, `(() => {
    document.querySelectorAll(${JSON.stringify(selector)}).forEach((item) => { item.open = true; });
    return true;
  })()`);
  await sleep(250);
}

async function clickSelector(client, selector) {
  return evaluate(client, `new Promise((resolve) => {
    const el = document.querySelector(${JSON.stringify(selector)});
    if (!el) { resolve(false); return; }
    el.click();
    setTimeout(() => resolve(true), 700);
  })`, true);
}

async function discoverUrls(client, summary) {
  const schoolId = summary.competitions?.school;
  const firstDivisionUrl = schoolId ? `${BASE_URL}/torneo/control/divisiones/${schoolId}/` : await evaluate(client, `(() => document.querySelector('a[href*="/torneo/control/divisiones/"]')?.href || "")()`);
  return {
    division: firstDivisionUrl,
    groups: `${firstDivisionUrl}fases/groups/`,
    quarterfinal: `${firstDivisionUrl}fases/quarterfinal/`,
    semifinal: `${firstDivisionUrl}fases/semifinal/`,
    final: `${firstDivisionUrl}fases/final/`,
  };
}

function itemById(id) {
  const row = capturePlan.find((item) => item[0] === id);
  return { id: row[0], file: row[1], procedure: row[2], route: row[3] };
}

async function runCapture(client, id, action, manifest) {
  const item = itemById(id);
  try {
    const meta = await action(item);
    manifest.push(meta || await capture(client, item));
  } catch (error) {
    console.error(`ERROR ${id} ${item.file}: ${error.stack || error.message || error}`);
    manifest.push({
      id,
      file: item.file,
      status: "ERROR",
      privacy: "NO EVALUADA",
      note: String(error.message || error),
    });
  }
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.mkdirSync(REVIEW_DIR, { recursive: true });
  fs.mkdirSync(DISCARDED_DIR, { recursive: true });

  const summary = JSON.parse(fs.readFileSync(SUMMARY_PATH, "utf8"));
  const browser = findBrowser();
  const profileDir = path.join(DEMO_ROOT, "edge-profile-banco");
  if (!profileDir.startsWith(DEMO_ROOT)) throw new Error("Perfil temporal fuera del entorno demo.");
  fs.rmSync(profileDir, { recursive: true, force: true });
  fs.mkdirSync(profileDir, { recursive: true });

  const proc = spawn(browser, [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profileDir}`,
    `--window-size=${WIDTH},${HEIGHT}`,
    "about:blank",
  ], { stdio: "ignore" });

  const manifest = [];
  let client;
  try {
    const version = await waitForJson(`http://127.0.0.1:${PORT}/json/version`);
    const tabs = await waitForJson(`http://127.0.0.1:${PORT}/json/list`);
    const page = tabs.find((tab) => tab.type === "page") || tabs[0];
    client = new CdpClient(page.webSocketDebuggerUrl || version.webSocketDebuggerUrl);
    await client.open();
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await client.send("Page.setLifecycleEventsEnabled", { enabled: true });
    await setViewport(client);

    const publicRoutes = ["MU-001", "MU-002", "MU-003", "MU-004", "MU-008", "MU-011", "MU-012"];
    for (const id of publicRoutes) {
      await runCapture(client, id, async (item) => {
        await navigate(client, item.route);
        return capture(client, item);
      }, manifest);
    }

    await runCapture(client, "MU-005", async (item) => {
      await navigate(client, item.route);
      await fillForm(client, {
        institution_name: "Colegio Captura Demo",
        responsible_name: "Docente Captura Demo",
        robot_name: "Robot Captura Escolar",
        leader_name: "Integrante Escolar Demo",
        contact_phone: "3000000001",
        leader_document_number: "9900000001",
        contact_email: "captura.escolar@example.com",
      });
      await scrollTo(client, 220);
      return capture(client, item);
    }, manifest);

    await runCapture(client, "MU-006", async (item) => {
      await navigate(client, item.route);
      await fillForm(client, {
        institution_name: "Institucion Registro Demo",
        responsible_name: "Responsable Registro Demo",
        robot_name: "Robot Registro Demo",
        leader_name: "Participante Registro Demo",
        contact_phone: "3110000001",
        leader_document_number: "9100000001",
        contact_email: "registro.demo@example.com",
      });
      await submitFirstForm(client);
      await scrollTo(client, 160);
      return capture(client, item);
    }, manifest);

    await runCapture(client, "MU-007", async (item) => {
      await navigate(client, item.route);
      await fillForm(client, {
        institution_name: "Universidad Captura Demo",
        responsible_name: "Docente Universidad Demo",
        robot_name: "Robot Captura Universidad",
        semester: "3",
        leader_name: "Integrante Universidad Demo",
        contact_phone: "3000000002",
        leader_document_number: "9900000002",
        contact_email: "captura.universidad@example.com",
      });
      await scrollTo(client, 220);
      return capture(client, item);
    }, manifest);

    await runCapture(client, "MU-009", async (item) => {
      await navigate(client, `/registro/confirmar-asistencia/${summary.attendance_tokens.pending_school}/`);
      return capture(client, item);
    }, manifest);

    await runCapture(client, "MU-010", async (item) => {
      await navigate(client, `/registro/confirmar-asistencia/${summary.attendance_tokens.confirmed_school}/`);
      return capture(client, item);
    }, manifest);

    await login(client);
    const urls = await discoverUrls(client, summary);

    await runCapture(client, "MU-013", async (item) => {
      await navigate(client, item.route);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-014", async (item) => {
      await navigate(client, item.route);
      await scrollTo(client, 320);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-015", async (item) => {
      await navigate(client, urls.division);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-016", async (item) => {
      await navigate(client, urls.division);
      await openDetails(client, "details.disclosure-panel");
      await scrollTo(client, 820);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-017", async (item) => {
      await navigate(client, urls.division);
      await openDetails(client, "details.heavy-panel");
      await scrollTo(client, 1180);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-018", async (item) => {
      await navigate(client, urls.groups);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-019", async (item) => {
      await navigate(client, urls.groups);
      await scrollTo(client, 520);
      return capture(client, item, { note: "Captura base del boton guardar grupo; el dialogo nativo no se renderiza en PNG headless." });
    }, manifest);
    await runCapture(client, "MU-020", async (item) => {
      await navigate(client, urls.groups);
      await scrollTo(client, 0);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-021", async (item) => {
      await navigate(client, urls.division);
      await clickSelector(client, "[data-phase-decision-open]");
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-022", async (item) => {
      await navigate(client, urls.division);
      await clickSelector(client, "[data-phase-decision-open]");
      await clickSelector(client, "[data-phase-decision-use-recommendation]");
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-023", async (item) => {
      await navigate(client, urls.division);
      await clickSelector(client, "[data-phase-decision-open]");
      await clickSelector(client, "[data-phase-decision-use-recommendation]");
      await clickSelector(client, "[data-phase-repechage-open]");
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-024", async (item) => {
      await navigate(client, urls.division);
      await clickSelector(client, "[data-phase-decision-open]");
      await clickSelector(client, "[data-phase-decision-manual]");
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-025", async (item) => {
      await navigate(client, urls.division);
      await clickSelector(client, "[data-phase-decision-open]");
      await clickSelector(client, "[data-phase-decision-manual]");
      await scrollTo(client, 260);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-026", async (item) => {
      await navigate(client, urls.semifinal);
      await evaluate(client, `(() => {
        document.querySelector("[data-result-form]")?.scrollIntoView({ block: "start" });
        return true;
      })()`);
      await sleep(250);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-027", async (item) => {
      await navigate(client, urls.quarterfinal);
      await evaluate(client, `(() => {
        document.querySelector("[data-result-form]")?.scrollIntoView({ block: "start" });
        return true;
      })()`);
      await sleep(250);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-028", async (item) => {
      await navigate(client, urls.semifinal);
      await evaluate(client, `(() => {
        document.querySelector("[data-result-form]")?.scrollIntoView({ block: "start" });
        return true;
      })()`);
      await sleep(250);
      await evaluate(client, `(() => {
        const form = document.querySelector("[data-result-form]");
        const input = form?.querySelector("input[name='winner_team_id']:not(:checked)");
        if (input) {
          input.checked = true;
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
        return Boolean(input);
      })()`);
      return capture(client, item, {
        status: "GENERADA_PARCIAL",
        note: "Estado inmediatamente anterior a window.confirm/manual_override; CDP documenta el dialogo, pero el dialogo nativo no aparece en screenshot headless.",
        dialogs: client.dialogs,
      });
    }, manifest);
    await runCapture(client, "MU-029", async (item) => {
      await navigate(client, urls.groups);
      await clickSelector(client, ".participant-trigger[data-participant-state-id]");
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-030", async (item) => {
      await navigate(client, urls.groups);
      await clickSelector(client, ".participant-trigger[data-participant-state-id]");
      await evaluate(client, `(() => {
        const select = document.querySelector("[data-participant-modal] select");
        if (select && select.options.length > 1) select.selectedIndex = Math.min(1, select.options.length - 1);
        return true;
      })()`);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-031", async (item) => {
      await navigate(client, urls.final);
      await scrollTo(client, 460);
      return capture(client, item);
    }, manifest);

    const communicationRoutes = ["MU-032", "MU-033", "MU-034", "MU-036", "MU-038", "MU-039", "MU-040", "MU-041", "MU-042"];
    for (const id of communicationRoutes) {
      await runCapture(client, id, async (item) => {
        await navigate(client, item.route);
        if (id === "MU-037") await scrollTo(client, 520);
        return capture(client, item);
      }, manifest);
    }

    await runCapture(client, "MU-035", async (item) => {
      await navigate(client, "/comunicaciones/plantillas/");
      const previewUrl = await evaluate(client, `(() => document.querySelector('a[href*="/previsualizar/"]')?.href || "")()`);
      if (!previewUrl) throw new Error("No se encontro enlace de previsualizacion.");
      await navigate(client, previewUrl);
      return capture(client, item);
    }, manifest);
    await runCapture(client, "MU-037", async (item) => {
      await navigate(client, item.route);
      await fillForm(client, {
        name: "Destinatario Manual Captura",
        email: "destinatario.manual@example.com",
        institution_name: "Institucion Manual Demo",
      });
      await scrollTo(client, 520);
      return capture(client, item);
    }, manifest);
  } finally {
    if (client) client.close();
    proc.kill("SIGTERM");
    await sleep(1000);
    if (!proc.killed) proc.kill("SIGKILL");
    fs.writeFileSync(MANIFEST_PATH, JSON.stringify({
      generated_at: new Date().toISOString(),
      base_url: BASE_URL,
      width: WIDTH,
      height: HEIGHT,
      manifest,
    }, null, 2), "utf8");
    if (profileDir.startsWith(DEMO_ROOT)) fs.rmSync(profileDir, { recursive: true, force: true });
  }

  const failed = manifest.filter((item) => item.status === "ERROR");
  if (failed.length) {
    process.exitCode = 2;
  }
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exit(1);
});
