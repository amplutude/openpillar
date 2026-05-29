#!/usr/bin/env python3
import argparse, json, shutil, sys, urllib.request
from datetime import datetime, timezone
from html import escape as _escape
from pathlib import Path

import markdown as md_lib

sys.path.insert(0, str(Path(__file__).parent))
from openpillar_utils import load_yaml, load_markdown, load_policy_registry, load_config
from html_templates import (
    render_page, breadcrumb, jsonld_article, svg_logo, relative_root, esc
)

MD = md_lib.Markdown(extensions=["tables", "fenced_code", "toc"])


def md_to_html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def badge(status: str) -> str:
    # status is constrained to a known set; anything else falls back to "draft"
    css = {"active": "active", "draft": "draft", "retired": "retired", "deprecated": "deprecated"}.get(status, "draft")
    return f'<span class="badge badge--{css}">{esc(status or "unknown")}</span>'


def load_data(repo_root: Path) -> dict:
    policies = load_policy_registry(repo_root / "policies")
    pillars_root = repo_root / "pillars"
    pillars = []
    for pillar_dir in sorted(pillars_root.iterdir()):
        if not pillar_dir.is_dir():
            continue
        meta_path = pillar_dir / "metadata.yaml"
        if not meta_path.exists():
            continue
        pillar = load_yaml(meta_path)
        pillar["sub_pillars"] = []
        for sub_dir in sorted(pillar_dir.iterdir()):
            if not sub_dir.is_dir():
                continue
            sub_meta_path = sub_dir / "metadata.yaml"
            if not sub_meta_path.exists():
                continue
            sub = load_yaml(sub_meta_path)
            sub["policy_markdown"] = load_markdown(sub_dir / "policy.md") if (sub_dir / "policy.md").exists() else ""
            refs = sub.get("policy_refs") or []
            sub["resolved_policies"] = []
            for ref in refs:
                if ref in policies:
                    sub["resolved_policies"].append(policies[ref])
                else:
                    print(f"::warning::Unresolved policy_ref {ref} in {sub.get('id')}", file=sys.stderr)
            pillar["sub_pillars"].append(sub)
        pillars.append(pillar)
    return {"policies": policies, "pillars": pillars}


def pillar_url_id(pillar_id: str) -> str:
    return pillar_id.replace("/", "-")


def build_homepage(data: dict, config: dict, dist: Path, env: str) -> None:
    base_url = config["site"]["base_url"]
    canonical = f"{base_url}/"
    policy_repo = config["repos"]["policy_repo"]

    standards_html = "".join(
        f'<a class="standards-bar__item" href="{esc(s["url"])}" target="_blank" rel="noopener" title="{esc(s["description"])}">{esc(s["name"])}</a>'
        for s in config.get("standards", [])
    )

    pillar_cards = ""
    for p in data["pillars"]:
        pid = p["id"]
        sub_count = len(p["sub_pillars"])
        href = f"pillars/{esc(pid)}/index.html"
        pillar_cards += f"""
        <a class="pillar-card" href="{href}">
          <div class="pillar-card__id">{esc(pid)}</div>
          <div class="pillar-card__title">{esc(p["name"])}</div>
          <div class="pillar-card__desc">{esc(p.get("description", ""))}</div>
          <div class="pillar-card__footer">
            <span class="pillar-card__count">{sub_count} control{"s" if sub_count != 1 else ""}</span>
            {badge(p.get("status", "active"))}
          </div>
        </a>"""

    env_banner = ""
    if env == "test":
        env_banner = '<div id="env-banner">⚠ TEST ENVIRONMENT — This site reflects test policy content, not production.</div>'

    body = f"""
{env_banner}
<section class="hero">
  <div class="hero__logo">{svg_logo().replace('width="32" height="32"', 'width="56" height="56"')}</div>
  <h1 class="hero__title">{esc(config["site"]["name"])}</h1>
  <p class="hero__tagline">{esc(config["site"]["tagline"])}</p>
  <p class="hero__description">{esc(config["site"]["description"])}</p>
  <div class="standards-bar" aria-label="Aligned standards">
    {standards_html}
  </div>
  <a class="btn btn--primary hero__cta" href="{esc(policy_repo)}" target="_blank" rel="noopener">Contribute on GitHub</a>
</section>

<section id="pillars" class="pillars-section">
  <h2 class="section-title">Governance Pillars</h2>
  <p class="section-subtitle">Each pillar groups related technology controls. Click a pillar to explore its controls and referenced policies.</p>
  <div class="pillars-grid">
    {pillar_cards}
  </div>
</section>
"""
    html = render_page(
        title=config["site"]["name"],
        description=config["site"]["description"],
        canonical=canonical,
        body_html=body,
        config=config,
    )
    (dist / "index.html").write_text(html, encoding="utf-8")


def build_pillar_page(pillar: dict, config: dict, dist: Path) -> None:
    base_url = config["site"]["base_url"]
    pid = pillar["id"]
    out_dir = dist / "pillars" / pid
    out_dir.mkdir(parents=True, exist_ok=True)
    canonical = f"{base_url}/pillars/{pid}/"
    root = relative_root(canonical, base_url)

    sub_cards = ""
    for sub in pillar["sub_pillars"]:
        sid = sub["id"]
        ref_badges = "".join(
            f'<span class="tag">{esc(ref)}</span>'
            for ref in (sub.get("policy_refs") or [])
        )
        sub_cards += f"""
        <a class="pillar-card" href="{esc(sid)}/index.html">
          <div class="pillar-card__id">{esc(sid)}</div>
          <div class="pillar-card__title">{esc(sub["name"])}</div>
          <div class="pillar-card__desc">{esc(sub.get("description", ""))}</div>
          <div class="pillar-card__footer">
            <div>{ref_badges}</div>
            {badge(sub.get("status", "active"))}
          </div>
        </a>"""

    meta_html = ""
    for label, key in [("Owner", "owner"), ("Effective", "effective_date"), ("Review", "review_date"), ("Version", "version")]:
        if pillar.get(key):
            meta_html += f'<div class="policy-meta__item"><span>{label}</span><span class="policy-meta__value">{esc(pillar[key])}</span></div>'

    body = f"""
<article>
  <header class="policy-header">
    <div class="policy-header__id">{esc(pid)}</div>
    <h1 class="policy-header__name">{esc(pillar["name"])}</h1>
    <div class="policy-meta">{meta_html}{badge(pillar.get("status","active"))}</div>
    <p style="color:var(--color-text-muted);margin-top:0.75rem;line-height:1.7">{esc(pillar.get("description",""))}</p>
  </header>

  <section id="controls" style="margin-top:2.5rem">
    <h2 class="section-title" style="font-size:1.2rem">Controls</h2>
    <div class="pillars-grid">{sub_cards}</div>
  </section>
</article>
"""
    html = render_page(
        title=pillar["name"],
        description=pillar.get("description", f"Controls under {pillar['name']} — {config['site']['name']}"),
        canonical=canonical,
        body_html=body,
        config=config,
        breadcrumbs=[("Home", f"{root}index.html"), (pillar["name"], canonical)],
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def build_sub_pillar_page(sub: dict, pillar: dict, config: dict, dist: Path) -> None:
    base_url = config["site"]["base_url"]
    policy_repo = config["repos"]["policy_repo"]
    pid = pillar["id"]
    sid = sub["id"]
    out_dir = dist / "pillars" / pid / sid
    out_dir.mkdir(parents=True, exist_ok=True)
    canonical = f"{base_url}/pillars/{pid}/{sid}/"
    root = relative_root(canonical, base_url)

    # Compute folder path hint for edit link
    # e.g. P-001-001 → pillars/001/001
    parts = sid.replace("P-", "").split("-")
    folder_hint = "pillars/" + "/".join(f"{p.zfill(3)}" for p in parts)
    edit_url = f"{policy_repo}/edit/main/{folder_hint}/policy.md"
    view_url = f"{policy_repo}/tree/main/{folder_hint}"

    meta_html = ""
    for label, key in [("Owner", "owner"), ("Effective", "effective_date"), ("Review", "review_date"), ("Version", "version")]:
        if sub.get(key):
            meta_html += f'<div class="policy-meta__item"><span>{label}</span><span class="policy-meta__value">{esc(sub[key])}</span></div>'

    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in (sub.get("tags") or []))

    body_md = md_to_html(sub.get("policy_markdown") or "")

    refs_html = ""
    for pol in (sub.get("resolved_policies") or []):
        pol_md = md_to_html(pol.get("policy_markdown") or "")
        pol_meta = ""
        for label, key in [("Owner", "owner"), ("Effective", "effective_date"), ("Version", "version")]:
            if pol.get(key):
                pol_meta += f'<div class="policy-meta__item"><span>{label}</span><span class="policy-meta__value">{esc(pol[key])}</span></div>'
        refs_html += f"""
<div class="policy-card" data-policy-id="{esc(pol["id"])}">
  <div class="policy-card__header">
    <div class="policy-card__title">
      <span class="badge badge--active" style="font-size:0.65rem">{esc(pol["id"])}</span>
      {esc(pol["name"])}
    </div>
    <div style="display:flex;gap:0.75rem;align-items:center">
      {badge(pol.get("status","active"))}
      <span style="font-size:0.8rem;color:var(--color-text-muted)">v{esc(pol.get("version",""))}</span>
      <span class="policy-card__toggle" aria-hidden="true">▾</span>
    </div>
  </div>
  <div class="policy-card__body">
    <div class="policy-meta" style="margin-bottom:1rem">{pol_meta}</div>
    <div class="policy-content">{pol_md}</div>
  </div>
</div>"""

    jld = jsonld_article(
        name=sub["name"],
        description=sub.get("description", f"{sub['name']} — {config['site']['name']}"),
        url=canonical,
        date_published=sub.get("effective_date", ""),
        date_modified=sub.get("review_date", ""),
    )

    body = f"""
<article data-page="sub-pillar">
  <header class="policy-header">
    <div class="policy-header__id">{esc(pillar["name"])} / {esc(sid)}</div>
    <h1 class="policy-header__name">{esc(sub["name"])}</h1>
    <div class="policy-meta">{meta_html}{badge(sub.get("status","active"))}</div>
    {f'<div style="margin-top:0.5rem">{tags_html}</div>' if tags_html else ""}
    <div class="policy-actions">
      <a class="btn btn--ghost" href="{esc(edit_url)}" target="_blank" rel="noopener">✏ Edit on GitHub</a>
      <a class="btn btn--ghost" href="{esc(view_url)}" target="_blank" rel="noopener">⎆ View on GitHub</a>
    </div>
  </header>

  <div class="policy-content" style="margin-top:1.75rem">{body_md}</div>

  {f'<section class="policy-refs"><h2 style="font-size:1.1rem;margin-top:2.5rem;margin-bottom:1rem">Referenced Policies</h2>{refs_html}</section>' if refs_html else ""}

  <div class="version-history" id="version-history">
    <button class="version-history__toggle" data-policy-ids="{esc(",".join(p["id"] for p in sub.get("resolved_policies",[])))}" onclick="toggleVersionHistory(this)">
      📋 Version History
    </button>
    <div class="timeline" id="version-timeline" hidden></div>
  </div>
</article>
"""
    html = render_page(
        title=sub["name"],
        description=sub.get("description", f"{sub['name']} — {config['site']['name']}"),
        canonical=canonical,
        body_html=body,
        config=config,
        breadcrumbs=[
            ("Home", f"{root}index.html"),
            (pillar["name"], f"{root}pillars/{pid}/index.html"),
            (sub["name"], canonical),
        ],
        edit_url=edit_url,
        jsonld=jld,
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def build_sitemap(data: dict, config: dict, dist: Path) -> None:
    base_url = config["site"]["base_url"]
    # Clean directory-form URLs, matching the <link rel="canonical"> on each page.
    urls = [f"{base_url}/"]
    for pillar in data["pillars"]:
        pid = pillar["id"]
        urls.append(f"{base_url}/pillars/{pid}/")
        for sub in pillar["sub_pillars"]:
            urls.append(f"{base_url}/pillars/{pid}/{sub['id']}/")

    url_els = "\n".join(
        f"  <url><loc>{esc(u)}</loc><changefreq>weekly</changefreq></url>"
        for u in urls
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_els}
</urlset>"""
    (dist / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def build_robots(config: dict, dist: Path) -> None:
    base_url = config["site"]["base_url"]
    (dist / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n",
        encoding="utf-8",
    )


def download_marked(dest: Path) -> None:
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = "https://cdn.jsdelivr.net/npm/marked/marked.min.js"
    with urllib.request.urlopen(url) as resp:
        dest.write_bytes(resp.read())
    print(f"Downloaded marked.min.js → {dest}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["test", "production"], default="production")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    dist = repo_root / "dist"
    dist.mkdir(parents=True, exist_ok=True)

    config = load_config(repo_root)
    data = load_data(repo_root)

    # Copy static assets (css, js)
    shutil.copytree(repo_root / "src", dist, dirs_exist_ok=True)
    download_marked(dist / "js" / "marked.min.js")

    # Generate pages
    build_homepage(data, config, dist, args.env)
    for pillar in data["pillars"]:
        build_pillar_page(pillar, config, dist)
        for sub in pillar["sub_pillars"]:
            build_sub_pillar_page(sub, pillar, config, dist)

    build_sitemap(data, config, dist)
    build_robots(config, dist)

    # Also emit data.json for any headless consumers
    meta = {
        "env": args.env,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "pillar_count": len(data["pillars"]),
        "sub_pillar_count": sum(len(p["sub_pillars"]) for p in data["pillars"]),
    }
    with (dist / "data.json").open("w") as f:
        json.dump({"meta": meta, **data}, f, indent=2, default=str)

    print(
        f"Built: {meta['pillar_count']} pillars, {meta['sub_pillar_count']} sub-pillars, "
        f"{len(data['policies'])} policies → {dist}"
    )


if __name__ == "__main__":
    main()
