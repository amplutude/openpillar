(function () {
  'use strict';

  // ── Version history ───────────────────────────────────────────
  let versionsData = null;

  async function fetchVersions() {
    if (versionsData) return versionsData;
    try {
      const res = await fetch('versions.json');
      versionsData = res.ok ? await res.json() : { policies: {} };
    } catch {
      versionsData = { policies: {} };
    }
    return versionsData;
  }

  window.toggleVersionHistory = async function (btn) {
    const timeline = document.getElementById('version-timeline');
    if (!timeline) return;
    if (!timeline.hidden) { timeline.hidden = true; return; }

    const ids = (btn.dataset.policyIds || '').split(',').filter(Boolean);
    const versions = await fetchVersions();
    const polMap = versions.policies || {};
    let html = '';

    for (const polId of ids) {
      const entry = polMap[polId];
      if (!entry) continue;
      const archived = entry.archived_versions || [];
      html += `<div style="margin-bottom:1.25rem">
        <strong style="font-size:0.8rem;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:.06em">${polId}</strong>
        <div class="timeline__item">
          <span class="timeline__version">v${entry.version}</span>
          ${entry.deployed_at ? `<span class="timeline__date">${entry.deployed_at.slice(0, 10)}</span>` : ''}
          <span class="badge badge--active" style="margin-left:.5rem;font-size:.65rem">current</span>
          <div class="timeline__links">
            <a href="${entry.github_ref}" target="_blank" rel="noopener">View on GitHub ↗</a>
          </div>
        </div>`;
      for (const ver of [...archived].reverse()) {
        html += `<div class="timeline__item">
          <span class="timeline__version">v${ver}</span>
          <div class="timeline__links">
            <a href="archive/${polId}/${ver}/policy.json" target="_blank" rel="noopener">Archived JSON ↗</a>
            <a href="${entry.github_ref}" target="_blank" rel="noopener">GitHub ↗</a>
          </div>
        </div>`;
      }
      if (!archived.length) {
        html += `<div style="font-size:.8rem;color:var(--color-text-muted);padding:.4rem 0 0 1.25rem">No previous versions archived yet.</div>`;
      }
      html += '</div>';
    }

    timeline.innerHTML = html || '<div style="padding:.5rem 0;font-size:.85rem;color:var(--color-text-muted)">No version history available.</div>';
    timeline.hidden = false;
  };

  // ── Policy reference card toggles ─────────────────────────────
  function initPolicyCards() {
    document.querySelectorAll('.policy-card').forEach(card => {
      const header = card.querySelector('.policy-card__header');
      if (!header) return;
      header.addEventListener('click', () => {
        card.classList.toggle('policy-card--open');
      });
    });
  }

  // ── Mobile hamburger ──────────────────────────────────────────
  function initHamburger() {
    const btn = document.getElementById('hamburger');
    const nav = document.querySelector('.topnav__nav');
    if (!btn || !nav) return;
    btn.addEventListener('click', () => {
      const open = nav.style.display === 'flex';
      nav.style.display = open ? '' : 'flex';
      nav.style.flexDirection = 'column';
      nav.style.position = 'absolute';
      nav.style.top = 'var(--topnav-height)';
      nav.style.left = '0';
      nav.style.right = '0';
      nav.style.background = 'var(--color-navy)';
      nav.style.padding = '1rem 1.5rem';
      nav.style.gap = '1rem';
      nav.style.borderTop = '1px solid rgba(255,255,255,.08)';
    });
  }

  // ── Search — redirects to homepage with highlight ─────────────
  function initSearch() {
    const input = document.getElementById('search');
    if (!input) return;
    input.addEventListener('keydown', e => {
      if (e.key !== 'Enter') return;
      const q = input.value.trim();
      if (!q) return;
      // Find root relative to current page by counting path depth
      const depth = (window.location.pathname.match(/\//g) || []).length - 1;
      const root = depth > 0 ? '../'.repeat(depth) : '';
      window.location.href = `${root}index.html#search=${encodeURIComponent(q)}`;
    });
  }

  // ── Homepage: highlight from hash search ─────────────────────
  function initHomepageSearch() {
    const hash = window.location.hash;
    const match = hash.match(/^#search=(.+)$/);
    if (!match) return;
    const q = decodeURIComponent(match[1]).toLowerCase();
    document.querySelectorAll('.pillar-card').forEach(card => {
      const text = card.textContent.toLowerCase();
      if (!text.includes(q)) {
        card.style.opacity = '0.4';
      } else {
        card.style.boxShadow = '0 0 0 2px var(--color-accent)';
      }
    });
  }

  // ── Topnav active link ────────────────────────────────────────
  function initActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.topnav__nav a').forEach(a => {
      const href = a.getAttribute('href') || '';
      if (href && path.endsWith(href.replace(/^.*\//, ''))) {
        a.style.color = '#fff';
        a.style.fontWeight = '600';
      }
    });
  }

  // ── Init ──────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    initPolicyCards();
    initHamburger();
    initSearch();
    initActiveNav();
    if (document.querySelector('.pillars-grid')) {
      initHomepageSearch();
    }
  });
})();
