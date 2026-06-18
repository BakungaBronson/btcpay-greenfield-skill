"""
tunnel.py — cross-platform: expose your local webhook server on a public HTTPS
URL so BTCPay can reach it.

BTCPay delivers webhooks by POSTing to a URL it can reach over HTTPS. While
developing on your own machine you don't have one, so you run a tunnel. This
script makes that turnkey on Windows / macOS / Linux WITHOUT assuming the user
already has ngrok:

  1. Find ngrok (on PATH, or a local copy this script cached earlier).
  2. If it's missing, download the official binary for THIS OS + CPU into
     scripts/.tools/ — no admin rights, no package manager required.
  3. Check that an ngrok authtoken is configured (ngrok needs a free one, once).
  4. Start `ngrok http <port>` and print the public https URL to register:
        client.create_webhook(url=PUBLIC_URL + "/btcpay-webhook", secret=...)

Usage:
  python tunnel.py 8080            # install if needed, then open a tunnel to :8080
  python tunnel.py --check         # only report install/auth status, don't tunnel

Stdlib only — no pip install needed for this script itself.
"""

from __future__ import annotations

import io
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

# Official ngrok v3 stable download channel (verified for all 5 OS/arch combos).
NGROK_BASE = "https://bin.equinox.io/c/bNyj1mQVY4c"
TOOLS_DIR = Path(__file__).resolve().parent / ".tools"
NGROK_API = "http://127.0.0.1:4040/api/tunnels"


def _platform_slug() -> tuple[str, str]:
    """Return (ngrok-os, ngrok-arch) for this machine, or raise if unsupported."""
    sysname = sys.platform
    os_map = {"darwin": "darwin", "linux": "linux", "win32": "windows"}
    if sysname not in os_map:
        raise RuntimeError(f"Unsupported OS for auto-install: {sysname!r}. "
                           f"Install ngrok manually: https://ngrok.com/download")
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        arch = "arm64"
    elif machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("i386", "i686", "x86"):
        arch = "386"
    else:
        # Best effort: most desktops are amd64.
        arch = "amd64"
    return os_map[sysname], arch


def _ngrok_binary_name() -> str:
    return "ngrok.exe" if sys.platform == "win32" else "ngrok"


def find_ngrok() -> Optional[str]:
    """Locate ngrok: a system install (PATH) first, then our local cache."""
    on_path = shutil.which("ngrok")
    if on_path:
        return on_path
    cached = TOOLS_DIR / _ngrok_binary_name()
    if cached.exists():
        return str(cached)
    return None


def install_ngrok() -> str:
    """Download the official ngrok binary for this OS/arch into scripts/.tools/.

    No admin rights and no package manager needed — works the same everywhere.
    (If you'd rather use a package manager: `brew install ngrok` on macOS,
    `choco install ngrok` / `winget install ngrok.ngrok` on Windows,
    `snap install ngrok` on Linux.)
    """
    os_name, arch = _platform_slug()
    ext = "zip" if os_name in ("windows", "darwin") else "tgz"
    url = f"{NGROK_BASE}/ngrok-v3-stable-{os_name}-{arch}.{ext}"
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"ngrok not found — downloading the official build for "
          f"{os_name}/{arch} (~12 MB, one time)...\n  {url}")

    with urllib.request.urlopen(url, timeout=120) as resp:
        blob = resp.read()

    binary_name = _ngrok_binary_name()
    if ext == "zip":
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            member = next(n for n in zf.namelist() if n.endswith(binary_name))
            with zf.open(member) as src, open(TOOLS_DIR / binary_name, "wb") as dst:
                shutil.copyfileobj(src, dst)
    else:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            member = next(m for m in tf.getmembers() if m.name.endswith(binary_name))
            src = tf.extractfile(member)
            with open(TOOLS_DIR / binary_name, "wb") as dst:
                shutil.copyfileobj(src, dst)

    path = TOOLS_DIR / binary_name
    if sys.platform != "win32":
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Installed ngrok -> {path}")
    return str(path)


def ensure_ngrok() -> str:
    """Return a usable ngrok path, installing it locally if necessary."""
    return find_ngrok() or install_ngrok()


def _config_paths() -> list[Path]:
    home = Path.home()
    return [
        home / "Library/Application Support/ngrok/ngrok.yml",   # macOS
        home / ".config/ngrok/ngrok.yml",                        # Linux/XDG
        Path(os.environ.get("LOCALAPPDATA", home)) / "ngrok/ngrok.yml",  # Windows
        home / ".ngrok2/ngrok.yml",                              # legacy
    ]


def has_authtoken() -> bool:
    """True if an ngrok authtoken is available (env var or config file)."""
    if os.environ.get("NGROK_AUTHTOKEN"):
        return True
    for p in _config_paths():
        try:
            if p.exists() and "authtoken" in p.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def print_authtoken_help() -> None:
    print(
        "\nngrok needs a free authtoken (one-time setup):\n"
        "  1. Sign up:    https://dashboard.ngrok.com/signup\n"
        "  2. Copy token: https://dashboard.ngrok.com/get-started/your-authtoken\n"
        "  3. Register:   ngrok config add-authtoken <YOUR_TOKEN>\n"
        "     (or export NGROK_AUTHTOKEN=<YOUR_TOKEN> before running this)\n"
    )


def start_tunnel(port: int, ngrok_path: Optional[str] = None,
                 wait_s: int = 20) -> tuple[str, subprocess.Popen]:
    """Start `ngrok http <port>` and return (public_https_url, process).

    The caller is responsible for keeping the process alive (the tunnel dies
    with it) and terminating it when done.
    """
    ngrok_path = ngrok_path or ensure_ngrok()
    proc = subprocess.Popen(
        [ngrok_path, "http", str(port), "--log=stdout"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + wait_s
    last_err = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(NGROK_API, timeout=2) as r:
                data = json.load(r)
            tunnels = data.get("tunnels", [])
            https = [t for t in tunnels if t.get("public_url", "").startswith("https")]
            if https:
                return https[0]["public_url"], proc
        except Exception as e:  # API not up yet
            last_err = e
        time.sleep(0.5)
    proc.terminate()
    raise RuntimeError(f"Tunnel did not come up within {wait_s}s. "
                       f"Last error: {last_err}. Is the authtoken set?")


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    args = [a for a in argv if not a.startswith("-")]
    port = int(args[0]) if args else int(os.environ.get("PORT", "8080"))

    ngrok_path = ensure_ngrok()
    print(f"ngrok: {ngrok_path}")
    authed = has_authtoken()
    print(f"authtoken configured: {authed}")
    if not authed:
        print_authtoken_help()
        if not check_only:
            return 1
    if check_only:
        return 0

    print(f"Opening tunnel to http://localhost:{port} ...")
    url, proc = start_tunnel(port, ngrok_path)
    print("\n" + "=" * 60)
    print(f"PUBLIC URL:  {url}")
    print(f"Register it:  client.create_webhook(url=\"{url}/btcpay-webhook\", secret=...)")
    print(f"Inspect deliveries at http://127.0.0.1:4040")
    print("=" * 60 + "\nCtrl-C to stop the tunnel.")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\nTunnel stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
