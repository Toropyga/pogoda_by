"""Create a distributable archive without caches or development environments."""

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--output", type=Path, required=True)
    args = arguments.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(
            part in {"__pycache__", ".git", ".venv", ".pytest_cache", ".ruff_cache"}
            for part in path.relative_to(root).parts
        ) and path.suffix not in {".pyc", ".zip"}
    )
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive checksum check failed")
        if "custom_components/pogoda_by/manifest.json" not in archive.namelist():
            raise ValueError("Missing installable integration")
    print(f"Created {output} ({len(files)} files, {output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
