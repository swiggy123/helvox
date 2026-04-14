import os
import platform
import sys
import tempfile
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


def _in_temp_dir(path: Path) -> bool:
    """Return True if *path* is inside the system temporary directory."""
    try:
        tmp = Path(tempfile.gettempdir()).resolve()
        path.resolve().relative_to(tmp)
        return True
    except (ValueError, OSError):
        return False


def _best_exe_path() -> Path:
    """
    Return the path of the *original* executable, not a PyInstaller temp extract.

    PyInstaller --onefile (especially with console=False on Windows) may run the
    app's Python code from a child process whose sys.executable points inside the
    temp _MEIxxxxxx directory rather than the user-placed .exe/.app.
    sys.argv[0] reliably points to the original binary in all known configurations.
    """
    candidates: list[Path] = []

    # argv[0] is the most reliable source; resolve relative paths against cwd.
    if sys.argv and sys.argv[0]:
        a = Path(sys.argv[0])
        if not a.is_absolute():
            a = Path(os.getcwd()) / a
        candidates.append(a)

    candidates.append(Path(sys.executable))

    # Prefer the first candidate that is NOT in the system temp directory.
    for c in candidates:
        try:
            resolved = c.resolve()
            if not _in_temp_dir(resolved):
                return resolved
        except OSError:
            continue

    # Last resort: just use sys.executable even if it is in temp.
    return Path(sys.executable).resolve()


def portable_base_dir() -> Path:
    """Directory next to the packaged executable / app bundle. In development: repo root."""
    if getattr(sys, "frozen", False):
        exe = _best_exe_path()

        if sys.platform == "darwin":
            # Walk up from the binary to find the .app bundle.
            p = exe
            while p != p.parent:
                if p.suffix == ".app":
                    parent = p.parent
                    # macOS App Translocation: the OS runs the .app from a
                    # random read-only path under /private/var/folders/ when
                    # the app is opened directly from a DMG or quarantined
                    # location.  Fall back to home so files land somewhere
                    # writable and consistent.
                    if str(parent).startswith("/private/var/folders/"):
                        return Path.home()
                    return parent
                p = p.parent
            # No .app bundle — guard against a translocated plain binary.
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
