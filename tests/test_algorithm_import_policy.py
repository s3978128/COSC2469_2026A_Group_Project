import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ALGORITHMS_DIR = SRC / "algorithms"

# Modules and helpers that should not be imported inside src/algorithms.
BANNED_MODULE_PREFIXES = {
    "heapq",
    "bisect",
    "queue",
    "networkx",
    "numpy",
    "scipy",
}

BANNED_FROM_IMPORTS = {
    ("collections", "deque"),
    ("queue", "PriorityQueue"),
}


class TestAlgorithmImportPolicy(unittest.TestCase):
    def test_algorithms_do_not_use_banned_helpers(self):
        violations = []

        for path in sorted(ALGORITHMS_DIR.glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        top = module_name.split(".")[0]
                        if top in BANNED_MODULE_PREFIXES:
                            violations.append(f"{path.name}: import {module_name}")

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    top = module.split(".")[0] if module else ""
                    if top in BANNED_MODULE_PREFIXES:
                        imported = ", ".join(alias.name for alias in node.names)
                        violations.append(f"{path.name}: from {module} import {imported}")

                    for alias in node.names:
                        if (module, alias.name) in BANNED_FROM_IMPORTS:
                            violations.append(
                                f"{path.name}: from {module} import {alias.name}"
                            )

        self.assertFalse(
            violations,
            "Disallowed imports detected in src/algorithms:\n"
            + "\n".join(sorted(violations)),
        )


if __name__ == "__main__":
    unittest.main()
