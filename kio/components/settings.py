from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# kio/components/settings.py -> kio/config/kio.yaml
_PACKAGE_CONFIG = Path(__file__).resolve().parent.parent / "config" / "kio.yaml"
print(_PACKAGE_CONFIG)
# 仓库根目录 config/kio.yaml（可选，用于部署/本地覆盖）
_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPO_CONFIG = _REPO_ROOT / "config" / "kio.yaml"
print(_REPO_CONFIG)

@dataclass(frozen=True)
class KioSettings:
    """运行配置：先读 YAML（包内 + 仓库 config/），再由环境变量 KIO_* 覆盖。"""

    host: str
    port: int
    reload: bool


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return raw if isinstance(raw, dict) else {}


def _merge_shallow(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    out = dict(a)
    out.update(b)
    return out


def _coerce_reload(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    s = str(value).strip().lower()
    return s in ("1", "true", "yes", "on")


def load_kio_settings() -> KioSettings:
    merged = _merge_shallow(_load_yaml(_PACKAGE_CONFIG), _load_yaml(_REPO_CONFIG))

    host = str(merged.get("host", "0.0.0.0"))
    port = int(merged.get("port", 9000))
    reload = _coerce_reload(merged.get("reload", True))

    # 环境变量优先级最高（未设置则保留 YAML/合并结果）
    if "KIO_HOST" in os.environ:
        host = os.environ["KIO_HOST"].strip()
    if "KIO_PORT" in os.environ:
        port = int(os.environ["KIO_PORT"])
    if "KIO_RELOAD" in os.environ:
        reload = _coerce_reload(os.environ["KIO_RELOAD"])

    return KioSettings(host=host, port=port, reload=reload)
