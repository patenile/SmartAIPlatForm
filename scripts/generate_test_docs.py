"""
Script to auto-generate test documentation from test code and comments.
Outputs a Markdown file with test names, docstrings, and comments.
"""
import ast
import pathlib

test_dir = pathlib.Path(__file__).parent.parent / "tests"
out_path = pathlib.Path(__file__).parent.parent / "docs" / "generated_test_docs.md"

def extract_tests(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    tests = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            doc = ast.get_docstring(node) or ""
            tests.append((node.name, doc))
    return tests

def main():
    all_tests = []
    for py_file in test_dir.glob("test_*.py"):
        tests = extract_tests(py_file)
        if tests:
            all_tests.append(f"### {py_file.name}\n")
            for name, doc in tests:
                all_tests.append(f"- **{name}**: {doc or 'No docstring.'}")
            all_tests.append("")
    out_path.write_text("\n".join(all_tests), encoding="utf-8")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
