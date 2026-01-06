# Page Layouts Implementation Plan

## Current Problem
The current export functionality only writes plain `.txt` files with no formatting whatsoever. The `export_txt()` function in `app/app.py:124-133` simply dumps text content - no styling, no structure.

## What You Want
1. **Justified text** on all pages
2. **Paragraph separation** (proper spacing between paragraphs)
3. **Page numbers** on the right side
4. **Book title** on first pages
5. **Layout changes that actually affect the output**

---

## Implementation Plan

### Step 1: Add Required Dependencies
Add to `pyproject.toml`:
- `weasyprint` or `reportlab` - For PDF generation with full layout control
- `jinja2` - For HTML templates

### Step 2: Create Document Layout Module
New file: `app/layouts.py`

This module will define layout presets with these configurable options:
```python
@dataclass
class PageLayout:
    name: str
    # Page dimensions
    page_size: str = "A4"  # A4, Letter, etc.
    margins: dict  # top, bottom, left, right in mm

    # Text formatting
    text_align: str = "justify"  # left, right, center, justify
    font_family: str = "serif"
    font_size: int = 12
    line_height: float = 1.5

    # Paragraph settings
    paragraph_spacing: int = 12  # points after each paragraph
    first_line_indent: int = 0   # optional indent

    # Header/Footer
    show_page_numbers: bool = True
    page_number_position: str = "right"  # left, center, right

    # Title page
    show_title_page: bool = True
    book_title: str = ""
    author: str = ""
```

### Step 3: Define Layout Presets
Create ready-to-use layouts:

| Layout Name | Description |
|-------------|-------------|
| **Book** | Traditional book layout with title page, justified text, right-aligned page numbers |
| **Report** | Professional report format with headers, centered page numbers |
| **Manuscript** | Double-spaced, monospace font, left-aligned for editing |
| **Article** | Single column, clean formatting for articles |
| **Plain** | Simple layout, no page numbers, minimal formatting |

### Step 4: Create HTML/CSS Templates
New folder: `app/templates/`

For each layout, create templates like:
```
app/templates/
├── base.html           # Base template structure
├── book.html           # Book-specific template
├── book.css            # Book styling
├── report.html
├── report.css
└── ...
```

Example `book.css`:
```css
@page {
    size: A4;
    margin: 25mm 20mm 25mm 25mm;

    @bottom-right {
        content: counter(page);
        font-size: 10pt;
    }
}

body {
    text-align: justify;
    font-family: "Georgia", serif;
    font-size: 12pt;
    line-height: 1.6;
}

p {
    margin-bottom: 12pt;
    text-indent: 0;
}

.title-page {
    page-break-after: always;
    text-align: center;
    padding-top: 40%;
}

.title-page h1 {
    font-size: 28pt;
    margin-bottom: 24pt;
}
```

### Step 5: Create PDF Export Function
New function in `app/layouts.py`:

```python
def export_formatted_pdf(
    content: str,
    layout: PageLayout,
    book_title: str = "",
    author: str = "",
    output_path: str = None
) -> str:
    """
    Export translated text to a properly formatted PDF.

    1. Parse content into paragraphs
    2. Apply layout template
    3. Render to PDF using WeasyPrint
    4. Return file path
    """
```

### Step 6: Update the UI (app/app.py)

Add layout controls in the sidebar under "Advanced Options":

```python
with gr.Accordion("Page Layout", open=False):
    layout_preset = gr.Dropdown(
        label="Layout Style",
        choices=["Book", "Report", "Manuscript", "Article", "Plain"],
        value="Book"
    )
    book_title_input = gr.Textbox(
        label="Book/Document Title",
        placeholder="Enter title for title page"
    )
    author_input = gr.Textbox(
        label="Author",
        placeholder="Optional author name"
    )
    export_format = gr.Radio(
        label="Export Format",
        choices=["PDF", "DOCX", "HTML", "TXT"],
        value="PDF"
    )
```

### Step 7: Wire Up Export Button
Modify `export_txt()` → `export_document()`:

```python
def export_document(content, layout_name, title, author, format):
    layout = get_layout_preset(layout_name)

    if format == "PDF":
        return export_formatted_pdf(content, layout, title, author)
    elif format == "DOCX":
        return export_formatted_docx(content, layout, title, author)
    elif format == "HTML":
        return export_formatted_html(content, layout, title, author)
    else:
        return export_txt(content)
```

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Modify | Add weasyprint, jinja2 dependencies |
| `app/layouts.py` | **Create** | Layout classes and export functions |
| `app/templates/base.html` | **Create** | Base HTML template |
| `app/templates/book.css` | **Create** | Book layout CSS with page styles |
| `app/templates/report.css` | **Create** | Report layout CSS |
| `app/templates/manuscript.css` | **Create** | Manuscript layout CSS |
| `app/templates/article.css` | **Create** | Article layout CSS |
| `app/app.py` | Modify | Add layout UI controls, update export |
| `app/process.py` | Modify | Import new layout functions |

---

## Detailed Feature Specification

### 1. Justified Text
- CSS `text-align: justify` applied to body text
- Optional hyphenation for better justification

### 2. Paragraph Separation
- Each `\n\n` in source becomes a `<p>` tag
- CSS `margin-bottom: 12pt` on paragraphs
- No first-line indent by default (configurable)

### 3. Page Numbers (Right Side)
- Using CSS `@page` rules with `@bottom-right` region
- Format: just the number, or "Page X of Y"
- Not shown on title page

### 4. Title Page (First Page)
- Centered book title in large font
- Optional author name below
- Page break after title page
- No page number on title page

---

## Implementation Order

1. Add dependencies to pyproject.toml
2. Create `app/layouts.py` with `PageLayout` dataclass
3. Create layout presets (Book, Report, etc.)
4. Create `app/templates/` folder with HTML/CSS templates
5. Implement `export_formatted_pdf()` function
6. Add UI controls to `app/app.py`
7. Connect export button to new export function
8. Test with sample translations

---

## Questions to Clarify Before Implementation

1. **Page size preference?** A4 (European) or Letter (US)?
2. **Font preference?** Serif (Georgia/Times) or Sans-serif (Arial)?
3. **Do you want both PDF and DOCX export, or PDF only?**
4. **Should the original source text be included alongside translation?** (bilingual layout option)
