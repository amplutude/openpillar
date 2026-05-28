#!/usr/bin/env python3
import argparse, json, shutil, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from openpillar_utils import load_yaml, load_markdown, load_policy_registry

def build(repo_root: Path, env: str) -> dict:
    policies = load_policy_registry(repo_root / "policies")
    pillars_root = repo_root / "pillars"
    data = {"meta": {"env": env, "built_at": datetime.now(timezone.utc).isoformat(), "pillar_count": 0, "sub_pillar_count": 0}, "policies": policies, "pillars": []}

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
        data["pillars"].append(pillar)

    data["meta"]["pillar_count"] = len(data["pillars"])
    data["meta"]["sub_pillar_count"] = sum(len(p["sub_pillars"]) for p in data["pillars"])
    return data

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
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    data = build(repo_root, args.env)
    out = dist_dir / "data.json"
    with out.open("w") as f:
        json.dump(data, f, indent=2, default=str)

    shutil.copytree(repo_root / "src", dist_dir, dirs_exist_ok=True)
    download_marked(dist_dir / "js" / "marked.min.js")
    print(f"Built: {data['meta']['pillar_count']} pillars, {data['meta']['sub_pillar_count']} sub-pillars, {len(data['policies'])} policies → {out}")

if __name__ == "__main__":
    main()
