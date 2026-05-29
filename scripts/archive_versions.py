#!/usr/bin/env python3
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from openpillar_utils import load_policy_registry, load_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    # Policies live in the public policy repo; link version history there.
    policy_repo = load_config(repo_root).get("repos", {}).get(
        "policy_repo", "https://github.com/amplutude/openpillar"
    )

    try:
        import boto3
        import botocore.exceptions
    except ImportError:
        print("boto3 not available, skipping version archiving", file=sys.stderr)
        sys.exit(0)

    try:
        s3 = boto3.client("s3", region_name=args.region)

        # Fetch existing manifest
        try:
            obj = s3.get_object(Bucket=args.bucket, Key="versions.json")
            previous = json.loads(obj["Body"].read())
        except s3.exceptions.NoSuchKey:
            previous = {"policies": {}}
        except Exception:
            previous = {"policies": {}}

        # Load newly built data
        dist_data_path = repo_root / "dist" / "data.json"
        if not dist_data_path.exists():
            print("dist/data.json not found, skipping archive", file=sys.stderr)
            sys.exit(0)

        with dist_data_path.open() as f:
            built = json.load(f)

        current_policies = built.get("policies", {})
        prev_policies = previous.get("policies", {})
        bumps = []
        now = datetime.now(timezone.utc).isoformat()

        for pol_id, pol in current_policies.items():
            new_ver = pol.get("version", "0.0.0")
            prev_entry = prev_policies.get(pol_id, {})
            old_ver = prev_entry.get("version") if isinstance(prev_entry, dict) else None

            if old_ver and old_ver != new_ver:
                # Archive the OLD policy content (fetch from live S3)
                archive_key = f"archive/{pol_id}/{old_ver}/policy.json"
                try:
                    old_obj = s3.get_object(Bucket=args.bucket, Key="data.json")
                    old_data = json.loads(old_obj["Body"].read())
                    old_pol = old_data.get("policies", {}).get(pol_id, {})
                    s3.put_object(
                        Bucket=args.bucket,
                        Key=archive_key,
                        Body=json.dumps(old_pol, indent=2).encode(),
                        ContentType="application/json",
                    )
                    print(f"Archived {pol_id} v{old_ver} → {archive_key}")
                    bumps.append({"id": pol_id, "old": old_ver, "new": new_ver})
                except Exception as e:
                    print(f"Warning: could not archive {pol_id}: {e}", file=sys.stderr)

        # Build updated manifest
        new_manifest = {"generated_at": now, "policies": {}}
        for pol_id, pol in current_policies.items():
            prev_entry = prev_policies.get(pol_id, {})
            archived = list(prev_entry.get("archived_versions", []))
            if isinstance(prev_entry, dict) and prev_entry.get("version") and prev_entry["version"] != pol.get("version"):
                archived.append(prev_entry["version"])
            new_manifest["policies"][pol_id] = {
                "version": pol.get("version", "0.0.0"),
                "name": pol.get("name", ""),
                "deployed_at": now,
                "archived_versions": archived,
                "github_ref": policy_repo,
            }

        # Write manifest locally and to S3
        local_manifest_path = repo_root / "dist" / "versions.json"
        with local_manifest_path.open("w") as f:
            json.dump(new_manifest, f, indent=2)
        s3.put_object(
            Bucket=args.bucket,
            Key="versions.json",
            Body=json.dumps(new_manifest, indent=2).encode(),
            ContentType="application/json",
        )

        if bumps:
            print("Version bumps detected:")
            for b in bumps:
                print(f"  {b['id']}: {b['old']} → {b['new']}")
        else:
            print("No version bumps detected.")

    except Exception as e:
        import traceback
        print(f"archive_versions warning: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
