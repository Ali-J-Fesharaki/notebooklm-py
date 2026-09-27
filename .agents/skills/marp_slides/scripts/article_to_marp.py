#!/usr/bin/env python3
"""Generate Marp Markdown slide decks from articles using notebooklm-py.

This module feeds articles into a NotebookLM notebook for grounded content
extraction, then produces Marp-flavored Markdown with mermaid diagrams,
speaker notes, a custom CSS theme, and optional PDF/HTML export.  It can also
generate the native NotebookLM slide deck for side-by-side comparison.

Usage (CLI):
    python article_to_marp.py --file article.md --output slides.md
    python article_to_marp.py --url https://example.com --output slides.md --theme dark

Usage (library):
    from article_to_marp import ArticleToMarp
    result = await ArticleToMarp(theme="dark").generate(
        files=["article.md"], output_path="slides.md",
    )
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from notebooklm import NotebookLMClient

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
THEMES_DIR = SCRIPT_DIR / "themes"

# ─── Structured extraction prompts ──────────────────────────────────────────

EXTRACTION_PROMPT = textwrap.dedent("""\
    You are a presentation architect. Analyze the provided source material and
    produce a JSON object (no markdown fences, raw JSON only) with this schema:

    {{
      "title": "Concise presentation title",
      "subtitle": "One-line description",
      "authors": "Author names if found, else empty string",
      "sections": [
        {{
          "heading": "Section title",
          "bullets": ["Key point 1", "Key point 2", "Key point 3"],
          "speaker_notes": "Detailed explanation for the presenter",
          "diagram": {{
            "type": "mermaid_type or null",
            "code": "mermaid code or null",
            "caption": "diagram caption or null"
          }},
          "code_block": {{
            "language": "python or null",
            "code": "code snippet or null",
            "caption": "code caption or null"
          }},
          "table": {{
            "headers": ["Col1", "Col2"],
            "rows": [["val1", "val2"]],
            "caption": "table caption or null"
          }}
        }}
      ],
      "conclusion_bullets": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
      "keywords": ["keyword1", "keyword2"]
    }}

    Rules:
    - Limit to {max_slides} sections maximum.
    - Each section should have 3-5 concise bullet points.
    - Speaker notes should be 2-4 sentences with deeper context.
    - Include mermaid diagrams where relationships, flows, or architectures
      exist. Use graph TD, sequenceDiagram, or flowchart LR as appropriate.
    - Include code blocks ONLY if the source contains code or algorithms.
    - Include tables ONLY for genuinely comparative or structured data.
    - Set diagram/code_block/table to null when not applicable for a section.
    - Focus on the most important content; be selective, not exhaustive.
    {extra_instructions}
""")


# ─── Data classes ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DiagramData:
    type: str | None = None
    code: str | None = None
    caption: str | None = None


@dataclass(frozen=True)
class CodeBlockData:
    language: str | None = None
    code: str | None = None
    caption: str | None = None


@dataclass(frozen=True)
class TableData:
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    caption: str | None = None


@dataclass(frozen=True)
class SlideSection:
    heading: str
    bullets: list[str] = field(default_factory=list)
    speaker_notes: str = ""
    diagram: DiagramData | None = None
    code_block: CodeBlockData | None = None
    table: TableData | None = None


@dataclass(frozen=True)
class SlideContent:
    title: str
    subtitle: str
    authors: str
    sections: list[SlideSection]
    conclusion_bullets: list[str]
    keywords: list[str]


@dataclass
class GenerationResult:
    marp_path: str
    native_path: str | None = None
    export_path: str | None = None
    notebook_id: str | None = None


# ─── Content extraction ────────────────────────────────────────────────────

def _parse_slide_content(raw: str) -> SlideContent:
    """Parse the JSON response from NotebookLM into SlideContent."""
    # Strip markdown fences if the model wrapped them anyway
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    data = json.loads(cleaned)

    sections = []
    for s in data.get("sections", []):
        diagram = None
        if s.get("diagram") and s["diagram"].get("code"):
            diagram = DiagramData(
                type=s["diagram"].get("type"),
                code=s["diagram"]["code"],
                caption=s["diagram"].get("caption"),
            )

        code_block = None
        if s.get("code_block") and s["code_block"].get("code"):
            code_block = CodeBlockData(
                language=s["code_block"].get("language", ""),
                code=s["code_block"]["code"],
                caption=s["code_block"].get("caption"),
            )

        table = None
        if s.get("table") and s["table"].get("headers"):
            table = TableData(
                headers=s["table"]["headers"],
                rows=s["table"].get("rows", []),
                caption=s["table"].get("caption"),
            )

        sections.append(SlideSection(
            heading=s.get("heading", ""),
            bullets=s.get("bullets", []),
            speaker_notes=s.get("speaker_notes", ""),
            diagram=diagram,
            code_block=code_block,
            table=table,
        ))

    return SlideContent(
        title=data.get("title", "Untitled"),
        subtitle=data.get("subtitle", ""),
        authors=data.get("authors", ""),
        sections=sections,
        conclusion_bullets=data.get("conclusion_bullets", []),
        keywords=data.get("keywords", []),
    )


async def extract_slide_content(
    client: NotebookLMClient,
    notebook_id: str,
    *,
    max_slides: int = 15,
    instructions: str = "",
) -> SlideContent:
    """Use grounded chat to extract structured slide content from a notebook."""
    extra = f"Additional focus instructions: {instructions}" if instructions else ""
    prompt = EXTRACTION_PROMPT.format(max_slides=max_slides, extra_instructions=extra)

    result = await client.chat.ask(notebook_id, prompt)
    logger.info("Extraction complete (%d chars)", len(result.answer))
    return _parse_slide_content(result.answer)


# ─── Marp rendering ────────────────────────────────────────────────────────

def _render_frontmatter(theme: str) -> str:
    """Render Marp YAML frontmatter."""
    theme_name = f"marp-{theme}" if theme in ("dark", "light") else theme
    return textwrap.dedent(f"""\
        ---
        marp: true
        theme: {theme_name}
        paginate: true
        math: katex
        size: 16:9
        ---
    """)


def _render_title_slide(content: SlideContent) -> str:
    """Render the title slide."""
    lines = ["<!-- _class: lead -->", ""]
    lines.append(f"# {content.title}")
    if content.subtitle:
        lines.append(f"## {content.subtitle}")
    lines.append("")
    meta_parts = []
    if content.authors:
        meta_parts.append(content.authors)
    meta_parts.append(datetime.now().strftime("%B %Y"))
    lines.append(" · ".join(meta_parts))
    lines.append("")
    return "\n".join(lines)


def _render_speaker_notes(notes: str) -> str:
    """Wrap text in Marp speaker notes comment."""
    if not notes:
        return ""
    wrapped = textwrap.fill(notes, width=80)
    return f"\n<!--\n{wrapped}\n-->\n"


def _render_section_slide(section: SlideSection) -> str:
    """Render a single content slide."""
    lines = [f"# {section.heading}", ""]

    # Bullets
    for bullet in section.bullets:
        lines.append(f"- {bullet}")
    if section.bullets:
        lines.append("")

    # Table (if present)
    if section.table and section.table.headers:
        t = section.table
        header_line = "| " + " | ".join(t.headers) + " |"
        sep_line = "| " + " | ".join("---" for _ in t.headers) + " |"
        lines.append(header_line)
        lines.append(sep_line)
        for row in t.rows:
            # Pad row to header length
            padded = row + [""] * (len(t.headers) - len(row))
            lines.append("| " + " | ".join(padded[:len(t.headers)]) + " |")
        if t.caption:
            lines.append(f"\n*{t.caption}*")
        lines.append("")

    # Code block (if present)
    if section.code_block and section.code_block.code:
        cb = section.code_block
        lang = cb.language or ""
        lines.append(f"```{lang}")
        lines.append(cb.code)
        lines.append("```")
        if cb.caption:
            lines.append(f"*{cb.caption}*")
        lines.append("")

    # Mermaid diagram (if present)
    if section.diagram and section.diagram.code:
        d = section.diagram
        lines.append("```mermaid")
        lines.append(d.code)
        lines.append("```")
        if d.caption:
            lines.append(f"*{d.caption}*")
        lines.append("")

    # Speaker notes
    lines.append(_render_speaker_notes(section.speaker_notes))

    return "\n".join(lines)


def _render_conclusion_slide(content: SlideContent) -> str:
    """Render the conclusion/takeaways slide."""
    lines = ["<!-- _class: divider -->", "", "# Key Takeaways", ""]
    for bullet in content.conclusion_bullets:
        lines.append(f"- {bullet}")
    lines.append("")
    if content.keywords:
        lines.append(f"**Keywords:** {', '.join(content.keywords)}")
    lines.append("")
    return "\n".join(lines)


def render_marp(content: SlideContent, *, theme: str = "dark") -> str:
    """Render a SlideContent into a complete Marp Markdown string."""
    parts = [_render_frontmatter(theme)]
    parts.append(_render_title_slide(content))

    for i, section in enumerate(content.sections):
        parts.append("---\n")
        # Insert a divider slide every 4 sections for pacing
        if i > 0 and i % 4 == 0:
            parts.append("<!-- _class: divider -->\n")
            parts.append(f"# {section.heading}\n")
            parts.append("---\n")
        parts.append(_render_section_slide(section))

    parts.append("---\n")
    parts.append(_render_conclusion_slide(content))
    parts.append("---\n")
    parts.append("<!-- _class: lead -->\n")
    parts.append("# Thank You\n")
    parts.append("Questions & Discussion\n")

    return "\n".join(parts)


# ─── Export helpers ─────────────────────────────────────────────────────────

def _export_marp(marp_path: str, fmt: str, theme_css: Path | None) -> str:
    """Export Marp markdown to PDF/HTML/PPTX using marp-cli."""
    if not shutil.which("marp"):
        raise RuntimeError(
            "marp-cli not found. Install with: npm install -g @marp-team/marp-cli"
        )

    ext_map = {"pdf": ".pdf", "html": ".html", "pptx": ".pptx"}
    ext = ext_map.get(fmt, f".{fmt}")
    output_path = str(Path(marp_path).with_suffix(ext))

    cmd = ["marp", marp_path, "-o", output_path, "--allow-local-files"]
    if theme_css and theme_css.exists():
        cmd.extend(["--theme", str(theme_css)])

    logger.info("Exporting: %s", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_path


# ─── Main orchestrator ─────────────────────────────────────────────────────

class ArticleToMarp:
    """High-level converter: articles → Marp slides."""

    def __init__(
        self,
        *,
        theme: str = "dark",
        max_slides: int = 15,
        language: str = "en",
    ):
        self.theme = theme
        self.max_slides = max_slides
        self.language = language

    async def generate(
        self,
        *,
        urls: list[str] | None = None,
        files: list[str] | None = None,
        texts: list[str] | None = None,
        output_path: str = "slides.md",
        native_slides_path: str | None = None,
        export_format: str | None = None,
        keep_notebook: bool = False,
        instructions: str = "",
    ) -> GenerationResult:
        """Run the full pipeline: ingest → extract → render → export."""
        if not any([urls, files, texts]):
            raise ValueError("Provide at least one url, file, or text source.")

        result = GenerationResult(marp_path=output_path)

        async with NotebookLMClient.from_storage() as client:
            # 1. Create notebook
            nb_title = f"Slides: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            nb = await client.notebooks.create(nb_title)
            result.notebook_id = nb.id
            logger.info("Created notebook %s", nb.id)

            try:
                # 2. Add sources
                source_ids: list[str] = []

                for url in urls or []:
                    src = await client.sources.add_url(nb.id, url)
                    source_ids.append(src.id)
                    logger.info("Added URL source: %s", src.title)

                for fpath in files or []:
                    p = Path(fpath)
                    if not p.exists():
                        raise FileNotFoundError(f"File not found: {fpath}")
                    if p.suffix.lower() in (".md", ".txt"):
                        text = p.read_text(encoding="utf-8")
                        src = await client.sources.add_text(
                            nb.id, p.stem, text
                        )
                    else:
                        src = await client.sources.add_file(nb.id, str(p))
                    source_ids.append(src.id)
                    logger.info("Added file source: %s", p.name)

                for i, text in enumerate(texts or []):
                    src = await client.sources.add_text(
                        nb.id, f"Text source {i + 1}", text
                    )
                    source_ids.append(src.id)

                # 3. Wait for all sources
                for sid in source_ids:
                    await client.sources.wait_until_ready(
                        nb.id, sid, timeout=600
                    )
                logger.info("All %d sources ready", len(source_ids))

                # 4. Extract structured content via chat
                content = await extract_slide_content(
                    client, nb.id,
                    max_slides=self.max_slides,
                    instructions=instructions,
                )

                # 5. Render Marp markdown
                marp_md = render_marp(content, theme=self.theme)
                Path(output_path).write_text(marp_md, encoding="utf-8")
                logger.info("Wrote Marp slides to %s", output_path)

                # 6. Generate native NotebookLM slide deck (optional)
                if native_slides_path:
                    logger.info("Generating native NotebookLM slide deck...")
                    status = await client.artifacts.generate_slide_deck(
                        nb.id,
                        source_ids=source_ids,
                        language=self.language,
                        instructions=instructions or None,
                    )
                    final = await client.artifacts.wait_for_completion(
                        nb.id, status.task_id, timeout=600,
                    )
                    if final.is_complete:
                        dl = await client.artifacts.download_slide_deck(
                            nb.id, native_slides_path,
                            artifact_id=status.task_id,
                        )
                        result.native_path = dl
                        logger.info("Downloaded native deck to %s", dl)
                    else:
                        logger.warning(
                            "Native deck generation ended with: %s",
                            final.status,
                        )

                # 7. Export (optional)
                if export_format:
                    theme_css = THEMES_DIR / f"{self.theme}.css"
                    result.export_path = _export_marp(
                        output_path, export_format, theme_css
                    )
                    logger.info("Exported to %s", result.export_path)

            finally:
                if not keep_notebook and result.notebook_id:
                    await client.notebooks.delete(nb.id)
                    logger.info("Cleaned up notebook %s", nb.id)

        return result


# ─── CLI ────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Marp slide decks from articles using NotebookLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s --file article.md --output slides.md
              %(prog)s --url https://example.com --theme dark --export pdf
              %(prog)s --file a.md --file b.md --native-slides native.pdf
        """),
    )
    parser.add_argument(
        "--url", action="append", dest="urls", default=[],
        help="Article URL (repeatable)",
    )
    parser.add_argument(
        "--file", action="append", dest="files", default=[],
        help="Article file path (repeatable)",
    )
    parser.add_argument(
        "--text", action="append", dest="texts", default=[],
        help="Inline text source (repeatable)",
    )
    parser.add_argument(
        "--output", "-o", default="slides.md",
        help="Output Marp Markdown path (default: slides.md)",
    )
    parser.add_argument(
        "--theme", "-t", default="dark", choices=["dark", "light"],
        help="Theme name (default: dark)",
    )
    parser.add_argument(
        "--language", default="en",
        help="Slide language (default: en)",
    )
    parser.add_argument(
        "--max-slides", type=int, default=15,
        help="Maximum number of content slides (default: 15)",
    )
    parser.add_argument(
        "--native-slides",
        help="Also generate native NotebookLM slide deck at this path",
    )
    parser.add_argument(
        "--export", choices=["pdf", "html", "pptx"],
        help="Export format (requires marp-cli)",
    )
    parser.add_argument(
        "--keep-notebook", action="store_true",
        help="Don't delete the notebook after generation",
    )
    parser.add_argument(
        "--instructions", default="",
        help="Extra instructions for content focus",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    return parser


async def async_main(args: argparse.Namespace) -> None:
    converter = ArticleToMarp(
        theme=args.theme,
        max_slides=args.max_slides,
        language=args.language,
    )
    result = await converter.generate(
        urls=args.urls or None,
        files=args.files or None,
        texts=args.texts or None,
        output_path=args.output,
        native_slides_path=args.native_slides,
        export_format=args.export,
        keep_notebook=args.keep_notebook,
        instructions=args.instructions,
    )

    print(f"\n✅ Marp slides written to: {result.marp_path}")
    if result.native_path:
        print(f"✅ Native NotebookLM deck: {result.native_path}")
    if result.export_path:
        print(f"✅ Exported to: {result.export_path}")
    if result.notebook_id and args.keep_notebook:
        print(f"📓 Notebook kept: {result.notebook_id}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    if not args.urls and not args.files and not args.texts:
        parser.error("Provide at least one --url, --file, or --text source.")

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
