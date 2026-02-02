"""
Generate a test matrix mapping implemented test functions to the design code (scripts/modules) they target, and output a Markdown summary for docs/tests_matrix.md.
"""
import ast
import pathlib
import re

test_dir = pathlib.Path(__file__).parent.parent / "tests"
scripts_dir = pathlib.Path(__file__).parent.parent / "scripts"
run_app = pathlib.Path(__file__).parent.parent / "run_app.py"
out_path = pathlib.Path(__file__).parent.parent / "docs" / "tests_matrix.md"

def extract_tests(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    tests = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            doc = ast.get_docstring(node) or ""
            # Try to extract target from docstring or parametrize decorators
            targets = set()
            if doc:
                for line in doc.splitlines():
                    m = re.search(r"target[s]?:?\s*([\w\./, ]+)", line, re.I)
                    if m:
                        targets.update([t.strip() for t in m.group(1).split(",")])
            for deco in node.decorator_list:
                if isinstance(deco, ast.Call) and hasattr(deco.func, 'id') and deco.func.id == 'pytest.mark.parametrize':
                    for arg in deco.args:
                        if hasattr(arg, 'elts'):
                            for elt in arg.elts:
                                if hasattr(elt, 's'):
                                    targets.add(elt.s)
            tests.append((node.name, doc, sorted(targets)))
    return tests

def main():
    all_tests = []
    for py_file in test_dir.glob("test_*.py"):
        tests = extract_tests(py_file)
        if tests:
            all_tests.append(f"### {py_file.name}\n")
            for name, doc, targets in tests:
                target_str = ", ".join(targets) if targets else "(see code)"
                all_tests.append(f"- **{name}** → **Targets:** {target_str}\n  - Doc: {doc or 'No docstring.'}")
            all_tests.append("")
    out_path.write_text("\n".join(all_tests), encoding="utf-8")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
