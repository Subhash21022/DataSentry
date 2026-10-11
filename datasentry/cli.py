import sys
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import pandas as pd

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from datasentry.core.profiler import DataProfiler
from datasentry.core.validator import DataValidator
from datasentry.core.ml_anomaly import MLAnomalyDetector
from datasentry.core.reporter import generate_html_report, generate_json_report

app = typer.Typer(
    name="datasentry",
    help="DataSentry: All-in-One Data Quality, Profiling & ML Anomaly Detection Platform",
    add_completion=False,
)
console = Console(legacy_windows=False)


@app.command()
def profile(
    filepath: str = typer.Argument(..., help="Path to CSV dataset to profile"),
    output_json: Optional[str] = typer.Option(None, "--json", help="Save profile output to JSON"),
):
    """
    📊 Run deep statistical and semantic profiling on a dataset.
    """
    path = Path(filepath)
    if not path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    with console.status(f"[bold cyan]Profiling {path.name}...[/bold cyan]"):
        profiler = DataProfiler.from_csv(filepath)
        report = profiler.run_profile()

    # Summary Panel
    summary = report["summary"]
    score_data = report["quality_score"]

    console.print(
        Panel(
            f"[bold]Rows:[/bold] {summary['row_count']} | "
            f"[bold]Columns:[/bold] {summary['column_count']} | "
            f"[bold]Duplicates:[/bold] {summary['duplicate_rows']} | "
            f"[bold]Null Cells:[/bold] {summary['total_missing_cells']} | "
            f"[bold]Score:[/bold] [cyan]{score_data['score']}% (Grade: {score_data['grade']})[/cyan]",
            title="🛡️ DataSentry Profile Summary",
            border_style="cyan",
        )
    )

    # Columns Table
    table = Table(title="Column Details", show_header=True, header_style="bold magenta")
    table.add_column("Column", style="dim")
    table.add_column("Type")
    table.add_column("Nulls (%)", justify="right")
    table.add_column("Distinct", justify="right")
    table.add_column("Summary / Distribution")

    for col_name, col_data in report["columns"].items():
        summary_str = ""
        if "min" in col_data:
            summary_str = f"[{col_data['min']} .. {col_data['max']}], mean={col_data['mean']}"
        elif "top_values" in col_data:
            summary_str = ", ".join(list(col_data["top_values"].keys())[:3])

        null_color = "red" if col_data["null_count"] > 0 else "green"
        table.add_row(
            col_name,
            col_data["semantic_type"],
            f"[{null_color}]{col_data['null_count']} ({col_data['null_percentage']}%) [/{null_color}]",
            str(col_data["distinct_count"]),
            summary_str,
        )

    console.print(table)

    # Cleaning suggestions
    suggestions = report.get("cleaning_suggestions", [])
    if suggestions:
        console.print("\n[bold yellow]💡 Intelligent Cleaning Suggestions:[/bold yellow]")
        for s in suggestions:
            console.print(f"  • [{s['severity'].upper()}] {s['message']}")

    if output_json:
        generate_json_report(report, output_json)
        console.print(f"\n[green]Saved JSON profile to {output_json}[/green]")


@app.command()
def validate(
    filepath: str = typer.Argument(..., help="Path to CSV dataset"),
    rules_file: Optional[str] = typer.Option(None, "--rules", "-r", help="Path to JSON validation rules file"),
):
    """
    ✅ Execute deterministic data validation rules with pass/fail exit codes.
    """
    path = Path(filepath)
    if not path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    df = pd.read_csv(filepath)

    rules = []
    if rules_file and Path(rules_file).exists():
        with open(rules_file, "r") as f:
            rules_data = json.load(f)
            rules = rules_data.get("rules", rules_data if isinstance(rules_data, list) else [])
    else:
        # Default baseline rules
        rules = [
            {"type": "not_null", "column": df.columns[0], "description": f"Primary column '{df.columns[0]}' not null"},
        ]

    validator = DataValidator(df, rules)
    result = validator.validate()

    table = Table(title="Validation Results", show_header=True, header_style="bold blue")
    table.add_column("Rule", style="dim")
    table.add_column("Description")
    table.add_column("Status", justify="center")
    table.add_column("Violations", justify="right")

    for r in result["results"]:
        status_str = "[bold green]PASS[/bold green]" if r["passed"] else "[bold red]FAIL[/bold red]"
        table.add_row(
            r["type"],
            r["description"],
            status_str,
            str(r["violations_count"]),
        )

    console.print(table)

    if not result["success"]:
        console.print(f"\n[bold red]Validation Failed:[/bold red] {result['failed_rules']} rule(s) failed.")
        raise typer.Exit(code=1)
    else:
        console.print("\n[bold green]Validation Succeeded: All rules passed![/bold green]")


@app.command()
def detect_anomalies(
    filepath: str = typer.Argument(..., help="Path to CSV dataset"),
    contamination: float = typer.Option(0.05, "--contamination", "-c", help="Expected contamination proportion (0.01 - 0.20)"),
):
    """
    🤖 Run unsupervised Machine Learning Anomaly Detection (Isolation Forest).
    """
    path = Path(filepath)
    if not path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        raise typer.Exit(code=1)

    with console.status("[bold magenta]Training Isolation Forest and scoring rows...[/bold magenta]"):
        df = pd.read_csv(filepath)
        detector = MLAnomalyDetector(df, contamination=contamination)
        result = detector.detect_anomalies()

    if "error" in result:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold]Algorithm:[/bold] {result['algorithm']} | "
            f"[bold]Evaluated Rows:[/bold] {result['evaluated_rows']} | "
            f"[bold]Anomalies Flagged:[/bold] [red]{result['total_anomalies']} ({result['anomaly_percentage']}%) [/red]",
            title="🤖 ML Tabular Anomaly Detection",
            border_style="magenta",
        )
    )

    if result["total_anomalies"] > 0:
        table = Table(title="Top Flagged Anomalies", show_header=True, header_style="bold red")
        table.add_column("Row #", justify="right")
        table.add_column("Anomaly Score", justify="right")
        table.add_column("Top Contributing Feature")
        table.add_column("Data Snapshot")

        for item in result["anomalies"][:10]:
            snapshot = ", ".join([f"{k}: {v}" for k, v in list(item["data"].items())[:3]])
            table.add_row(
                str(item["row_index"]),
                f"{item['anomaly_score']:.3f}",
                f"{item['suspected_primary_feature']} (z={item['feature_z_score']})",
                snapshot,
            )

        console.print(table)
    else:
        console.print("[green]No high-confidence anomalies detected.[/green]")


@app.command()
def report(
    filepath: str = typer.Argument(..., help="Path to CSV dataset"),
    output: str = typer.Option("report.html", "--output", "-o", help="Output report filename"),
    format: str = typer.Option("html", "--format", "-f", help="Report format: html or json"),
):
    """
    📑 Generate a complete standalone HTML or JSON Data Quality Report.
    """
    df = pd.read_csv(filepath)
    profiler = DataProfiler(df)
    profile_data = profiler.run_profile()

    if format.lower() == "html":
        generate_html_report(profile_data, output)
        console.print(f"[bold green]Successfully generated HTML report at: {output}[/bold green]")
    else:
        generate_json_report(profile_data, output)
        console.print(f"[bold green]Successfully generated JSON report at: {output}[/bold green]")


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="FastAPI server port"),
    host: str = typer.Option("127.0.0.1", "--host", help="FastAPI server host"),
):
    """
    🌐 Start the DataSentry FastAPI backend server.
    """
    import uvicorn
    console.print(f"[bold green]Starting DataSentry Backend API on http://{host}:{port}...[/bold green]")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    app()
