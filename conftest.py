# conftest.py (repo root) — only if not already present
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "skills"))
# Symlink import path: skills.epic-driven-roadmap → skills.epic_driven_roadmap
import importlib.util, types
_pkg = types.ModuleType("epic_driven_roadmap")
_pkg.__path__ = [str(ROOT / "skills/epic-driven-roadmap")]
sys.modules["epic_driven_roadmap"] = _pkg
_adapt = types.ModuleType("epic_driven_roadmap.adapters")
_adapt.__path__ = [str(ROOT / "skills/epic-driven-roadmap/adapters")]
sys.modules["epic_driven_roadmap.adapters"] = _adapt
_lm = types.ModuleType("epic_driven_roadmap.adapters.local_markdown")
_lm.__path__ = [str(ROOT / "skills/epic-driven-roadmap/adapters/local-markdown")]
sys.modules["epic_driven_roadmap.adapters.local_markdown"] = _lm
# also expose under skills.* path
_skills = types.ModuleType("skills"); _skills.__path__ = [str(ROOT / "skills")]
sys.modules["skills"] = _skills
sys.modules["skills.epic_driven_roadmap"] = _pkg
sys.modules["skills.epic_driven_roadmap.adapters"] = _adapt
sys.modules["skills.epic_driven_roadmap.adapters.local_markdown"] = _lm
