"""
Custom linter for project-specific anti-patterns.
Checks for forbidden imports, print statements, and TODO comments in scripts/ and run_app.py.
"""
import pathlib
import sys
import re

ROOT = pathlib.Path(__file__).parent.parent
TARGETS = list((ROOT / "scripts").glob("*.py")) + [ROOT / "run_app.py"]

FORBIDDEN_IMPORTS = ["os.system", "subprocess.Popen"]
FORBIDDEN_PATTERNS = [r"\bprint\(", r"#\s*TODO"]

errors = []
for file in TARGETS:
    code = file.read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_IMPORTS:
        if forbidden in code:
            errors.append(f"{file}: forbidden import '{forbidden}' found.")
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code):
            errors.append(f"{file}: forbidden pattern '{pattern}' found.")

if errors:
    print("Custom lint errors found:")
    for err in errors:
        print(err)
    sys.exit(1)
else:
    print("No custom lint errors found.")
