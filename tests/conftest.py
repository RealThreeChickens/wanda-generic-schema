"""Schema tests run memory-capped (2 GB Job Object, wanda_common/memguard.py found by env WANDA_COMMON_PATH, else
beside this repo); without wanda_common they run uncapped and say so."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_common = Path(os.environ.get("WANDA_COMMON_PATH") or ROOT.parent / "wanda_common")
if (_common / "memguard.py").is_file():
    sys.path.insert(0, str(_common))
    import memguard  # noqa: E402

    memguard.install(2048)
else:
    print(f"schema tests: no wanda_common/memguard.py at {_common} - running without a memory cap", file=sys.stderr)
