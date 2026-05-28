"""HTML template helpers for OpenPillar static site generation."""
from urllib.parse import urlparse


def svg_logo() -> str:
    """Returns inline SVG for the OpenPillar logo."""
    return '''<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <polygon points="16,2 28,9 28,23 16,30 4,23 4,9" stroke="#3b82f6" stroke-width="2" fill="none"/>
  <rect x="14" y="8" width="4" height="16" rx="1" fill="#3b82f6"/>
</svg>'''


def relative_root(canonical: str, base_url: str) -> str:
    """Compute relative path prefix for CSS/JS based on URL depth."""
    path = canonical.replace(base_url, "").lstrip("/")
    depth = path.count("/") if path else 0
    if depth == 0:
        return ""
    return "../" * depth


def head_meta(title: str, description: str, canonical: str, config: dict) -> str:
    """Returns <head> contents with full SEO meta tags."""
    site_name = config["site"]["name"]
    base_url = config["site"]["base_url"]
    og_image = f"{base_url}/og-image.png"
    root = relative_root(canonical, base_url)
    return f"""  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | {site_name}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="{site_name}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <link rel="stylesheet" href="{root}css/styles.css">"""


def topnav(config: dict, canonical: str, edit_url: str = None) -> str:
    """Returns the top navigation bar HTML."""
    policy_repo = config["repos"]["policy_repo"]
    root = relative_root(canonical, config["site"]["base_url"])
    logo_svg = svg_logo().replace('width="32" height="32"', 'width="28" height="28" class="topnav__logo-svg"')
    return f"""<nav class="topnav" role="navigation" aria-label="Main navigation">
  <a class="topnav__brand" href="{root}index.html">
    {logo_svg}
    <span class="topnav__title">{config["site"]["logo_text"]}</span>
    <span class="topnav__env" id="env-badge"></span>
  </a>
  <div class="topnav__nav">
    <a href="{root}index.html">Home</a>
    <a href="{root}index.html#pillars">Pillars</a>
    <a href="{policy_repo}" target="_blank" rel="noopener">GitHub</a>
  </div>
  <div class="topnav__search">
    <input id="search" type="search" placeholder="Search policies…" aria-label="Search">
  </div>
  <a class="topnav__cta btn btn--ghost" href="{policy_repo}" target="_blank" rel="noopener">Contribute</a>
  <button class="topnav__hamburger" id="hamburger" aria-label="Toggle navigation">&#9776;</button>
</nav>"""


def footer_html(config: dict) -> str:
    """Returns footer HTML."""
    links = config.get("footer", {}).get("links", [])
    copyright_text = config.get("footer", {}).get("copyright", "")
    standards = config.get("standards", [])

    links_html = "\n".join(
        f'        <li><a href="{link["url"]}" target="_blank" rel="noopener">{link["label"]}</a></li>'
        for link in links
    )
    standards_html = "\n".join(
        f'        <li><a href="{s["url"]}" target="_blank" rel="noopener">{s["name"]}</a></li>'
        for s in standards
    )
    logo_svg = svg_logo()
    return f"""<footer class="site-footer" role="contentinfo">
  <div class="site-footer__grid">
    <div class="site-footer__brand">
      {logo_svg}
      <div>
        <div style="font-weight:700;font-size:1.1rem;color:#fff;margin-bottom:0.5rem">{config["site"]["logo_text"]}</div>
        <div style="font-size:0.85rem;color:#94a3b8;line-height:1.6">{config["site"]["description"]}</div>
      </div>
    </div>
    <div>
      <div class="site-footer__heading">Links</div>
      <ul class="site-footer__links">
{links_html}
      </ul>
    </div>
    <div>
      <div class="site-footer__heading">Standards</div>
      <ul class="site-footer__links">
{standards_html}
      </ul>
    </div>
  </div>
  <div class="site-footer__bottom">
    <span>&copy; {copyright_text}</span>
    <span>Built with OpenPillar</span>
  </div>
</footer>"""


def breadcrumb(crumbs: list) -> str:
    """crumbs = [(label, url), ...], last item has no link."""
    parts = []
    for i, (label, url) in enumerate(crumbs):
        if i < len(crumbs) - 1:
            parts.append(f'<a href="{url}">{label}</a>')
            parts.append('<span class="breadcrumb__sep" aria-hidden="true">/</span>')
        else:
            parts.append(f'<span aria-current="page">{label}</span>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def jsonld_article(name: str, description: str, url: str, date_published: str, date_modified: str) -> str:
    """Returns JSON-LD <script> block for Article structured data."""
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "name": name,
        "description": description,
        "url": url,
        "datePublished": str(date_published) if date_published else "",
        "dateModified": str(date_modified) if date_modified else "",
    }
    return f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>'


def render_page(title: str, description: str, canonical: str, body_html: str,
                config: dict, breadcrumbs: list = None, edit_url: str = None, jsonld: str = None) -> str:
    """Full page render."""
    head = head_meta(title, description, canonical, config)
    nav = topnav(config, canonical, edit_url)
    foot = footer_html(config)
    crumb_html = breadcrumb(breadcrumbs) if breadcrumbs else ""
    jsonld_block = jsonld if jsonld else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head}
</head>
<body>
{nav}
<main class="main-content" id="main-content">
  {crumb_html}
  {body_html}
</main>
{foot}
{jsonld_block}
<script src="{relative_root(canonical, config["site"]["base_url"])}js/app.js" defer></script>
</body>
</html>"""
