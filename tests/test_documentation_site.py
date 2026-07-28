from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_main_documentation_site_builds(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(ROOT / "mkdocs.yml"),
            "--site-dir",
            str(site_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    assert (site_dir / "index.html").is_file()
    assert (site_dir / "installation/index.html").is_file()
    assert (site_dir / "example-site/index.html").is_file()
    assert (site_dir / "example-site/api-reference/index.html").is_file()
    assert (
        site_dir
        / "example-site/api-reference/pet/operation-put-update-pet/index.html"
    ).is_file()
    assert (site_dir / "example-site/models/pet/index.html").is_file()
    assert not (site_dir / "example-site/openapi/spec.json").exists()

    home = (site_dir / "index.html").read_text()
    assert "Overview" in home
    assert "Installation" in home
    assert "Example site" in home
    assert "Petstore API" in home
    assert "Models" in home

