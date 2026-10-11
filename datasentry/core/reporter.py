import json
from typing import Any, Dict
from jinja2 import Template


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataSentry — Quality & Profiling Report</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text-main); padding: 2rem; line-height: 1.5; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }
        h1 { font-size: 1.8rem; display: flex; align-items: center; gap: 0.5rem; color: #fff; }
        .badge { background: #0284c7; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.5rem; }
        .metric-title { font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .metric-value { font-size: 2rem; font-weight: 700; margin-top: 0.5rem; }
        .score-circle { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; font-size: 1.5rem; font-weight: bold; }
        .score-A { background: rgba(34, 197, 94, 0.2); color: var(--success); border: 2px solid var(--success); }
        .score-B { background: rgba(56, 189, 248, 0.2); color: var(--accent); border: 2px solid var(--accent); }
        .score-C { background: rgba(245, 158, 11, 0.2); color: var(--warning); border: 2px solid var(--warning); }
        .score-F { background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 2px solid var(--danger); }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }
        th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        th { background: #1e293b; color: var(--text-muted); font-weight: 600; }
        tr:hover { background: rgba(255, 255, 255, 0.02); }
        .tag { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; background: #334155; }
        .suggestion-item { padding: 0.75rem; border-left: 4px solid var(--warning); background: #1e293b; margin-bottom: 0.5rem; border-radius: 0 0.5rem 0.5rem 0; }
        footer { margin-top: 3rem; text-align: center; color: var(--text-muted); font-size: 0.85rem; border-top: 1px solid var(--border); padding-top: 1.5rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🛡️ DataSentry Quality Report</h1>
                <p style="color: var(--text-muted); margin-top: 0.25rem;">Automated Dataset Profiling & Verification</p>
            </div>
            <div class="score-circle score-{{ profile.quality_score.grade }}">
                {{ profile.quality_score.score }}%
            </div>
        </header>

        <!-- Summary KPI Cards -->
        <div class="grid">
            <div class="card">
                <div class="metric-title">Total Rows</div>
                <div class="metric-value">{{ profile.summary.row_count }}</div>
            </div>
            <div class="card">
                <div class="metric-title">Total Columns</div>
                <div class="metric-value">{{ profile.summary.column_count }}</div>
            </div>
            <div class="card">
                <div class="metric-title">Duplicate Rows</div>
                <div class="metric-value" style="color: {{ 'var(--danger)' if profile.summary.duplicate_rows > 0 else 'var(--success)' }}">
                    {{ profile.summary.duplicate_rows }}
                </div>
            </div>
            <div class="card">
                <div class="metric-title">Missing Cells</div>
                <div class="metric-value" style="color: {{ 'var(--warning)' if profile.summary.total_missing_cells > 0 else 'var(--success)' }}">
                    {{ profile.summary.total_missing_cells }}
                </div>
            </div>
        </div>

        <!-- Column Profiles -->
        <div class="card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.25rem; margin-bottom: 0.5rem;">Column Profiling & Semantic Types</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Semantic Type</th>
                        <th>Dtype</th>
                        <th>Nulls (%)</th>
                        <th>Distinct</th>
                        <th>Range / Top Values</th>
                    </tr>
                </thead>
                <tbody>
                    {% for name, col in profile.columns.items() %}
                    <tr>
                        <td><strong>{{ name }}</strong></td>
                        <td><span class="tag">{{ col.semantic_type }}</span></td>
                        <td><code>{{ col.pandas_dtype }}</code></td>
                        <td>{{ col.null_count }} ({{ col.null_percentage }}%)</td>
                        <td>{{ col.distinct_count }}</td>
                        <td>
                            {% if col.min is defined %}
                                [{{ col.min }} → {{ col.max }}] (μ: {{ col.mean }})
                            {% elif col.top_values is defined %}
                                {{ col.top_values.keys() | list | join(', ') }}
                            {% else %}
                                —
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Cleaning Suggestions -->
        {% if profile.cleaning_suggestions %}
        <div class="card" style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.25rem; margin-bottom: 1rem;">💡 Smart Cleaning Recommendations</h2>
            {% for s in profile.cleaning_suggestions %}
            <div class="suggestion-item">
                <strong>[{{ s.type | upper }} - {{ s.severity | upper }}]</strong> {{ s.message }}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <footer>
            Generated by <strong>DataSentry v0.1.0</strong> • Unified Open-Source Data Quality Platform
        </footer>
    </div>
</body>
</html>
"""


def generate_html_report(profile_data: Dict[str, Any], output_path: str) -> None:
    template = Template(HTML_TEMPLATE)
    html_content = template.render(profile=profile_data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_json_report(data: Dict[str, Any], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
