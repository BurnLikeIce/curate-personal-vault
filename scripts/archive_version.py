"""Save a prepared personal work release in the vault, or verify a saved copy."""

import argparse
import hashlib
import json
import ntpath
from pathlib import Path, PureWindowsPath
import shutil
import sys
import tempfile


MANIFEST = "文件校验.json"


def portable_name(value):
    is_reserved = getattr(ntpath, "isreserved", None)
    reserved = is_reserved(value) if is_reserved else PureWindowsPath(value).is_reserved()
    bad = '<>:"/\\|?*'
    if (not value or value in (".", "..") or value.endswith((" ", "."))
            or any(c in bad or ord(c) < 32 for c in value)
            or reserved):
        raise ValueError(f"请使用可跨电脑保存的文件名：{value!r}")
    return value


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def verify(release):
    record = release / MANIFEST
    if record.is_symlink():
        raise ValueError("校验文件应为普通文件。")
    expected = json.loads(record.read_text(encoding="utf-8"))
    if not isinstance(expected, dict) or not expected:
        raise ValueError("作品校验清单为空或格式不符。")
    contents = {p.name for p in release.iterdir() if p.name != MANIFEST}
    if contents != set(expected):
        raise ValueError(f"版本文件列表与清单不符：{release}")
    for name, checksum in expected.items():
        item = release / portable_name(name)
        if item.is_symlink() or not item.is_file() or digest(item) != checksum:
            raise ValueError(f"文件校验不符：{item}")
    return expected


def reuse(release, expected):
    if release.is_symlink() or verify(release) != expected:
        raise ValueError(f"原版本内容不同，请核实并使用新版本号：{release}")
    print(f"复用已校验的版本 {release}")


def save(args):
    vault = args.vault.resolve()
    if not vault.is_dir():
        raise ValueError(f"知识库目录不存在：{vault}")
    works = vault / portable_name(args.works_dir)
    parent = works / portable_name(args.project)
    release = parent / portable_name(args.version)
    if any(part.resolve() != part for part in (works, parent, release)):
        raise ValueError("作品目录必须位于本知识库，使用普通目录。")
    sources = {}
    seen = {MANIFEST.casefold()}
    for source in args.files:
        name = portable_name(source.name)
        if name.casefold() in seen or not source.is_file():
            raise ValueError(f"文件缺失、重名或与清单名冲突：{source}")
        seen.add(name.casefold())
        sources[name] = source
    expected = {name: digest(source) for name, source in sources.items()}
    if release.exists():
        reuse(release, expected)
        return
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".待归档-", dir=parent) as folder:
        pending = Path(folder) / "内容"
        pending.resolve().relative_to(parent)
        pending.mkdir()
        for name, source in sources.items():
            shutil.copyfile(source, pending / name)
        (pending / MANIFEST).write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        verify(pending)
        try:
            pending.rename(release)
        except OSError:
            if not release.exists():
                raise
            reuse(release, expected)
            return
    print(f"已保存并校验 {release}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("save")
    add.add_argument("--project", required=True)
    add.add_argument("--version", required=True)
    add.add_argument("--vault", type=Path, required=True, help="已有的知识库目录")
    add.add_argument("--works-dir", default="作品", help="库根目录下的作品目录名")
    add.add_argument("files", type=Path, nargs="+")
    check = commands.add_parser("verify")
    check.add_argument("release", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "save":
            save(args)
        else:
            files = verify(args.release)
            print(f"校验通过，共 {len(files)} 个作品文件。")
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
