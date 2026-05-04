# SPDX-FileCopyrightText: 2025 ETH Zurich and University of Bologna
#
# SPDX-License-Identifier: Apache-2.0

import os
import shlex
import subprocess
import sys
from pathlib import Path

__all__ = ["bootstrap_gap9_env"]

_BOOTSTRAP_FLAG = "DEEPLOY_GAP9_BOOTSTRAPPED"
_DEFAULT_SDK_HOME = "/app/install/gap9-sdk"


def bootstrap_gap9_env() -> None:
    """Re-exec under the GAP9 venv with `gap9_evk_audio.sh` already sourced.

    Replaces the manual ``source .gap9-venv/bin/activate`` /
    ``source gap9_evk_audio.sh`` / ``export GVSOC_INSTALL_DIR=...`` dance
    documented in ``README_GAP9.md``. Idempotent (guarded by the
    ``DEEPLOY_GAP9_BOOTSTRAPPED`` env flag) and a no-op outside the GAP9
    container, where the SDK paths don't exist. Override the SDK location
    with ``GAP_SDK_HOME``.

    Call this BEFORE importing anything that depends on the GAP9 venv's
    site-packages — once we re-exec, the new interpreter starts from
    scratch.
    """
    if os.environ.get(_BOOTSTRAP_FLAG) == "1":
        return

    sdk = Path(os.environ.get("GAP_SDK_HOME", _DEFAULT_SDK_HOME))
    venv_dir = sdk / ".gap9-venv"
    venv_py = venv_dir / "bin" / "python"
    board_cfg = sdk / "configs" / "gap9_evk_audio.sh"
    gvsoc_install = sdk / "install" / "workstation"

    if not venv_py.exists() or not board_cfg.exists():
        return

    # Capture the env after sourcing the board config; suppress any chatter
    # so it can't be mistaken for env entries.
    out = subprocess.check_output(["bash", "-c", f"source {shlex.quote(str(board_cfg))} >/dev/null 2>&1 && env -0"])
    new_env = dict(os.environ)
    for entry in out.split(b"\x00"):
        if not entry:
            continue
        key, _, value = entry.decode().partition("=")
        new_env[key] = value

    # Mimic what `activate` does so anything we shell out to (gapy, etc.)
    # also picks up the venv.
    new_env["VIRTUAL_ENV"] = str(venv_dir)
    new_env["PATH"] = f"{venv_dir / 'bin'}{os.pathsep}{new_env.get('PATH', '')}"
    new_env["GVSOC_INSTALL_DIR"] = str(gvsoc_install)
    new_env[_BOOTSTRAP_FLAG] = "1"

    if Path(sys.executable).resolve() == venv_py.resolve():
        os.environ.update(new_env)
        return

    os.execve(str(venv_py), [str(venv_py), *sys.argv], new_env)
