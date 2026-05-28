(function () {
  'use strict';

  let appData = null;
  let versionsData = null;
  const sidebar = document.getElementById('sidebar-nav');
  const loading = document.getElementById('sidebar-loading');
  const welcome = document.getElementById('welcome');
  const policyView = document.getElementById('policy-view');
  const searchInput = document.getElementById('search');

  // --- Data fetching ---
  async function fetchData() {
    const res = await fetch('data.json');
    if (!res.ok) throw new Error('Failed to load data.json');
    return res.json();
  }

  async function fetchVersions() {
    try {
      const res = await fetch('versions.json');
      if (!res.ok) return { policies: {} };
      return res.json();
    } catch {
      return { policies: {} };
    }
  }

  // --- Environment banner ---
  function initEnvBanner(env) {
    const badge = document.getElementById('env-badge');
    if (env === 'test') {
      badge.textContent = 'TEST';
      badge.style.display = 'inline-block';
      const banner = document.createElement('div');
      banner.id = 'env-banner';
      banner.textContent = '⚠ TEST ENVIRONMENT — This site reflects test policy content, not production.';
      document.body.insertBefore(banner, document.body.firstChild);
      document.documentElement.style.setProperty('--banner-height', '32px');
    }
  }

  // --- Sidebar rendering ---
  function badgeHtml(status) {
    const cls = ['active','draft','retired','deprecated'].includes(status) ? status : 'draft';
    return `<span class="badge badge--${cls}">${status || 'unknown'}</span>`;
  }

  function renderSidebar(pillars, filter = '') {
    const q = filter.toLowerCase();
    let html = '';
    for (const pillar of pillars) {
      const matchingSubs = pillar.sub_pillars.filter(s =>
        !q || s.name.toLowerCase().includes(q) || (s.id||'').toLowerCase().includes(q) ||
        (s.tags||[]).some(t => t.toLowerCase().includes(q))
      );
      if (q && matchingSubs.length === 0) continue;
      const open = q ? 'open' : '';
      html += `<details ${open}>
        <summary>
          <span>${pillar.name}</span>
          <small style="opacity:0.5;font-size:0.75rem;margin-left:auto">${pillar.id}</small>
        </summary>`;
      const subs = q ? matchingSubs : pillar.sub_pillars;
      for (const sub of subs) {
        const active = location.hash === '#sub/' + sub.id ? ' sidebar__item--active' : '';
        html += `<a class="sidebar__item${active}" data-id="${sub.id}" href="#sub/${sub.id}">${sub.name}
          <div style="font-size:0.7rem;opacity:0.6;margin-top:2px">${sub.id}</div>
        </a>`;
      }
      html += `</details>`;
    }
    if (!html) html = '<div style="padding:1rem;color:#64748b;font-size:0.85rem">No results</div>';
    sidebar.innerHTML = html;
    sidebar.hidden = false;
    if (loading) loading.hidden = true;
  }

  // --- Find sub-pillar by ID ---
  function findSubPillar(id) {
    for (const pillar of appData.pillars) {
      for (const sub of pillar.sub_pillars) {
        if (sub.id === id) return { sub, pillar };
      }
    }
    return null;
  }

  // --- Policy view rendering ---
  function renderPolicy(sub, pillar) {
    welcome.hidden = true;
    policyView.hidden = false;

    const tagsHtml = (sub.tags || []).map(t => `<span class="tag">${t}</span>`).join(' ');
    const refs = sub.resolved_policies || [];

    let refsHtml = '';
    if (refs.length > 0) {
      refsHtml = '<div class="policy-refs"><h2 style="font-size:1.1rem;margin-top:2.5rem;margin-bottom:1rem">Referenced Policies</h2>';
      for (const pol of refs) {
        refsHtml += `
          <div class="policy-card">
            <div class="policy-card__header" onclick="this.parentElement.querySelector('.policy-card__body').style.display = this.parentElement.querySelector('.policy-card__body').style.display === 'none' ? 'block' : 'none'">
              <div class="policy-card__title">
                <span class="badge badge--active" style="font-size:0.65rem">${pol.id}</span>
                ${pol.name}
              </div>
              <div style="display:flex;gap:0.75rem;align-items:center">
                ${badgeHtml(pol.status)}
                <span style="font-size:0.8rem;color:var(--color-text-muted)">v${pol.version}</span>
                <span style="color:var(--color-text-muted)">▾</span>
              </div>
            </div>
            <div class="policy-card__body">
              <div class="policy-body">${marked.parse(pol.policy_markdown || '')}</div>
            </div>
          </div>`;
      }
      refsHtml += '</div>';
    }

    const versionHistoryId = 'vh-' + sub.id.replace(/[^a-z0-9]/gi, '-');

    policyView.innerHTML = `
      <div class="policy-header">
        <div class="policy-header__id">${pillar.name} / ${sub.id}</div>
        <div class="policy-header__name">${sub.name}</div>
        <div class="policy-meta">
          ${sub.owner ? `<div class="policy-meta__item"><span>Owner</span><span class="policy-meta__value">${sub.owner}</span></div>` : ''}
          ${sub.version ? `<div class="policy-meta__item"><span>Version</span><span class="policy-meta__value">${sub.version}</span></div>` : ''}
          ${sub.effective_date ? `<div class="policy-meta__item"><span>Effective</span><span class="policy-meta__value">${sub.effective_date}</span></div>` : ''}
          ${sub.review_date ? `<div class="policy-meta__item"><span>Review</span><span class="policy-meta__value">${sub.review_date}</span></div>` : ''}
          ${sub.status ? `<div class="policy-meta__item">${badgeHtml(sub.status)}</div>` : ''}
        </div>
        ${tagsHtml ? `<div style="margin-top:0.5rem">${tagsHtml}</div>` : ''}
      </div>
      <div class="policy-body" style="margin-top:1.75rem">${marked.parse(sub.policy_markdown || '')}</div>
      ${refsHtml}
      <div class="version-history" id="${versionHistoryId}">
        <button class="version-history__toggle" onclick="toggleVersionHistory('${versionHistoryId}', ${JSON.stringify(refs.map(r=>r.id))})">
          📋 Version History
        </button>
        <div class="timeline" id="${versionHistoryId}-timeline" hidden></div>
      </div>
    `;
  }

  // --- Version history ---
  window.toggleVersionHistory = function(containerId, policyIds) {
    const timeline = document.getElementById(containerId + '-timeline');
    if (!timeline.hidden) { timeline.hidden = true; return; }

    let html = '';
    const polMap = versionsData.policies || {};
    for (const polId of policyIds) {
      const entry = polMap[polId];
      if (!entry) continue;
      const archived = entry.archived_versions || [];
      html += `<div style="margin-bottom:1rem"><strong style="font-size:0.85rem;color:var(--color-text-muted)">${polId}</strong>`;
      // Current version
      html += `<div class="timeline__item">
        <span class="timeline__version">v${entry.version}</span>
        <span class="timeline__date">${entry.deployed_at ? entry.deployed_at.slice(0,10) : ''}</span>
        <span class="badge badge--active" style="margin-left:0.5rem;font-size:0.65rem">current</span>
        <div class="timeline__links">
          <a href="${entry.github_ref}" target="_blank" rel="noopener">View on GitHub ↗</a>
        </div>
      </div>`;
      // Archived versions
      for (const ver of [...archived].reverse()) {
        const archivePath = `archive/${polId}/${ver}/policy.json`;
        html += `<div class="timeline__item">
          <span class="timeline__version">v${ver}</span>
          <div class="timeline__links">
            <a href="${archivePath}" target="_blank" rel="noopener">View archived JSON ↗</a>
            <a href="${entry.github_ref}" target="_blank" rel="noopener">GitHub ↗</a>
          </div>
        </div>`;
      }
      if (archived.length === 0) {
        html += `<div style="font-size:0.8rem;color:var(--color-text-muted);padding:0.5rem 0">No previous versions archived yet.</div>`;
      }
      html += '</div>';
    }
    if (!html) html = '<div style="font-size:0.8rem;color:var(--color-text-muted);padding:0.5rem 0">No version history available.</div>';
    timeline.innerHTML = html;
    timeline.hidden = false;
  };

  // --- Navigation ---
  function navigate(id) {
    const found = findSubPillar(id);
    if (!found) return;
    renderPolicy(found.sub, found.pillar);
    // Update active state in sidebar
    sidebar.querySelectorAll('.sidebar__item').forEach(el => {
      el.classList.toggle('sidebar__item--active', el.dataset.id === id);
    });
    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('sidebar--open');
  }

  // --- Router ---
  function handleRoute() {
    const hash = location.hash;
    const match = hash.match(/^#sub\/(.+)$/);
    if (match) {
      navigate(decodeURIComponent(match[1]));
    } else {
      welcome.hidden = false;
      policyView.hidden = true;
    }
  }

  // --- Search ---
  function initSearch() {
    searchInput.addEventListener('input', () => {
      renderSidebar(appData.pillars, searchInput.value.trim());
    });
  }

  // --- Hamburger ---
  function initHamburger() {
    const btn = document.getElementById('hamburger');
    if (!btn) return;
    const sidebarEl = document.getElementById('sidebar');
    btn.addEventListener('click', () => sidebarEl.classList.toggle('sidebar--open'));
    document.addEventListener('click', e => {
      if (!sidebarEl.contains(e.target) && !btn.contains(e.target)) {
        sidebarEl.classList.remove('sidebar--open');
      }
    });
  }

  // --- Sidebar delegated click ---
  function initSidebarNav() {
    sidebar.addEventListener('click', e => {
      const item = e.target.closest('.sidebar__item');
      if (!item) return;
      // navigation happens via hashchange; just prevent default scroll
    });
  }

  // --- Init ---
  document.addEventListener('DOMContentLoaded', async () => {
    try {
      appData = await fetchData();
      initEnvBanner(appData.meta.env);
      renderSidebar(appData.pillars);
      initSearch();
      initSidebarNav();
      initHamburger();
      versionsData = await fetchVersions();
      window.addEventListener('hashchange', handleRoute);
      handleRoute();
    } catch (err) {
      const content = document.getElementById('content');
      if (content) content.innerHTML = `<div style="padding:2rem;color:red"><strong>Error loading data:</strong> ${err.message}</div>`;
    }
  });
})();
