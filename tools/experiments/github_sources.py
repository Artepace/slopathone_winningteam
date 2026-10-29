"""Discover and download public GitHub solution archives without executing them."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

DEFAULT_REPO = "Artepace/slopathone_winningteam"
MAX_ARCHIVE = 50 * 1024 * 1024
MAX_JSON = 16 * 1024 * 1024


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def fetch(url, limit):
    request = Request(url, headers={"User-Agent": "career-experiment-lab/1", "Accept": "application/vnd.github+json"})
    try:
        with urlopen(request, timeout=45) as response:
            payload = response.read(limit + 1)
    except HTTPError as error:
        if error.code in (403, 429):
            raise ValueError("GitHub rejected the request or its public API limit was reached; retry later.") from error
        raise ValueError(f"GitHub HTTP {error.code}; check repository and ref.") from error
    if len(payload) > limit:
        raise ValueError("GitHub response exceeds the configured size limit.")
    return payload


def fetch_json(url):
    return json.loads(fetch(url, MAX_JSON))


def validate_repo(repo):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Repository must be owner/repository.")
    return repo


def solution_entries(tree):
    if tree.get("truncated"):
        raise ValueError("GitHub returned an incomplete tree; discovery cannot claim to be complete.")
    results = []
    for entry in tree.get("tree", []):
        name = entry.get("path", "")
        parts = PurePosixPath(name).parts
        if entry.get("type") != "blob" or not name.lower().endswith(".zip") or "solution" not in PurePosixPath(name).name.lower():
            continue
        if name.startswith("/") or ".." in parts or "\\" in name or not re.fullmatch(r"[0-9a-f]{40}", entry.get("sha", "")):
            raise ValueError("Unsafe archive entry in GitHub tree.")
        if entry.get("size", 0) > MAX_ARCHIVE:
            continue
        results.append(entry)
    return sorted(results, key=lambda item: item["path"])


def blob_sha(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


@lru_cache(maxsize=1)
def inspection_helpers():
    """Load trusted sibling helpers, never a Python file from a solution archive."""
    spec = importlib.util.spec_from_file_location("_career_archive_inspection", Path(__file__).with_name("controller.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def archive_fingerprints(payload, inbox):
    """Safely inspect ZIP data; exclude documents from the gameplay fingerprint."""
    helpers = inspection_helpers()
    try:
        with tempfile.TemporaryDirectory(prefix="inspect-", dir=inbox) as temporary:
            temporary = Path(temporary)
            archive = temporary / "input.zip"
            archive.write_bytes(payload)
            extracted = temporary / "extracted"
            extracted.mkdir()
            helpers.extract_archive(archive, extracted)
            root = helpers.find_submission_root(extracted)
            helpers.validate_basic(root)
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8-sig"))
            canonical = json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
            digest = hashlib.sha256(b"manifest.json\0" + hashlib.sha256(canonical).digest())
            for item in sorted((root / "skills").rglob("*"), key=lambda item: item.relative_to(root).parts):
                if item.is_file():
                    digest.update(item.relative_to(root).as_posix().encode("utf-8") + b"\0")
                    digest.update(bytes.fromhex(helpers.file_digest(item)))
            return {"gameplay_sha256": digest.hexdigest(), "content_sha256": helpers.submission_digest(root)}
    except helpers.ControllerError as error:
        raise ValueError(f"Downloaded solution archive failed safe inspection: {error}") from error


def check(repo, ref, inbox, download=False):
    repo = validate_repo(repo)
    inbox = Path(inbox).resolve()
    inbox.mkdir(parents=True, exist_ok=True)
    index_path = inbox / "github-index.json"
    previous = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"seen": {}, "downloads": {}}
    base = f"https://api.github.com/repos/{repo}"
    if not ref:
        ref = fetch_json(base)["default_branch"]
    commit_info = fetch_json(base + "/commits/" + quote(ref, safe=""))
    commit = commit_info["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Invalid GitHub commit identifier.")
    tree = fetch_json(base + "/git/trees/" + commit + "?recursive=1")
    archives = []
    for entry in solution_entries(tree):
        path, blob = entry["path"], entry["sha"]
        key = f"{repo}:{path}:{blob}"
        item = {"path": path, "blob_sha": blob, "size": entry.get("size"), "is_new": key not in previous["seen"],
                "source_url": f"https://github.com/{repo}/blob/{commit}/{quote(path, safe='/')}", "commit": commit}
        existing = previous["downloads"].get(key)
        if existing:
            local = inbox / existing["filename"]
            if local.is_file() and hashlib.sha256(local.read_bytes()).hexdigest() == existing["sha256"]:
                item.update({"local_path": str(local), "sha256": existing["sha256"]})
                if "gameplay_sha256" not in existing:
                    existing.update(archive_fingerprints(local.read_bytes(), inbox))
                item.update({field: existing[field] for field in ("gameplay_sha256", "content_sha256") if field in existing})
        if download and "local_path" not in item:
            data = fetch(f"https://raw.githubusercontent.com/{repo}/{commit}/{quote(path, safe='/')}", MAX_ARCHIVE)
            if blob_sha(data) != blob:
                raise ValueError(f"Downloaded archive does not match GitHub blob: {path}")
            fingerprints = archive_fingerprints(data, inbox)
            digest = hashlib.sha256(data).hexdigest()
            stem = re.sub(r"[^A-Za-z0-9_-]", "-", PurePosixPath(path).stem)[:64] or "solution"
            filename = f"archive-{stem}-{blob[:12]}.zip"
            local = inbox / filename
            if local.exists() and hashlib.sha256(local.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Refusing to overwrite different local content: {filename}")
            if not local.exists():
                with local.open("xb") as handle:
                    handle.write(data)
            item.update({"local_path": str(local), "sha256": digest, **fingerprints})
            previous["downloads"][key] = {"filename": filename, "sha256": digest, "commit": commit, "path": path,
                                          "repository": repo, "source_url": item["source_url"], **fingerprints}
        previous["seen"].setdefault(key, utc_now())
        archives.append(item)
    for item in archives:
        digest = item.get("gameplay_sha256")
        item_key = f"{repo}:{item['path']}:{item['blob_sha']}"
        item["gameplay_duplicate_of"] = [
            {"repository": record.get("repository", known_key.split(":", 1)[0]),
             "path": record["path"], "commit": record["commit"], "sha256": record["sha256"],
             "source_url": record.get("source_url") or
                 f"https://github.com/{known_key.split(':', 1)[0]}/blob/{record['commit']}/{quote(record['path'], safe='/')}"}
            for known_key, record in previous["downloads"].items()
            if digest and known_key != item_key and record.get("gameplay_sha256") == digest
        ]
    result = {"repository": repo, "ref": ref, "commit": commit,
              "committed_at": commit_info["commit"]["committer"]["date"], "checked_at": utc_now(), "archives": archives}
    previous["latest_check"] = result
    temporary = index_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(previous, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(index_path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="")
    parser.add_argument("--inbox", type=Path, default=Path(__file__).resolve().parent / "inbox")
    parser.add_argument("--download", action="store_true", help="Download verified ZIPs; never execute or install them.")
    args = parser.parse_args()
    try:
        result = check(args.repo, args.ref, args.inbox, args.download)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
