"""Unit tests for the notebooklm.marp presentation module."""

import json
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from click.testing import CliRunner

from notebooklm import (
    NativeSlideData,
    SlideContent,
    SlideSection,
    export_marp,
    extract_slide_content,
    render_marp_markdown,
)
from notebooklm.cli.marp_cmd import marp as marp_cli
from notebooklm.marp import _clean_json


def test_clean_json_markdown_block():
    raw = 'Here is the plan:\n```json\n{"title": "Test Title", "sections": []}\n```\nHope it helps!'
    assert _clean_json(raw) == '{"title": "Test Title", "sections": []}'


def test_clean_json_raw_object():
    raw = '{"title": "Raw Title", "sections": []}'
    assert _clean_json(raw) == '{"title": "Raw Title", "sections": []}'


def test_clean_json_whitespace():
    raw = '  \n{"title": "Spaced"} \n '
    assert _clean_json(raw) == '{"title": "Spaced"}'


def test_render_marp_markdown_basic():
    content = SlideContent(
        title="Introduction to AI",
        subtitle="Foundations & Vision",
        authors="DeepMind",
        sections=[
            SlideSection(
                heading="Model Predictive Control",
                bullets=["Dynamic environments", "State constraints"],
                speaker_notes="Presenter notes go here.",
                code_block={"language": "python", "code": "def solve(): return 42"},
                mermaid_diagram="flowchart LR\n    A --> B",
                table={
                    "headers": ["Algorithm", "Speed"],
                    "rows": [["MPC", "100Hz"], ["PAC-MPC", "120Hz"]],
                    "caption": "Performance Benchmark",
                },
            )
        ],
        conclusion_bullets=["Safety first", "Optimal efficiency"],
        keywords=["MPC", "Control"],
    )

    md = render_marp_markdown(content, theme="marp-dark")
    assert "marp: true" in md
    assert "theme: marp-dark" in md
    assert "# Introduction to AI" in md
    assert "## Foundations & Vision" in md
    assert "DeepMind" in md
    assert "# Model Predictive Control" in md
    assert "- Dynamic environments" in md
    assert "```python" in md
    assert "def solve(): return 42" in md
    assert "```mermaid" in md
    assert "flowchart LR" in md
    assert "| Algorithm | Speed |" in md
    assert "| MPC | 100Hz |" in md
    assert "*Performance Benchmark*" in md
    assert "Presenter notes go here." in md
    assert "# Summary & Key Takeaways" in md
    assert "- Safety first" in md
    assert "**Keywords**: MPC, Control" in md


def test_render_marp_markdown_with_native_slides(tmp_path: Path):
    base_dir = tmp_path
    img_file = base_dir / "slide_images" / "slide_01.png"
    img_file.parent.mkdir(parents=True)
    img_file.write_bytes(b"dummy image")

    content = SlideContent(
        title="Vision Paper",
        sections=[
            SlideSection(heading="Section 1", bullets=["Point A"]),
        ],
    )
    native_slides = [
        NativeSlideData(
            index=0,
            image_path=str(img_file),
            alt_text="Visual Slide 1",
            text="High-level architecture overview.",
        )
    ]

    md = render_marp_markdown(content, native_slides=native_slides, base_dir=base_dir)
    assert "![bg contain](slide_images/slide_01.png)" in md
    assert "High-level architecture overview." in md


@pytest.mark.asyncio
async def test_extract_slide_content_success():
    client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.answer = json.dumps(
        {
            "title": "Extracted Title",
            "subtitle": "Extracted Subtitle",
            "authors": "Author Name",
            "sections": [
                {
                    "heading": "Core Theorem",
                    "bullets": ["Bullet 1", "Bullet 2"],
                    "speaker_notes": "Notes context",
                }
            ],
            "conclusion_bullets": ["Final thought"],
            "keywords": ["AI"],
        }
    )
    client.chat.ask = AsyncMock(return_value=mock_resp)

    content = await extract_slide_content(client, "fake-notebook-id")
    assert content.title == "Extracted Title"
    assert content.subtitle == "Extracted Subtitle"
    assert len(content.sections) == 1
    assert content.sections[0].heading == "Core Theorem"
    assert content.sections[0].bullets == ["Bullet 1", "Bullet 2"]


@pytest.mark.asyncio
async def test_extract_slide_content_fallback():
    client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.answer = "Not a JSON document. Just a paragraph describing the article."
    client.chat.ask = AsyncMock(return_value=mock_resp)

    content = await extract_slide_content(client, "fake-notebook-id")
    assert content.title == "Overview"
    assert len(content.sections) >= 1


def test_export_marp_missing_binary(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    with pytest.raises(RuntimeError, match="marp-cli executable not found"):
        export_marp("dummy.md", fmt="pdf")


def test_cli_marp_help():
    runner = CliRunner()
    result = runner.invoke(marp_cli, ["--help"])
    assert result.exit_code == 0
    assert "Generate Marp presentations" in result.output


def test_cli_marp_generate_no_sources():
    runner = CliRunner()
    result = runner.invoke(marp_cli, ["generate"])
    assert result.exit_code == 1
    assert "Provide at least one --file, --url, or --text" in result.output
