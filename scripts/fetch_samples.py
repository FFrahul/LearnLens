"""Download only manifest items explicitly marked for openly licensed reuse."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "samples" / "manifest.json"
SAMPLES = ROOT / "samples"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    downloaded = []
    for item in manifest.get("files", []):
        if item.get("download_url") and item.get("license", "").upper().startswith("CC"):
            destination = SAMPLES / item["target_folder"] / item["filename"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(item["download_url"], destination)
            if item.get("sha256") and sha256(destination) != item["sha256"]:
                destination.unlink()
                raise RuntimeError(f"Checksum mismatch: {item['filename']}")
            downloaded.append(str(destination.relative_to(ROOT)))
    print(json.dumps({"downloaded": downloaded}))


if __name__ == "__main__":
    main()
