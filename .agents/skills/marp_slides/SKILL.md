---
name: marp-slides
description: >-
  Generate presentation-ready Marp Markdown slide decks from articles and URLs
  using notebooklm-py. Feeds articles into NotebookLM for grounded content
  extraction, then produces Marp-flavored Markdown with mermaid diagrams,
  speaker notes, a custom CSS theme, and optional PDF/HTML export. Also
  generates the native NotebookLM slide deck for side-by-side comparison.
  Activate when the user wants to turn articles, URLs, or text into
  presentations, slides, or decks.
---

# Marp Slides from Articles

Generate polished Marp Markdown presentations from articles by leveraging
notebooklm-py for grounded content extraction and structured summarisation.

## Prerequisites

```bash
pip install "notebooklm-py[browser]"
notebooklm auth check --test --json   # must return status == "ok"
```

Optional for PDF/HTML export:

```bash
npm install -g @marp-team/marp-cli
```

## Workflow

### 1. Run the Script

Use the main generation script at
[`scripts/article_to_marp.py`](file:///home/ajf/AI_tools/notebooklm-py/.agents/skills/marp_slides/scripts/article_to_marp.py):

```bash
# Single article
python .agents/skills/marp_slides/scripts/article_to_marp.py \
  --url "https://example.com/article" \
  --output slides.md

# Multiple articles
python .agents/skills/marp_slides/scripts/article_to_marp.py \
  --url "https://example.com/a1" \
  --url "https://example.com/a2" \
  --output slides.md

# With native NotebookLM slide deck comparison
python .agents/skills/marp_slides/scripts/article_to_marp.py \
  --url "https://example.com/article" \
  --output slides.md \
  --native-slides ./native_deck.pdf

# Custom theme
python .agents/skills/marp_slides/scripts/article_to_marp.py \
  --url "https://example.com/article" \
  --output slides.md \
  --theme dark

# Export to PDF/HTML (requires marp-cli)
python .agents/skills/marp_slides/scripts/article_to_marp.py \
  --url "https://example.com/article" \
  --output slides.md \
  --export pdf
```

### 2. Use as a Python Library

```python
import asyncio
from article_to_marp import ArticleToMarp

async def main():
    converter = ArticleToMarp(theme="dark")
    result = await converter.generate(
        urls=["https://example.com/article"],
        output_path="slides.md",
        native_slides_path="native.pdf",  # optional comparison
        export_format="pdf",               # optional export
    )
    print(f"Marp slides: {result.marp_path}")
    print(f"Native deck: {result.native_path}")

asyncio.run(main())
```

### 3. Programmatic Use from notebooklm-py

```python
import asyncio
from notebooklm import NotebookLMClient

# The skill's core module can be imported directly
import sys; sys.path.insert(0, ".agents/skills/marp_slides/scripts")
from article_to_marp import extract_slide_content, render_marp

async def main():
    async with NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create("Presentation: Topic")
        source = await client.sources.add_url(nb.id, "https://example.com")
        await client.sources.wait_until_ready(nb.id, source.id, timeout=600)

        # Extract structured content via grounded chat
        content = await extract_slide_content(client, nb.id)

        # Render to Marp markdown
        marp_md = render_marp(content, theme="dark")
        with open("slides.md", "w") as f:
            f.write(marp_md)

asyncio.run(main())
```

## Output Features

The generated Marp Markdown includes:

- **Title slide** with article title, subtitle, and date
- **Section divider slides** with gradient backgrounds
- **Content slides** with structured bullet points and speaker notes
- **Code blocks** with syntax highlighting (when articles contain code)
- **Mermaid diagrams** for relationships, flows, and architectures
- **Tables** for comparative or structured data
- **Multi-column layouts** using Marp's `<!-- split -->` directives
- **Custom CSS theme** (light/dark) with Inter font and smooth gradients

## Themes

Two built-in themes ship with this skill:

| Theme   | Description                                                |
|---------|------------------------------------------------------------|
| `light` | Clean white background, dark text, blue accent gradients   |
| `dark`  | Deep slate background, light text, cyan/purple gradients   |

Theme CSS is at
[`scripts/themes/`](file:///home/ajf/AI_tools/notebooklm-py/.agents/skills/marp_slides/scripts/themes/).

## Flags Reference

| Flag               | Default       | Description                              |
|--------------------|---------------|------------------------------------------|
| `--url`            | *(required)*  | Article URL(s), repeatable               |
| `--text`           |               | Inline text source instead of URL        |
| `--output`         | `slides.md`   | Output Marp Markdown path                |
| `--theme`          | `dark`        | Theme name: `light` or `dark`            |
| `--language`       | `en`          | Slide language                           |
| `--max-slides`     | `15`          | Maximum number of content slides         |
| `--native-slides`  |               | Also generate native NotebookLM deck     |
| `--export`         |               | Export format: `pdf`, `html`, or `pptx`  |
| `--keep-notebook`  | `false`       | Don't delete the notebook after          |
| `--instructions`   |               | Extra instructions for content focus     |

## Authorization Notes

This skill creates a temporary notebook, adds sources, chats, and optionally
generates a native slide deck. Per the notebooklm skill's authorization
boundaries, a user request to "generate slides from this article" authorizes
the full workflow including notebook creation, source addition, chat, native
generation, and download. The notebook is deleted at the end unless
`--keep-notebook` is passed.
