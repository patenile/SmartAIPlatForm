#!/usr/bin/env python3
"""
Mermaid Diagram Renderer Utility
- Used by rule_dependency_graph.py to write Mermaid diagrams to markdown files
- Can be extended for other scripts
"""
def renderMermaidDiagram(mermaid_code, output_path):
    """
    Write Mermaid diagram code to a markdown file with proper formatting.
    Args:
        mermaid_code (str): Mermaid diagram code (e.g., 'graph TD...')
        output_path (str or Path): Path to output markdown file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Rule Dependency Graph\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n````\n")
    print(f"Mermaid diagram written to {output_path}")

# Optional: CLI usage for quick rendering
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python renderMermaidDiagram.py <input_mermaid_file> <output_md_file>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        code = f.read()
    renderMermaidDiagram(code, sys.argv[2])
