"""Marp presentation generation and slide extraction module for NotebookLM.

This module provides tools to extract grounded content from NotebookLM notebooks,
generate native visual slide decks, extract rendered slide images and text, and
render presentation-ready Marp Markdown decks with optional PDF/HTML/PPTX export.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from ._auth.cookies import load_httpx_cookies
from .client import NotebookLMClient

logger = logging.getLogger(__name__)

DEFAULT_MARP_THEME = "marp-dark"

# ─── Structured extraction prompts ──────────────────────────────────────────

_STRUCTURED_SLIDE_PROMPT = """Analyze all uploaded sources thoroughly and create a comprehensive, highly-structured presentation slide deck.

Return a JSON object conforming EXACTLY to the following schema:
{
  "title": "Presentation title (concise, impactful)",
  "subtitle": "Subtitle or context description",
  "authors": "Author(s) or organization name",
  "sections": [
    {
      "heading": "Section / Slide Title",
      "bullets": [
        "Concise key takeaway or finding (1-2 sentences)",
        "Data point, mechanism, or principle with context",
        "Implication, application, or result"
      ],
      "speaker_notes": "Detailed context and commentary for the presenter to say.",
      "code_block": {
        "language": "python or bash or null",
        "code": "code snippet illustrating the concept or null"
      },
      "mermaid_diagram": "flowchart TD\\n    ... or null",
      "table": {
        "headers": ["Col 1", "Col 2"],
        "rows": [["val 1", "val 2"]],
        "caption": "table caption or null"
      }
    }
  ],
  "conclusion_bullets": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "keywords": ["keyword1", "keyword2"]
}

Rules:
- Limit to {max_slides} sections maximum.
- Each section should have 3-5 concise bullet points.
- Speaker notes should be 2-4 sentences with deeper context.
- Include mermaid diagrams where relationships, flows, or architectures are discussed (valid Mermaid syntax only).
- Include code blocks where algorithms, commands, or implementations are mentioned.
- Include comparison tables when comparing methods, benchmarks, or datasets.
- Wrap the entire response in a single ```json ``` markdown code block.
{extra_instructions}
"""


# ─── Data Classes ───────────────────────────────────────────────────────────


@dataclass
class SlideSection:
    """A single content slide in the presentation."""

    heading: str
    bullets: list[str] = field(default_factory=list)
    speaker_notes: str = ""
    code_block: dict[str, str] | None = None
    mermaid_diagram: str | None = None
    table: dict[str, Any] | None = None


@dataclass
class SlideContent:
    """Complete extracted structured presentation content."""

    title: str = "Presentation"
    subtitle: str = ""
    authors: str = ""
    sections: list[SlideSection] = field(default_factory=list)
    conclusion_bullets: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


@dataclass
class NativeSlideData:
    """Rendered slide image and text extracted from a native NotebookLM slide deck."""

    index: int
    image_path: str | None = None
    image_url: str | None = None
    alt_text: str | None = None
    text: str | None = None
    width: int | None = None
    height: int | None = None


@dataclass
class MarpResult:
    """Result of generating a presentation."""

    marp_path: str
    export_path: str | None = None
    native_path: str | None = None
    native_slides: list[NativeSlideData] | None = None
    images_dir: str | None = None
    notebook_id: str | None = None


# ─── Built-in CSS Themes ────────────────────────────────────────────────────

_BUILTIN_THEMES: dict[str, str] = {
    "marp-dark": """/* @theme marp-dark */
@import 'default';

:root {
  --color-bg: #0f172a;
  --color-fg: #e2e8f0;
  --color-accent: #38bdf8;
  --color-accent-subtle: #1e293b;
  --color-border: #334155;
  --color-lead-bg: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
}

section {
  background-color: var(--color-bg);
  color: var(--color-fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 40px 60px;
}

section.lead {
  background: var(--color-lead-bg);
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

section.lead h1 {
  font-size: 2.2em;
  color: #f8fafc;
  border-bottom: none;
}

section.lead h2 {
  font-size: 1.2em;
  color: #94a3b8;
  font-weight: 400;
}

section.divider {
  background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

section.divider h1 {
  font-size: 2.0em;
  color: var(--color-accent);
  border: none;
}

h1 {
  color: #f1f5f9;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 8px;
  font-size: 1.6em;
}

h2 {
  color: var(--color-accent);
  font-size: 1.2em;
}

ul {
  font-size: 0.85em;
  line-height: 1.6;
}

li {
  margin-bottom: 8px;
}

code {
  background: var(--color-accent-subtle);
  color: #7dd3fc;
  border-radius: 4px;
  padding: 2px 6px;
}

pre {
  background: #020617;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.7em;
}

table {
  font-size: 0.75em;
  border-collapse: collapse;
  width: 100%;
}

th {
  background: #1e293b;
  color: #f8fafc;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
}

td {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
}

footer {
  font-size: 0.5em;
  color: #64748b;
}
""",
    "marp-light": """/* @theme marp-light */
@import 'default';

:root {
  --color-bg: #ffffff;
  --color-fg: #1e293b;
  --color-accent: #0284c7;
  --color-border: #e2e8f0;
}

section {
  background-color: var(--color-bg);
  color: var(--color-fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 40px 60px;
}

section.lead {
  background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
  text-align: center;
}

h1 {
  color: #0f172a;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 8px;
}

h2 {
  color: var(--color-accent);
}
""",
}


# ─── Content Extraction ─────────────────────────────────────────────────────


def _clean_json(text: str) -> str:
    """Extract JSON object from potentially markdown-wrapped model output."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        return m.group(1)
    return text.strip()


async def extract_slide_content(
    client: NotebookLMClient,
    notebook_id: str,
    *,
    max_slides: int = 15,
    instructions: str = "",
) -> SlideContent:
    """Query NotebookLM chat to extract grounded, structured presentation content."""
    extra = f"Additional instructions: {instructions}" if instructions else ""
    prompt = _STRUCTURED_SLIDE_PROMPT.replace("{max_slides}", str(max_slides)).replace(
        "{extra_instructions}", extra
    )

    logger.info("Extracting structured presentation content via NotebookLM chat...")
    resp = await client.chat.ask(notebook_id, prompt)
    raw_text = resp.answer or ""

    try:
        json_str = _clean_json(raw_text)
        data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as err:
        logger.warning("Failed to parse JSON response (%s); building fallback content", err)
        sections = [
            SlideSection(
                heading=f"Section {i + 1}",
                bullets=[p.strip() for p in para.split(". ") if p.strip()][:4],
                speaker_notes=para[:200],
            )
            for i, para in enumerate(raw_text.split("\n\n")[:max_slides])
            if para.strip()
        ]
        return SlideContent(
            title="Overview",
            sections=sections,
            conclusion_bullets=["Summary of key points"],
        )

    sections: list[SlideSection] = []
    for s in data.get("sections", []):
        sec = SlideSection(
            heading=s.get("heading", "Untitled Section"),
            bullets=s.get("bullets", []),
            speaker_notes=s.get("speaker_notes", ""),
            code_block=s.get("code_block") if s.get("code_block", {}).get("code") else None,
            mermaid_diagram=s.get("mermaid_diagram"),
            table=s.get("table") if s.get("table", {}).get("rows") else None,
        )
        sections.append(sec)

    return SlideContent(
        title=data.get("title", "Presentation"),
        subtitle=data.get("subtitle", ""),
        authors=data.get("authors", ""),
        sections=sections,
        conclusion_bullets=data.get("conclusion_bullets", []),
        keywords=data.get("keywords", []),
    )


# ─── Native Slide Deck & Image Extraction ───────────────────────────────────


async def extract_native_slide_images(
    client: NotebookLMClient,
    notebook_id: str,
    artifact_id: str,
    output_dir: Path,
) -> list[NativeSlideData]:
    """Extract rendered slide images and text from a native NotebookLM slide deck.

    Downloads each slide's high-res rendered image (1376x768 PNG) to *output_dir*
    and returns structured slide data with local paths, alt text, and text.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    artifact = await client.artifacts.get(notebook_id, artifact_id)
    if not artifact.slides:
        logger.warning("Native deck %s has no slide images", artifact_id)
        return []

    logger.info(
        "Extracting %d slide images from native deck %s",
        len(artifact.slides),
        artifact_id,
    )

    cookies = load_httpx_cookies()
    slides: list[NativeSlideData] = []
    async with httpx.AsyncClient(cookies=cookies, follow_redirects=True, timeout=60.0) as http:
        for i, slide in enumerate(artifact.slides):
            image_path = None
            if slide.image_url:
                try:
                    resp = await http.get(slide.image_url)
                    resp.raise_for_status()
                    ct = resp.headers.get("content-type", "")
                    is_png = resp.content[:8] == b"\x89PNG\r\n\x1a\n"
                    if "image" in ct or "octet-stream" in ct or is_png:
                        ext = (
                            ".png"
                            if (is_png or "png" in ct)
                            else ".jpg"
                            if "jpeg" in ct
                            else ".webp"
                            if "webp" in ct
                            else ".png"
                        )
                        img_file = output_dir / f"slide_{i + 1:02d}{ext}"
                        img_file.write_bytes(resp.content)
                        image_path = str(img_file)
                        logger.info(
                            "Downloaded slide %d image -> %s (%d bytes)",
                            i + 1,
                            img_file.name,
                            len(resp.content),
                        )
                    else:
                        logger.warning(
                            "Slide %d returned unexpected content-type: %s",
                            i + 1,
                            ct,
                        )
                except httpx.HTTPError as exc:
                    logger.warning("Failed to download slide %d image: %s", i + 1, exc)

            slides.append(
                NativeSlideData(
                    index=i,
                    image_path=image_path,
                    image_url=slide.image_url,
                    alt_text=slide.alt_text,
                    text=slide.text,
                    width=slide.width,
                    height=slide.height,
                )
            )

    logger.info(
        "Extracted %d slides (%d with downloaded images)",
        len(slides),
        sum(1 for s in slides if s.image_path),
    )
    return slides


# ─── Marp Rendering ─────────────────────────────────────────────────────────


def _render_frontmatter(theme: str) -> str:
    return f"""---
marp: true
theme: {theme}
paginate: true
math: katex
size: 16:9
---
"""


def _render_title_slide(content: SlideContent) -> str:
    lines = ["<!-- _class: lead -->\n", f"# {content.title}"]
    if content.subtitle:
        lines.append(f"## {content.subtitle}\n")
    if content.authors:
        today = datetime.now().strftime("%B %Y")
        lines.append(f"{content.authors} · {today}")
    return "\n".join(lines)


def _render_section_slide(section: SlideSection) -> str:
    lines = [f"# {section.heading}\n"]

    for bullet in section.bullets:
        lines.append(f"- {bullet}")

    if section.code_block:
        lang = section.code_block.get("language") or ""
        code = section.code_block.get("code") or ""
        lines.append(f"\n```{lang}\n{code}\n```")

    if section.mermaid_diagram:
        lines.append(f"\n```mermaid\n{section.mermaid_diagram}\n```")

    if section.table:
        headers = section.table.get("headers", [])
        rows = section.table.get("rows", [])
        caption = section.table.get("caption")
        if headers and rows:
            lines.append("")
            lines.append("| " + " | ".join(str(h) for h in headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            if caption:
                lines.append(f"*{caption}*")

    if section.speaker_notes:
        wrapped = textwrap.fill(section.speaker_notes, width=80)
        lines.append(f"\n<!--\n{wrapped}\n-->")

    return "\n".join(lines)


def _render_native_slide(native: NativeSlideData, base_dir: Path | None = None) -> str:
    lines = []
    if native.image_path:
        img_p = Path(native.image_path)
        try:
            target_path = (
                img_p.relative_to(base_dir).as_posix() if base_dir else img_p.resolve().as_posix()
            )
        except ValueError:
            target_path = img_p.resolve().as_posix()
        lines.append(f"![bg contain]({target_path})")
        lines.append("")

    if native.text:
        if native.image_path:
            wrapped = textwrap.fill(native.text, width=80)
            lines.append(f"\n<!--\n{wrapped}\n-->\n")
        else:
            for para in native.text.split("\n"):
                stripped = para.strip()
                if stripped:
                    lines.append(f"- {stripped}")
            lines.append("")
    return "\n".join(lines)


def _render_conclusion_slide(content: SlideContent) -> str:
    lines = ["# Summary & Key Takeaways\n"]
    for bullet in content.conclusion_bullets:
        lines.append(f"- {bullet}")
    if content.keywords:
        lines.append(f"\n**Keywords**: {', '.join(content.keywords)}")
    return "\n".join(lines)


def render_marp_markdown(
    content: SlideContent,
    *,
    theme: str = DEFAULT_MARP_THEME,
    native_slides: list[NativeSlideData] | None = None,
    base_dir: Path | None = None,
) -> str:
    """Render a SlideContent into a complete Marp Markdown string.

    If *native_slides* is provided, each content slide is followed by its
    corresponding native NotebookLM rendered image slide, providing both
    structured Marp takeaways and Google's high-res visual design.
    """
    parts = [_render_frontmatter(theme)]
    parts.append(_render_title_slide(content))

    for i, section in enumerate(content.sections):
        parts.append("---\n")
        if i > 0 and i % 4 == 0:
            parts.append("<!-- _class: divider -->\n")
            parts.append(f"# {section.heading}\n")
            parts.append("---\n")
        parts.append(_render_section_slide(section))

        if native_slides and i < len(native_slides):
            ns = native_slides[i]
            if ns.image_path:
                parts.append("---\n")
                parts.append(_render_native_slide(ns, base_dir=base_dir))

    if native_slides:
        for ns in native_slides[len(content.sections) :]:
            if ns.image_path:
                parts.append("---\n")
                parts.append(_render_native_slide(ns, base_dir=base_dir))

    parts.append("---\n")
    parts.append(_render_conclusion_slide(content))
    parts.append("---\n")
    parts.append("<!-- _class: lead -->\n")
    parts.append("# Thank You\n")
    parts.append("Questions & Discussion\n")

    return "\n".join(parts)


# ─── Export Helpers ─────────────────────────────────────────────────────────


def export_marp(
    marp_path: str | Path,
    fmt: str = "pdf",
    theme_css: Path | str | None = None,
) -> str:
    """Export Marp markdown to PDF, HTML, or PPTX using marp-cli.

    Args:
        marp_path: Path to the .md file.
        fmt: Export format ('pdf', 'html', or 'pptx').
        theme_css: Optional custom CSS theme file.

    Returns:
        The generated output file path.
    """
    marp_cmd = shutil.which("marp")
    if not marp_cmd:
        raise RuntimeError(
            "marp-cli executable not found in PATH.\n"
            "Install standalone binary or via npm:\n"
            "  npm install -g @marp-team/marp-cli\n"
            "  or download from https://github.com/marp-team/marp-cli/releases"
        )

    ext_map = {"pdf": ".pdf", "html": ".html", "pptx": ".pptx"}
    ext = ext_map.get(fmt, f".{fmt}")
    marp_file = Path(marp_path)
    output_path = str(marp_file.with_suffix(ext))

    cmd = [marp_cmd, str(marp_file), "-o", output_path, "--allow-local-files"]
    if fmt in ("pdf", "html", "pptx"):
        cmd.append(f"--{fmt}")

    theme_path = Path(theme_css) if theme_css else None
    if theme_path and theme_path.exists():
        cmd.extend(["--theme", str(theme_path)])

    logger.info("Running marp-cli export: %s", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_path


# ─── High-Level Presenter Pipeline ──────────────────────────────────────────


class MarpPresenter:
    """High-level converter from documents and URLs to Marp presentations."""

    def __init__(
        self,
        *,
        theme: str = DEFAULT_MARP_THEME,
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
        use_native: bool = False,
        export_format: str | None = None,
        keep_notebook: bool = False,
        instructions: str = "",
        theme_css: str | Path | None = None,
    ) -> MarpResult:
        """Run the complete generation pipeline.

        1. Creates temporary NotebookLM notebook.
        2. Adds sources (URLs, local files, text).
        3. Extracts structured slide content with chat LLM.
        4. Optionally generates native Google slide deck and extracts images.
        5. Renders Marp Markdown with Katex, Mermaid, and embedded images.
        6. Optionally exports to PDF / HTML / PPTX via marp-cli.
        """
        result = MarpResult(marp_path=output_path)

        async with NotebookLMClient.from_storage() as client:
            nb = await client.notebooks.create(
                f"Presentation: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            result.notebook_id = nb.id
            logger.info("Created temporary notebook: %s", nb.id)

            try:
                source_ids: list[str] = []

                # Add URL sources
                for url in urls or []:
                    src = await client.sources.add_url(nb.id, url)
                    source_ids.append(src.id)

                # Add file sources
                for fpath in files or []:
                    p = Path(fpath)
                    if not p.exists():
                        raise FileNotFoundError(f"File not found: {fpath}")
                    if p.suffix.lower() in (".md", ".txt", ".markdown"):
                        src = await client.sources.add_text(
                            nb.id, p.name, p.read_text(encoding="utf-8")
                        )
                    else:
                        src = await client.sources.add_file(nb.id, str(p))
                    source_ids.append(src.id)

                # Add text sources
                for i, text in enumerate(texts or []):
                    src = await client.sources.add_text(nb.id, f"Text source {i + 1}", text)
                    source_ids.append(src.id)

                # Wait for sources to be parsed and ready
                for sid in source_ids:
                    await client.sources.wait_until_ready(nb.id, sid, timeout=600)
                logger.info("All %d sources ready", len(source_ids))

                # Extract structured slide content
                content = await extract_slide_content(
                    client,
                    nb.id,
                    max_slides=self.max_slides,
                    instructions=instructions,
                )

                # Generate native Google slide deck if requested
                native_slide_data: list[NativeSlideData] | None = None
                if native_slides_path or use_native:
                    logger.info("Generating Google native slide deck...")
                    status = await client.artifacts.generate_slide_deck(
                        nb.id,
                        source_ids=source_ids,
                        language=self.language,
                        instructions=instructions or None,
                    )
                    final = await client.artifacts.wait_for_completion(
                        nb.id,
                        status.task_id,
                        timeout=900,
                    )
                    if final.is_complete:
                        if native_slides_path:
                            dl = await client.artifacts.download_slide_deck(
                                nb.id,
                                native_slides_path,
                                artifact_id=status.task_id,
                            )
                            result.native_path = dl
                            logger.info("Downloaded native deck to %s", dl)

                        if use_native:
                            out_dir = Path(output_path).resolve().parent / "slide_images"
                            native_slide_data = await extract_native_slide_images(
                                client,
                                nb.id,
                                status.task_id,
                                out_dir,
                            )
                            result.native_slides = native_slide_data
                            result.images_dir = str(out_dir)
                    else:
                        logger.warning("Native deck generation status: %s", final.status)

                # Render Marp Markdown
                out_p = Path(output_path).resolve()
                marp_md = render_marp_markdown(
                    content,
                    theme=self.theme,
                    native_slides=native_slide_data,
                    base_dir=out_p.parent,
                )
                out_p.parent.mkdir(parents=True, exist_ok=True)
                out_p.write_text(marp_md, encoding="utf-8")
                result.marp_path = str(out_p)
                logger.info("Wrote Marp presentation to %s", result.marp_path)

                # Export to PDF / HTML / PPTX
                if export_format:
                    result.export_path = export_marp(
                        out_p,
                        fmt=export_format,
                        theme_css=theme_css,
                    )
                    logger.info("Exported to %s", result.export_path)

            finally:
                if not keep_notebook and result.notebook_id:
                    await client.notebooks.delete(nb.id)
                    logger.info("Cleaned up temporary notebook %s", nb.id)

        return result


# Backwards compatibility alias
ArticleToMarp = MarpPresenter


async def generate_presentation(
    *,
    urls: list[str] | None = None,
    files: list[str] | None = None,
    texts: list[str] | None = None,
    output: str = "slides.md",
    use_native: bool = False,
    native_slides_path: str | None = None,
    export_format: str | None = None,
    theme: str = DEFAULT_MARP_THEME,
    max_slides: int = 15,
    language: str = "en",
    keep_notebook: bool = False,
    instructions: str = "",
    theme_css: str | Path | None = None,
) -> MarpResult:
    """Convenience function to generate a presentation from articles/URLs in one call."""
    presenter = MarpPresenter(
        theme=theme,
        max_slides=max_slides,
        language=language,
    )
    return await presenter.generate(
        urls=urls,
        files=files,
        texts=texts,
        output_path=output,
        use_native=use_native,
        native_slides_path=native_slides_path,
        export_format=export_format,
        keep_notebook=keep_notebook,
        instructions=instructions,
        theme_css=theme_css,
    )
