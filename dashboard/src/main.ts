import "./styles.css";

// ─── Theme management ────────────────────────────────────────────────────────

type ThemeMode = "dark" | "light" | "system";

const THEME_KEY = "nemo-dashboard-theme";
const STORAGE_KEY = "nemo-dashboard-gateway-url";

function resolveSystemTheme(): "dark" | "light" {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(mode: ThemeMode) {
  const resolved = mode === "system" ? resolveSystemTheme() : mode;
  document.documentElement.setAttribute("data-theme", resolved);
  localStorage.setItem(THEME_KEY, mode);
}

function loadTheme(): ThemeMode {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "dark" || stored === "light" || stored === "system") return stored;
  return "system";
}

function currentTheme(): "dark" | "light" {
  return (document.documentElement.getAttribute("data-theme") as "dark" | "light") ?? "dark";
}

// ─── Icons ────────────────────────────────────────────────────────────────────

const icons = {
  messageSquare: `<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  link: `<svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`,
  folder: `<svg viewBox="0 0 24 24"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`,
  loader: `<svg viewBox="0 0 24 24"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>`,
  fileText: `<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
  barChart: `<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
  zap: `<svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
  monitor: `<svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
  settings: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M19.07 19.07l-1.41-1.41M4.93 19.07l1.41-1.41M22 12h-2M4 12H2M12 22v-2M12 4V2"/></svg>`,
  radio: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>`,
  sun: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`,
  moon: `<svg viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`,
  externalLink: `<svg viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`,
  book: `<svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>`,
  arrowRight: `<svg viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`,
  github: `<svg viewBox="0 0 24 24"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>`,
};

// ─── Feature definitions ──────────────────────────────────────────────────────

const features: Array<{
  icon: string;
  iconClass: string;
  title: string;
  desc: string;
  tab: string;
  stagger: number;
}> = [
  {
    icon: icons.messageSquare,
    iconClass: "icon-accent",
    title: "Chat",
    desc: "Direct gateway chat session for real-time agent interaction and quick interventions.",
    tab: "chat",
    stagger: 1,
  },
  {
    icon: icons.link,
    iconClass: "icon-teal",
    title: "Channels",
    desc: "Connect WhatsApp, Telegram, Discord, Signal, iMessage, and more in one place.",
    tab: "channels",
    stagger: 2,
  },
  {
    icon: icons.folder,
    iconClass: "icon-info",
    title: "Agents",
    desc: "Manage agent workspaces, tools, skills, and identities across your fleet.",
    tab: "agents",
    stagger: 3,
  },
  {
    icon: icons.fileText,
    iconClass: "icon-ok",
    title: "Sessions",
    desc: "Inspect active sessions, adjust per-session defaults, and manage context.",
    tab: "sessions",
    stagger: 4,
  },
  {
    icon: icons.barChart,
    iconClass: "icon-info",
    title: "Usage",
    desc: "Track token usage, costs, and session analytics with rich charts.",
    tab: "usage",
    stagger: 5,
  },
  {
    icon: icons.loader,
    iconClass: "icon-warn",
    title: "Cron Jobs",
    desc: "Schedule recurring agent wakeups and automation with cron expressions.",
    tab: "cron",
    stagger: 6,
  },
  {
    icon: icons.zap,
    iconClass: "icon-accent",
    title: "Skills",
    desc: "Manage skill availability, API key injection, and per-agent overrides.",
    tab: "skills",
    stagger: 1,
  },
  {
    icon: icons.monitor,
    iconClass: "icon-teal",
    title: "Nodes",
    desc: "Paired devices, capabilities, and command exposure across your network.",
    tab: "nodes",
    stagger: 2,
  },
  {
    icon: icons.settings,
    iconClass: "icon-ok",
    title: "Config",
    desc: "Edit nemo.json safely with form and raw editor, schema validation included.",
    tab: "config",
    stagger: 3,
  },
];

const quickLinks: Array<{ icon: string; iconClass: string; label: string; tab: string; stagger: number }> = [
  { icon: icons.messageSquare, iconClass: "icon-accent", label: "Chat", tab: "chat", stagger: 1 },
  { icon: icons.link, iconClass: "icon-teal", label: "Channels", tab: "channels", stagger: 2 },
  { icon: icons.folder, iconClass: "icon-info", label: "Agents", tab: "agents", stagger: 3 },
  { icon: icons.fileText, iconClass: "icon-ok", label: "Sessions", tab: "sessions", stagger: 4 },
  { icon: icons.barChart, iconClass: "icon-info", label: "Usage", tab: "usage", stagger: 5 },
  { icon: icons.loader, iconClass: "icon-warn", label: "Cron Jobs", tab: "cron", stagger: 6 },
  { icon: icons.radio, iconClass: "icon-accent", label: "Instances", tab: "instances", stagger: 1 },
  { icon: icons.zap, iconClass: "icon-teal", label: "Skills", tab: "skills", stagger: 2 },
  { icon: icons.monitor, iconClass: "icon-ok", label: "Nodes", tab: "nodes", stagger: 3 },
  { icon: icons.settings, iconClass: "icon-info", label: "Config", tab: "config", stagger: 4 },
];

// ─── Gateway URL helpers ──────────────────────────────────────────────────────

function loadGatewayUrl(): string {
  return localStorage.getItem(STORAGE_KEY) ?? "";
}

function saveGatewayUrl(url: string) {
  if (url.trim()) {
    localStorage.setItem(STORAGE_KEY, url.trim());
  }
}

function buildControlUiUrl(gatewayUrl: string, tab: string): string {
  const base = gatewayUrl.trim();
  if (!base) return `/${tab}`;
  // Derive the Control UI HTTP URL from the gateway WebSocket URL
  const httpBase = base.replace(/^wss?:\/\//, (m) => (m.startsWith("wss") ? "https://" : "http://"));
  const clean = httpBase.replace(/\/$/, "");
  return `${clean}/${tab}?gatewayUrl=${encodeURIComponent(base)}`;
}

// ─── Render helpers ───────────────────────────────────────────────────────────

function renderTopbar(themeMode: ThemeMode): string {
  const isDark = currentTheme() === "dark";
  return `
    <header class="topbar">
      <div class="topbar-left">
        <a class="brand" href="#" title="NEMO Dashboard">
          <div class="brand-logo"><img src="./favicon.svg" alt="NEMO" /></div>
          <div class="brand-text">
            <div class="brand-title">NEMO</div>
            <div class="brand-sub">Gateway Dashboard</div>
          </div>
        </a>
      </div>
      <div class="topbar-right">
        <a class="nav-link" href="https://docs.nemo.ai" target="_blank" rel="noreferrer">Docs</a>
        <a class="nav-link" href="https://github.com/sentientsprite/nemo-agent" target="_blank" rel="noreferrer">GitHub</a>
        <button class="theme-btn" id="theme-toggle" title="Toggle theme" aria-label="Toggle theme">
          ${isDark ? icons.sun : icons.moon}
        </button>
      </div>
    </header>
  `;
}

function renderHero(): string {
  return `
    <section class="hero">
      <div class="hero-badge">
        <span class="hero-badge-dot"></span>
        <span>Gateway Control UI</span>
      </div>
      <h1 class="hero-title">
        Your AI agent gateway<br/><span class="accent">dashboard</span>
      </h1>
      <p class="hero-sub">
        A unified control plane for managing agents, channels, sessions, and automation — all from one place.
      </p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="https://docs.nemo.ai" target="_blank" rel="noreferrer">
          Get started
        </a>
        <a class="btn btn-secondary" href="https://docs.nemo.ai/web/control-ui" target="_blank" rel="noreferrer">
          Open Control UI docs
        </a>
      </div>
    </section>
  `;
}

function renderConnectCard(gatewayUrl: string): string {
  return `
    <section class="connect-section">
      <div class="connect-card">
        <div class="connect-card-title">Connect to your gateway</div>
        <div class="connect-card-sub">Enter your gateway WebSocket URL to open the Control UI. The URL is saved locally.</div>
        <div class="connect-input-row">
          <input
            class="connect-input"
            id="gateway-url-input"
            type="text"
            placeholder="ws://100.x.y.z:18789"
            value="${escapeAttr(gatewayUrl)}"
            spellcheck="false"
            autocomplete="off"
          />
          <button class="btn btn-primary" id="open-dashboard-btn">Open dashboard</button>
        </div>
      </div>
    </section>
  `;
}

function renderStatsBar(): string {
  return `
    <div class="stats-bar">
      <div class="stat-item">
        <div class="stat-item-value accent">13+</div>
        <div class="stat-item-label">Tabs &amp; views</div>
      </div>
      <div class="stat-item">
        <div class="stat-item-value teal">10+</div>
        <div class="stat-item-label">Channels</div>
      </div>
      <div class="stat-item">
        <div class="stat-item-value ok">Live</div>
        <div class="stat-item-label">WebSocket sync</div>
      </div>
      <div class="stat-item">
        <div class="stat-item-value">Dark / Light</div>
        <div class="stat-item-label">Themes</div>
      </div>
    </div>
  `;
}

function renderFeatures(): string {
  const cards = features
    .map(
      (f) => `
      <div class="feature-card stagger-${f.stagger}" data-tab="${escapeAttr(f.tab)}">
        <div class="feature-card-icon ${f.iconClass}">${f.icon}</div>
        <div class="feature-card-title">${f.title}</div>
        <div class="feature-card-desc">${f.desc}</div>
      </div>
    `,
    )
    .join("");

  return `
    <section class="section">
      <div class="section-header">
        <div class="section-label">Features</div>
        <h2 class="section-title">Everything you need to control your agents</h2>
        <p class="section-sub">The Control UI gives you deep visibility and control over every part of your NEMO gateway.</p>
      </div>
      <div class="feature-grid">${cards}</div>
    </section>
  `;
}

function renderQuickLinks(gatewayUrl: string): string {
  const links = quickLinks
    .map(
      (l) => `
      <a class="quick-link stagger-${l.stagger}" href="${escapeAttr(buildControlUiUrl(gatewayUrl, l.tab))}" ${gatewayUrl ? "" : 'target="_blank" rel="noreferrer"'} data-tab="${escapeAttr(l.tab)}">
        <span class="quick-link-icon ${l.iconClass}">${l.icon}</span>
        <span class="quick-link-label">${l.label}</span>
        <span class="quick-link-arrow">→</span>
      </a>
    `,
    )
    .join("");

  return `
    <section class="section">
      <div class="section-header">
        <div class="section-label">Quick access</div>
        <h2 class="section-title">Jump straight to any view</h2>
        <p class="section-sub">Connect your gateway above, then click any link to open that view directly.</p>
      </div>
      <div class="quick-links-grid" id="quick-links-grid">${links}</div>
    </section>
  `;
}

function renderSetup(): string {
  return `
    <section class="setup-section">
      <div class="setup-card">
        <div class="setup-card-header">
          <div class="setup-card-title">Getting started</div>
          <div class="setup-card-sub">Set up NEMO on any machine in a few steps.</div>
        </div>
        <div class="setup-steps">
          <div class="setup-step">
            <div class="step-num">1</div>
            <div class="step-content">
              <div class="step-title">Install NEMO</div>
              <div class="step-desc">Install the CLI globally via npm.
                <div><code class="code-block">npm install -g nemo-agent</code></div>
              </div>
            </div>
          </div>
          <div class="setup-step">
            <div class="step-num">2</div>
            <div class="step-content">
              <div class="step-title">Start the gateway</div>
              <div class="step-desc">Launch the local gateway to serve the Control UI on port 18789.
                <div><code class="code-block">nemo gateway run</code></div>
              </div>
            </div>
          </div>
          <div class="setup-step">
            <div class="step-num">3</div>
            <div class="step-content">
              <div class="step-title">Open the dashboard</div>
              <div class="step-desc">Open the Control UI in your browser, or paste the gateway URL above.
                <div><code class="code-block">nemo dashboard</code></div>
              </div>
            </div>
          </div>
          <div class="setup-step">
            <div class="step-num">4</div>
            <div class="step-content">
              <div class="step-title">Connect channels</div>
              <div class="step-desc">Head to the Channels tab to link WhatsApp, Telegram, Discord, Signal, and more.</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderFooter(): string {
  return `
    <footer class="footer">
      <div class="footer-left">
        <div class="footer-logo"><img src="./favicon.svg" alt="NEMO" /></div>
        <span>NEMO Gateway Dashboard</span>
      </div>
      <div class="footer-links">
        <a class="footer-link" href="https://docs.nemo.ai" target="_blank" rel="noreferrer">Docs</a>
        <a class="footer-link" href="https://github.com/sentientsprite/nemo-agent" target="_blank" rel="noreferrer">GitHub</a>
        <a class="footer-link" href="https://docs.nemo.ai/web/control-ui" target="_blank" rel="noreferrer">Control UI</a>
      </div>
    </footer>
  `;
}

function escapeAttr(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ─── Main render ──────────────────────────────────────────────────────────────

function render() {
  const gatewayUrl = loadGatewayUrl();
  const themeMode = loadTheme();
  applyTheme(themeMode);

  const app = document.getElementById("app");
  if (!app) return;

  app.innerHTML = `
    <div class="page-wrapper">
      ${renderTopbar(themeMode)}
      ${renderHero()}
      ${renderConnectCard(gatewayUrl)}
      ${renderStatsBar()}
      ${renderFeatures()}
      ${renderQuickLinks(gatewayUrl)}
      ${renderSetup()}
      <hr class="divider" />
      ${renderFooter()}
    </div>
  `;

  wireEvents();
}

// ─── Event wiring ─────────────────────────────────────────────────────────────

function wireEvents() {
  const themeBtn = document.getElementById("theme-toggle");
  const gatewayInput = document.getElementById("gateway-url-input") as HTMLInputElement | null;
  const openBtn = document.getElementById("open-dashboard-btn");
  const quickLinksGrid = document.getElementById("quick-links-grid");

  themeBtn?.addEventListener("click", () => {
    const current = currentTheme();
    const next: ThemeMode = current === "dark" ? "light" : "dark";
    applyTheme(next);
    // Re-render to update the theme icon
    render();
  });

  openBtn?.addEventListener("click", () => {
    const url = gatewayInput?.value.trim() ?? "";
    if (!url) {
      window.open("http://127.0.0.1:18789/", "_blank");
      return;
    }
    saveGatewayUrl(url);
    const dashUrl = buildControlUiUrl(url, "chat");
    window.open(dashUrl, "_blank");
  });

  gatewayInput?.addEventListener("keydown", (e: KeyboardEvent) => {
    if (e.key === "Enter") {
      openBtn?.click();
    }
  });

  gatewayInput?.addEventListener("input", () => {
    const url = gatewayInput.value.trim();
    // Update quick links in place without full re-render
    const links = quickLinksGrid?.querySelectorAll<HTMLAnchorElement>("a.quick-link");
    links?.forEach((link) => {
      const tab = link.dataset.tab ?? "chat";
      link.href = buildControlUiUrl(url, tab);
    });
  });
}

// ─── Init ─────────────────────────────────────────────────────────────────────

render();
