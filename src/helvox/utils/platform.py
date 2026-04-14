import platform
import sys
from pathlib import Path

from platformdirs import user_data_path


def app_font(size: int, *, bold: bool = False) -> tuple[str, int] | tuple[str, int, str]:
    system = platform.system()

    if system == "Windows":
        family = "Segoe UI"
    elif system == "Darwin":
        family = "Helvetica"
    else:
        family = "Arial"

    if bold:
        return (family, size, "bold")

    return (family, size)


def portable_base_dir() -> Path:
    """Directory next to the packaged executable / app bundle. In development: repo root."""
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve()
        if sys.platform == "darwin":
            p = exe
            while p != p.parent:
                if p.suffix == ".app":
                    parent = p.parent
                    # macOS App Translocation: when the app is opened directly
                    # from a DMG or quarantined location the OS runs it from a
                    # random read-only path under /private/var/folders/.
                    # Fall back to the user home dir so portable files land
                    # somewhere writable and consistent.
                    if str(parent).startswith("/private/var/folders/"):
                        return Path.home()
                    return parent
                p = p.parent
            # No .app bundle found; guard against translocation of plain binary.
            if str(exe).startswith("/private/var/folders/"):
                return Path.home()
        return exe.parent
    # Running from source: repository root (parent of src/)
    return Path(__file__).resolve().parents[3]


def recordings_dir() -> Path:
    """Fixed folder for recordings: `<portable_base>/helvox/`."""
    return portable_base_dir() / "helvox"


def default_recordings_dir() -> Path:
    """Deprecated name; use recordings_dir(). Kept for compatibility."""
    return recordings_dir()
