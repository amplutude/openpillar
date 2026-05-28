from pathlib import Path
import yaml

def load_yaml(path):
    with path.open() as f:
        return yaml.safe_load(f) or {}

def load_config(repo_root: Path) -> dict:
    """Load config.yaml from repo root and resolve template references."""
    config_path = repo_root / "config.yaml"
    config = load_yaml(config_path)
    # Resolve {{ repos.policy_repo }} and {{ repos.app_repo }} in footer links
    policy_repo = config.get("repos", {}).get("policy_repo", "")
    app_repo = config.get("repos", {}).get("app_repo", "")
    for link in config.get("footer", {}).get("links", []):
        url = link.get("url", "")
        url = url.replace("{{ repos.policy_repo }}", policy_repo)
        url = url.replace("{{ repos.app_repo }}", app_repo)
        link["url"] = url
    return config

def load_markdown(path):
    with path.open() as f:
        return f.read()

def load_policy_registry(policies_root: Path) -> dict:
    """Walk policies/ and return {policy_id: {**meta, policy_markdown: str}}"""
    registry = {}
    if not policies_root.exists():
        return registry
    for d in sorted(policies_root.iterdir()):
        if not d.is_dir():
            continue
        meta_path = d / "metadata.yaml"
        if not meta_path.exists():
            continue
        meta = load_yaml(meta_path)
        policy_path = d / "policy.md"
        meta["policy_markdown"] = load_markdown(policy_path) if policy_path.exists() else ""
        registry[meta["id"]] = meta
    return registry
