#!/usr/bin/env python3
"""
Rule Visualization Dashboard
- Interactive web dashboard for rule analytics, coverage, drift, and trends
- Visualizes rule violations, performance, adoption, and more
Category: analytics, visualization
"""
import sys
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

LOGS_DIR = Path(__file__).parent.parent / "logs"

# Helper to load JSONL logs
def load_jsonl(path):
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def build_dashboard():
    # Load logs
    violations = load_jsonl(LOGS_DIR / "rule_violations.jsonl")
    performance = load_jsonl(LOGS_DIR / "rule_performance.jsonl")
    adoption = load_jsonl(LOGS_DIR / "rule_adoption.jsonl")
    drift = load_jsonl(LOGS_DIR / "rule_drift.jsonl")
    # DataFrames
    df_v = pd.DataFrame(violations)
    df_p = pd.DataFrame(performance)
    df_a = pd.DataFrame(adoption)
    df_d = pd.DataFrame(drift)
    # Layout
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1("SmartAIPlatform Rule Visualization Dashboard"),
        dcc.Tabs([
            dcc.Tab(label='Violations', children=[
                dcc.Graph(figure=px.histogram(df_v, x='rule', color='severity', title='Rule Violations by Rule')) if not df_v.empty else html.Div("No violation data.")
            ]),
            dcc.Tab(label='Performance', children=[
                dcc.Graph(figure=px.box(df_p, x='rule', y='runtime_ms', title='Rule Performance (ms)')) if not df_p.empty else html.Div("No performance data.")
            ]),
            dcc.Tab(label='Adoption', children=[
                dcc.Graph(figure=px.bar(df_a, x='rule', y='adoption_rate', title='Rule Adoption Rate')) if not df_a.empty else html.Div("No adoption data.")
            ]),
            dcc.Tab(label='Drift', children=[
                dcc.Graph(figure=px.line(df_d, x='timestamp', y='drift_score', color='rule', title='Rule Drift Over Time')) if not df_d.empty else html.Div("No drift data.")
            ]),
        ])
    ])
    return app

def main():
    app = build_dashboard()
    app.run(debug=True, port=8050)

if __name__ == "__main__":
    main()
