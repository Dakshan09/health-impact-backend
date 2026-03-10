"""
PDF Compiler
Converts Markdown health reports to properly formatted PDF files.
Supports Markdown tables (pipe-delimited rows) rendered as reportlab Tables.
"""

import os
import re
from datetime import datetime


def compile_pdf(markdown_content: str, output_path: str) -> str:
    """
    Compile a health report from Markdown content to PDF.
    Uses reportlab if available, falls back to saving HTML/text.

    Args:
        markdown_content: Markdown report string
        output_path: Output path for the PDF file

    Returns:
        Absolute path to the generated file
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Try reportlab first
    try:
        return _compile_with_reportlab(markdown_content, output_path)
    except ImportError:
        pass

    # Try markdown + weasyprint
    try:
        return _compile_with_weasyprint(markdown_content, output_path)
    except ImportError:
        pass

    # Fallback: save as HTML with PDF-like styling
    html_path = output_path.replace(".pdf", ".html")
    _save_as_html(markdown_content, html_path)
    print("[WARN] PDF libraries not installed. Saved as HTML: " + html_path)
    print("    To enable PDF output, run: pip install reportlab")
    return html_path


# ─── Reportlab compiler ──────────────────────────────────────────────────────

def _compile_with_reportlab(markdown_content: str, output_path: str) -> str:
    """Compile PDF using reportlab with full table support."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors

    TEAL_DARK   = colors.HexColor("#0D3B3E")
    TEAL_MED    = colors.HexColor("#0D7377")
    TEAL_LIGHT  = colors.HexColor("#14919B")
    GREY_BG     = colors.HexColor("#F5F5F5")
    WHITE       = colors.white

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ─────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "HealthTitle",
        parent=styles["Title"],
        textColor=TEAL_DARK,
        fontSize=22,
        spaceAfter=6,
        alignment=1,  # center
    )
    h2_style = ParagraphStyle(
        "HealthH2",
        parent=styles["Heading2"],
        textColor=WHITE,
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
        backColor=TEAL_DARK,
        borderPadding=(6, 8, 6, 8),
        leading=18,
    )
    h3_style = ParagraphStyle(
        "HealthH3",
        parent=styles["Heading3"],
        textColor=TEAL_MED,
        fontSize=11,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "HealthBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        spaceAfter=4,
    )
    bold_style = ParagraphStyle(
        "HealthBold",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=10,
        spaceAfter=2,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.gray,
        leading=10,
        spaceBefore=6,
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=WHITE,
        fontName="Helvetica-Bold",
    )

    story = []

    # ── Parse lines, accumulating table rows ──────────────────────────────
    lines = markdown_content.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # ── Markdown table detection ──────────────────────────────────
        if "|" in stripped and stripped.startswith("|"):
            table_rows = []
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip().startswith("|"):
                row_text = lines[i].strip()
                # Skip separator rows (|---|---|)
                if re.match(r"^\|[\s\-:|]+\|$", row_text):
                    i += 1
                    continue
                cells = [c.strip() for c in row_text.split("|")[1:-1]]
                table_rows.append(cells)
                i += 1

            if table_rows:
                story.append(_build_reportlab_table(
                    table_rows, table_cell_style, table_header_style,
                    TEAL_DARK, TEAL_LIGHT, GREY_BG, WHITE
                ))
                story.append(Spacer(1, 6))
            continue

        # ── Other Markdown elements ───────────────────────────────────
        if not stripped:
            story.append(Spacer(1, 4))
        elif stripped == "---":
            story.append(HRFlowable(
                width="100%", thickness=1,
                color=colors.HexColor("#CCCCCC"), spaceAfter=6, spaceBefore=6
            ))
        elif stripped.startswith("# "):
            story.append(Paragraph(stripped[2:], title_style))
        elif stripped.startswith("## "):
            story.append(Paragraph(stripped[3:], h2_style))
        elif stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], h3_style))
        elif stripped.startswith("> "):
            text = stripped[2:]
            story.append(Paragraph(f"<i>{text}</i>", disclaimer_style))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = f"\u2022 {stripped[2:]}"
            story.append(Paragraph(bullet_text, body_style))
        elif stripped.startswith("**") and stripped.endswith("**"):
            story.append(Paragraph(stripped[2:-2], bold_style))
        elif stripped.startswith("**"):
            text = _inline_bold(stripped)
            story.append(Paragraph(text, bold_style))
        elif stripped.startswith("DISCLAIMER:") or stripped.startswith("Generated by"):
            story.append(Paragraph(stripped, disclaimer_style))
        else:
            text = _inline_bold(stripped)
            story.append(Paragraph(text, body_style))

        i += 1

    doc.build(story)
    print("[OK] PDF report saved to: " + output_path)
    return output_path


def _inline_bold(text: str) -> str:
    """Convert **bold** markers to <b>bold</b> tags."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def _build_reportlab_table(rows, cell_style, header_style, teal_dark, teal_light, grey_bg, white):
    """Build a styled reportlab Table from parsed rows."""
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.lib import colors

    if not rows:
        return Table([[""]])

    num_cols = max(len(r) for r in rows)

    # Normalise column count
    normalised = []
    for r in rows:
        while len(r) < num_cols:
            r.append("")
        normalised.append(r)

    # First row = header
    header = normalised[0]
    data_rows = normalised[1:]

    table_data = []
    # Header row
    table_data.append([Paragraph(c, header_style) for c in header])
    # Data rows
    for r in data_rows:
        table_data.append([Paragraph(c, cell_style) for c in r])

    # Calculate col widths proportionally
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    available = A4[0] - 3 * cm  # page width minus margins
    col_width = available / num_cols
    col_widths = [col_width] * num_cols

    t = Table(table_data, colWidths=col_widths, repeatRows=1)

    style_commands = [
        # Header styling
        ("BACKGROUND",    (0, 0), (-1, 0), teal_dark),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING",    (0, 0), (-1, 0), 6),
        # Data row styling
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        # Grid
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]

    # Alternating row colours
    for row_idx in range(1, len(table_data)):
        if row_idx % 2 == 0:
            style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), grey_bg))

    t.setStyle(TableStyle(style_commands))
    return t


# ─── Weasyprint compiler ─────────────────────────────────────────────────────

def _compile_with_weasyprint(markdown_content: str, output_path: str) -> str:
    """Compile PDF using weasyprint."""
    import markdown
    from weasyprint import HTML

    html_content = _markdown_to_html_content(markdown_content)
    HTML(string=html_content).write_pdf(output_path)
    print("[OK] PDF report saved to: " + output_path)
    return output_path


def _save_as_html(markdown_content: str, output_path: str) -> str:
    """Save report as HTML file."""
    html_content = _markdown_to_html_content(markdown_content)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path


def _markdown_to_html_content(markdown_text: str) -> str:
    """Convert markdown to full HTML page with table support."""
    lines = markdown_text.split("\n")
    body_html = ""
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Table handling
        if "|" in stripped and stripped.startswith("|"):
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue  # skip separator
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                body_html += "<table><thead><tr>"
                body_html += "".join(f"<th>{c}</th>" for c in cells)
                body_html += "</tr></thead><tbody>"
            else:
                body_html += "<tr>"
                body_html += "".join(f"<td>{c}</td>" for c in cells)
                body_html += "</tr>"
            continue
        else:
            if in_table:
                body_html += "</tbody></table>"
                in_table = False

        if not stripped:
            body_html += "<br/>"
        elif stripped == "---":
            body_html += "<hr/>"
        elif stripped.startswith("# "):
            body_html += f"<h1>{stripped[2:]}</h1>"
        elif stripped.startswith("## "):
            body_html += f"<h2>{stripped[3:]}</h2>"
        elif stripped.startswith("### "):
            body_html += f"<h3>{stripped[4:]}</h3>"
        elif stripped.startswith("> "):
            body_html += f"<blockquote>{stripped[2:]}</blockquote>"
        elif stripped.startswith("- ") or stripped.startswith("* "):
            body_html += f"<li>{stripped[2:]}</li>"
        elif stripped.startswith("DISCLAIMER:") or stripped.startswith("Generated by"):
            body_html += f"<p class='disclaimer'>{stripped}</p>"
        else:
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            body_html += f"<p>{text}</p>"

    if in_table:
        body_html += "</tbody></table>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Health Impact Report</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; color: #333; }}
  h1 {{ color: #0D3B3E; border-bottom: 3px solid #0D7377; padding-bottom: 10px; text-align: center; font-size: 24px; }}
  h2 {{ color: #fff; background: #0D3B3E; padding: 8px 12px; font-size: 14px; margin-top: 20px; }}
  h3 {{ color: #0D7377; font-size: 12px; }}
  blockquote {{ border-left: 4px solid #ccc; padding-left: 15px; color: #666; font-style: italic; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
  li {{ margin: 4px 0; font-size: 10px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9px; }}
  th {{ background-color: #0D3B3E; color: #fff; padding: 6px 10px; text-align: left; font-weight: bold; }}
  td {{ border: 1px solid #ddd; padding: 5px 10px; text-align: left; }}
  tr:nth-child(even) {{ background-color: #F5F5F5; }}
  .disclaimer {{ font-size: 8px; color: #999; margin-top: 10px; }}
</style></head>
<body>{body_html}</body></html>"""


def generate_output_path(patient_name: str, base_dir: str = None) -> str:
    """Generate a timestamped output path for the report."""
    if not base_dir:
        base_dir = os.path.join(os.getcwd(), ".tmp", "user_reports")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in patient_name)
    filename = f"report_{safe_name}_{timestamp}.pdf"
    return os.path.join(base_dir, filename)


if __name__ == "__main__":
    # Demo
    sample_report = """# Health Impact Analysis Report
**Patient:** Demo Patient
**Date:** March 1, 2026

---

> This is a demo report for testing purposes only.

## Executive Summary

Patient presents with moderate cardiovascular risk factors.

## Recommendations

- Begin a regular exercise routine
- Adopt a heart-healthy diet
- Schedule annual check-up

---

*Generated by Health Impact Analyzer*
"""
    output = generate_output_path("DemoPatient")
    result = compile_pdf(sample_report, output)
    print(f"Report saved: {result}")
