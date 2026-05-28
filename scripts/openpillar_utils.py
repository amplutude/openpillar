from pathlib import Path
import yaml

def load_yaml(path):
    with path.open() as f:
        return yaml.safe_load(f) or {}

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
