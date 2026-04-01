"""config.json lives either next to the app (helvox/) or in the OS user config dir."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_config_path

from helvox.utils.platform import portable_base_dir


def user_config_file() -> Path:
    return Path(user_config_path(appname="helvox", appauthor="noxenum")) / "config.json"


def portable_config_file() -> Path:
    return portable_base_dir() / "helvox" / "config.json"


def resolve_startup_settings_path() -> tuple[Path, bool | None]:
    """(path passed to load_settings, hint if JSON lacks config_portable)."""
    p, u = portable_config_file(), user_config_file()
    if p.exists():
        return p, True
    if u.exists():
        return u, False
    if u.with_suffix(".ini").exists() and not u.exists():
        return u, False
    if p.with_suffix(".ini").exists() and not p.exists():
        return p, True
    return u, None


def has_any_config_file() -> bool:
    p, u = portable_config_file(), user_config_file()
    return (
        p.exists()
        or u.exists()
        or p.with_suffix(".ini").exists()
        or u.with_suffix(".ini").exists()
    )


def prune_other_config(keep: Path) -> None:
    keep = keep.resolve()
    for c in (portable_config_file(), user_config_file()):
        if c.resolve() != keep and c.exists():
            try:
                c.unlink()
            except OSError:
                pass
