# Rule Dependency Graph

```mermaid
graph TD
    %% Add dependencies/conflicts in rule_mapping.json to visualize here
```

- Solid arrows (-->): dependency (A must run before B)
- Dashed arrows (-.->): conflict (A and B should not be enabled together)

Run `python3 scripts/rule_dependency_graph.py --update-graph` to update this diagram.
