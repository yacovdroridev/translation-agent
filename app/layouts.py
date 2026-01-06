"""
Page layout configuration and PDF export functionality.

This module provides layout presets and PDF generation for translated documents.
"""

import os
from dataclasses import dataclass, field
from glob import glob
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


@dataclass
class PageLayout:
    """Configuration for document page layout."""

    name: str
    display_name: str

    # Page dimensions
    page_size: str = "A4"
    margin_top: str = "25mm"
    margin_bottom: str = "25mm"
    margin_left: str = "25mm"
    margin_right: str = "20mm"

    # Text formatting
    text_align: str = "justify"
    font_family: str = '"Georgia", "Times New Roman", serif'
    font_size: str = "12pt"
    line_height: float = 1.6

    # Paragraph settings
    paragraph_spacing: str = "12pt"
    first_line_indent: str = "0"

    # Header/Footer
    show_page_numbers: bool = True
    page_number_position: str = "right"  # left, center, right

    # Title page
    show_title_page: bool = True

    def get_page_number_css(self) -> str:
        """Generate CSS for page number positioning."""
        if not self.show_page_numbers:
            return ""

        position_map = {
            "left": "@bottom-left",
            "center": "@bottom-center",
            "right": "@bottom-right",
        }
        position = position_map.get(self.page_number_position, "@bottom-right")

        return f"""
        {position} {{
            content: counter(page);
            font-family: {self.font_family};
            font-size: 10pt;
        }}
        """


# Pre-defined layout presets
LAYOUT_PRESETS: dict[str, PageLayout] = {
    "book": PageLayout(
        name="book",
        display_name="Book",
        page_size="A4",
        margin_top="30mm",
        margin_bottom="25mm",
        margin_left="30mm",
        margin_right="20mm",
        text_align="justify",
        font_family='"Georgia", "Times New Roman", serif',
        font_size="12pt",
        line_height=1.6,
        paragraph_spacing="12pt",
        first_line_indent="0",
        show_page_numbers=True,
        page_number_position="right",
        show_title_page=True,
    ),
    "report": PageLayout(
        name="report",
        display_name="Report",
        page_size="A4",
        margin_top="25mm",
        margin_bottom="25mm",
        margin_left="25mm",
        margin_right="25mm",
        text_align="justify",
        font_family='"Arial", "Helvetica", sans-serif',
        font_size="11pt",
        line_height=1.5,
        paragraph_spacing="10pt",
        first_line_indent="0",
        show_page_numbers=True,
        page_number_position="center",
        show_title_page=True,
    ),
    "manuscript": PageLayout(
        name="manuscript",
        display_name="Manuscript",
        page_size="A4",
        margin_top="25mm",
        margin_bottom="25mm",
        margin_left="30mm",
        margin_right="30mm",
        text_align="left",
        font_family='"Courier New", "Courier", monospace',
        font_size="12pt",
        line_height=2.0,
        paragraph_spacing="24pt",
        first_line_indent="0",
        show_page_numbers=True,
        page_number_position="right",
        show_title_page=True,
    ),
    "article": PageLayout(
        name="article",
        display_name="Article",
        page_size="A4",
        margin_top="20mm",
        margin_bottom="20mm",
        margin_left="20mm",
        margin_right="20mm",
        text_align="justify",
        font_family='"Georgia", "Times New Roman", serif',
        font_size="11pt",
        line_height=1.5,
        paragraph_spacing="10pt",
        first_line_indent="0",
        show_page_numbers=True,
        page_number_position="center",
        show_title_page=False,
    ),
    "plain": PageLayout(
        name="plain",
        display_name="Plain",
        page_size="A4",
        margin_top="20mm",
        margin_bottom="20mm",
        margin_left="20mm",
        margin_right="20mm",
        text_align="left",
        font_family='"Arial", "Helvetica", sans-serif',
        font_size="12pt",
        line_height=1.4,
        paragraph_spacing="8pt",
        first_line_indent="0",
        show_page_numbers=False,
        page_number_position="right",
        show_title_page=False,
    ),
}


def get_layout_choices() -> list[str]:
    """Return list of layout display names for UI dropdown."""
    return [preset.display_name for preset in LAYOUT_PRESETS.values()]


def get_layout_by_name(display_name: str) -> PageLayout:
    """Get layout preset by display name."""
    for preset in LAYOUT_PRESETS.values():
        if preset.display_name == display_name:
            return preset
    return LAYOUT_PRESETS["book"]  # Default fallback


def text_to_paragraphs(text: str) -> list[str]:
    """Convert text with newlines to list of paragraphs."""
    # Split on double newlines (paragraph breaks)
    paragraphs = text.split("\n\n")
    # Clean up and filter empty paragraphs
    paragraphs = [p.strip().replace("\n", " ") for p in paragraphs if p.strip()]
    return paragraphs


def generate_document_html(
    content: str,
    layout: PageLayout,
    title: str = "",
    author: str = "",
) -> str:
    """Generate HTML document with embedded CSS for the given layout."""

    paragraphs = text_to_paragraphs(content)

    # Build the CSS
    page_number_css = layout.get_page_number_css()

    css = f"""
    @page {{
        size: {layout.page_size};
        margin: {layout.margin_top} {layout.margin_right} {layout.margin_bottom} {layout.margin_left};
        {page_number_css}
    }}

    @page title-page {{
        {page_number_css.replace("content: counter(page);", "content: none;")}
    }}

    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        font-family: {layout.font_family};
        font-size: {layout.font_size};
        line-height: {layout.line_height};
        text-align: {layout.text_align};
        color: #000;
        -webkit-hyphens: auto;
        hyphens: auto;
    }}

    .title-page {{
        page: title-page;
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        text-align: center;
    }}

    .title-page h1 {{
        font-size: 28pt;
        font-weight: bold;
        margin-bottom: 24pt;
        text-align: center;
    }}

    .title-page .author {{
        font-size: 16pt;
        font-style: italic;
        margin-top: 12pt;
        text-align: center;
    }}

    .content {{
        text-align: {layout.text_align};
    }}

    .content p {{
        margin-bottom: {layout.paragraph_spacing};
        text-indent: {layout.first_line_indent};
        text-align: {layout.text_align};
        orphans: 2;
        widows: 2;
    }}

    .content p:last-child {{
        margin-bottom: 0;
    }}
    """

    # Build HTML structure
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="UTF-8">',
        f"<title>{title or 'Document'}</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body>",
    ]

    # Add title page if enabled and title is provided
    if layout.show_title_page and title:
        html_parts.append('<div class="title-page">')
        html_parts.append(f"<h1>{title}</h1>")
        if author:
            html_parts.append(f'<div class="author">{author}</div>')
        html_parts.append("</div>")

    # Add content
    html_parts.append('<div class="content">')
    for para in paragraphs:
        html_parts.append(f"<p>{para}</p>")
    html_parts.append("</div>")

    html_parts.extend(["</body>", "</html>"])

    return "\n".join(html_parts)


def export_formatted_pdf(
    content: str,
    layout_name: str = "Book",
    title: str = "",
    author: str = "",
    output_dir: str = "outputs",
) -> str:
    """
    Export translated text to a properly formatted PDF.

    Args:
        content: The translated text content
        layout_name: Name of the layout preset to use
        title: Optional document/book title for title page
        author: Optional author name for title page
        output_dir: Directory to save the PDF

    Returns:
        Path to the generated PDF file
    """
    # Get layout configuration
    layout = get_layout_by_name(layout_name)

    # Generate HTML with embedded CSS
    html_content = generate_document_html(content, layout, title, author)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename
    existing_files = glob(os.path.join(output_dir, "*.pdf"))
    file_count = len(existing_files)
    file_path = os.path.join(output_dir, f"{file_count:06d}.pdf")

    # Generate PDF using WeasyPrint
    html_doc = HTML(string=html_content)
    html_doc.write_pdf(file_path)

    return file_path


def export_formatted_html(
    content: str,
    layout_name: str = "Book",
    title: str = "",
    author: str = "",
    output_dir: str = "outputs",
) -> str:
    """
    Export translated text to a formatted HTML file.

    Args:
        content: The translated text content
        layout_name: Name of the layout preset to use
        title: Optional document/book title
        author: Optional author name
        output_dir: Directory to save the HTML

    Returns:
        Path to the generated HTML file
    """
    # Get layout configuration
    layout = get_layout_by_name(layout_name)

    # Generate HTML with embedded CSS
    html_content = generate_document_html(content, layout, title, author)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename
    existing_files = glob(os.path.join(output_dir, "*.html"))
    file_count = len(existing_files)
    file_path = os.path.join(output_dir, f"{file_count:06d}.html")

    # Write HTML file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return file_path
