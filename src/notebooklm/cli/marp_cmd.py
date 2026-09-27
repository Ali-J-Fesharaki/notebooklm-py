"""Marp presentation generation CLI commands."""

from __future__ import annotations

import asyncio

import click

from ..marp import MarpPresenter
from .error_handler import exit_with_code
from .helpers import json_output_response
from .rendering import console, stderr_console


@click.group()
def marp():
    """Generate Marp presentations from articles, URLs, and NotebookLM decks."""
    pass


@marp.command("generate")
@click.option(
    "--file",
    "-f",
    "files",
    multiple=True,
    type=click.Path(exists=True),
    help="Local document/article path (can be used multiple times).",
)
@click.option(
    "--url",
    "-u",
    "urls",
    multiple=True,
    help="Article or web page URL (can be used multiple times).",
)
@click.option(
    "--text",
    "-t",
    "texts",
    multiple=True,
    help="Inline text content to ingest (can be used multiple times).",
)
@click.option(
    "--output",
    "-o",
    default="slides.md",
    show_default=True,
    help="Output Marp Markdown file path.",
)
@click.option(
    "--theme",
    default="marp-dark",
    show_default=True,
    help="Marp CSS theme name or path.",
)
@click.option(
    "--max-slides",
    type=int,
    default=15,
    show_default=True,
    help="Maximum number of content slides to generate.",
)
@click.option(
    "--use-native",
    is_flag=True,
    default=False,
    help="Extract native Google slide images (1376x768 PNGs) and embed in Marp deck.",
)
@click.option(
    "--native-slides",
    type=click.Path(),
    default=None,
    help="Also download native NotebookLM Google slide deck directly to this path.",
)
@click.option(
    "--export",
    "export_format",
    type=click.Choice(["pdf", "html", "pptx"], case_sensitive=False),
    default=None,
    help="Export presentation to PDF, HTML, or PPTX using marp-cli.",
)
@click.option(
    "--keep-notebook",
    is_flag=True,
    default=False,
    help="Keep the created NotebookLM notebook instead of deleting it after generation.",
)
@click.option(
    "--instructions",
    default="",
    help="Custom instructions to steer slide focus and emphasis.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output results in JSON format.",
)
def generate(
    files: tuple[str, ...],
    urls: tuple[str, ...],
    texts: tuple[str, ...],
    output: str,
    theme: str,
    max_slides: int,
    use_native: bool,
    native_slides: str | None,
    export_format: str | None,
    keep_notebook: bool,
    instructions: str,
    json_output: bool,
):
    """Generate Marp slides with Mermaid diagrams, speaker notes, and visual slides."""
    if not files and not urls and not texts:
        stderr_console.print("[red]Error:[/red] Provide at least one --file, --url, or --text.")
        exit_with_code(1)

    presenter = MarpPresenter(
        theme=theme,
        max_slides=max_slides,
    )

    try:
        result = asyncio.run(
            presenter.generate(
                files=list(files) if files else None,
                urls=list(urls) if urls else None,
                texts=list(texts) if texts else None,
                output_path=output,
                use_native=use_native,
                native_slides_path=native_slides,
                export_format=export_format,
                keep_notebook=keep_notebook,
                instructions=instructions,
            )
        )
    except Exception as exc:
        stderr_console.print(f"[red]Error during presentation generation:[/red] {exc}")
        exit_with_code(1)

    if json_output:
        json_output_response(
            {
                "marp_path": result.marp_path,
                "export_path": result.export_path,
                "native_path": result.native_path,
                "images_dir": result.images_dir,
                "slide_images_count": (
                    sum(1 for s in result.native_slides if s.image_path)
                    if result.native_slides
                    else 0
                ),
                "notebook_id": result.notebook_id,
            }
        )
        return

    console.print(f"[green]✓[/green] Marp presentation written to: [bold]{result.marp_path}[/bold]")
    if result.native_path:
        console.print(
            f"[green]✓[/green] Native Google slide deck: [bold]{result.native_path}[/bold]"
        )
    if result.native_slides:
        img_count = sum(1 for s in result.native_slides if s.image_path)
        console.print(
            f"[green]✓[/green] Extracted {img_count} slide images → [bold]{result.images_dir}/[/bold]"
        )
    if result.export_path:
        console.print(f"[green]✓[/green] Exported to: [bold]{result.export_path}[/bold]")
    if result.notebook_id and keep_notebook:
        console.print(f"[dim]Notebook preserved: {result.notebook_id}[/dim]")
