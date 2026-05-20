"""
Document Generation MCP Server for Insurance Renewal Agent
Creates renewal quote PDFs and coverage comparison documents
"""

import io
import base64
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class DocumentMCPServer:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = HexColor("#1a365d")
        self.accent_color = HexColor("#2c5282")
        self.success_color = HexColor("#276749")

    def generate_renewal_quote(
        self,
        policy_number: str,
        policy_holder_name: str,
        policy_type: str,
        current_premium: float,
        renewal_premium: float,
        premium_change_pct: float,
        effective_date: str,
        expiration_date: str,
        loyalty_discount_pct: float = 5.0,
        agent_name: str = None,
        agent_phone: str = None
    ) -> dict:
        """
        Generate a renewal quote PDF document
        Returns base64 encoded PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        story = []

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=self.primary_color,
            spaceAfter=6,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.accent_color,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.primary_color,
            spaceBefore=15,
            spaceAfter=8
        )

        value_style = ParagraphStyle(
            'Value',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=black,
            spaceAfter=4
        )

        bold_value_style = ParagraphStyle(
            'BoldValue',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=black,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )

        change_positive = premium_change_pct > 0
        change_color = HexColor("#c53030") if change_positive else self.success_color
        change_symbol = "+" if change_positive else "-"
        change_text = f"{change_symbol}{abs(premium_change_pct):.1f}%"

        story.append(Paragraph("POLICY RENEWAL QUOTE", title_style))
        story.append(Paragraph("Insurance Renewal Intelligence System", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.primary_color, spaceAfter=20))

        policy_info = [
            ["Policy Number:", policy_number, "Quote Date:", datetime.now().strftime("%B %d, %Y")],
            ["Policy Holder:", policy_holder_name, "Policy Type:", policy_type],
            ["Effective Date:", effective_date, "Expiration Date:", expiration_date],
            ["Agent:", agent_name or "N/A", "Phone:", agent_phone or "N/A"]
        ]

        info_table = Table(policy_info, colWidths=[1.2*inch, 2.2*inch, 1.2*inch, 2.2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.accent_color),
            ('TEXTCOLOR', (2, 0), (2, -1), self.accent_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("RENEWAL PREMIUM SUMMARY", header_style))
        story.append(HRFlowable(width="100%", thickness=1, color=self.accent_color, spaceAfter=10))

        premium_data = [
            ["Current Annual Premium:", f"${current_premium:,.2f}"],
            ["Market Adjustment:", f"+{premium_change_pct:.1f}%"],
            ["Loyalty Discount Applied:", f"-{loyalty_discount_pct:.1f}%"],
            ["", ""],
            ["Renewal Annual Premium:", f"${renewal_premium:,.2f}"],
            ["Premium Change:", f"{change_text} (${renewal_premium - current_premium:,.2f})"]
        ]

        premium_table = Table(premium_data, colWidths=[3.5*inch, 2.5*inch])
        premium_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, -2), (-1, -1), HexColor("#e2e8f0")),
            ('TEXTCOLOR', (1, -1), (1, -1), change_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOX', (0, -2), (-1, -1), 1, self.primary_color),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, HexColor("#cbd5e0")),
        ]))
        story.append(premium_table)
        story.append(Spacer(1, 20))

        coverage_data = [
            ["Coverage Type", "Current Limit", "Renewal Limit", "Status"],
            ["Liability", "$100,000", "$100,000", "No Change"],
            ["Property", "$250,000", "$250,000", "No Change"],
            ["Medical Payments", "$10,000", "$10,000", "No Change"],
            ["Uninsured Motorist", "$50,000", "$50,000", "No Change"],
        ]

        coverage_table = Table(coverage_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        coverage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('BOX', (0, 0), (-1, -1), 1, self.accent_color),
            ('LINEBELOW', (0, 0), (-1, 0), 1, self.accent_color),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f7fafc")]),
        ]))
        story.append(Paragraph("COVERAGE DETAILS", header_style))
        story.append(coverage_table)
        story.append(Spacer(1, 25))

        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor("#718096"),
            alignment=TA_CENTER
        )

        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e0"), spaceAfter=10))
        story.append(Paragraph(
            "This quote is valid for 30 days from the issue date. For questions, contact your agent or call our renewal hotline.",
            footer_style
        ))
        story.append(Spacer(1, 5))
        story.append(Paragraph(
            f"Document ID: RQ-{policy_number}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            footer_style
        ))

        doc.build(story)
        buffer.seek(0)

        pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return {
            "status": "success",
            "data": {
                "document_type": "renewal_quote",
                "policy_number": policy_number,
                "pdf_base64": pdf_base64,
                "file_name": f"Renewal_Quote_{policy_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
                "generated_at": datetime.now().isoformat()
            }
        }

    def generate_coverage_comparison(
        self,
        policy_number: str,
        policy_holder_name: str,
        current_coverage: list,
        proposed_coverage: list
    ) -> dict:
        """
        Generate a side-by-side coverage comparison document
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        story = []
        title_style = ParagraphStyle('Title', parent=self.styles['Heading1'], fontSize=18, textColor=self.primary_color, alignment=TA_CENTER)
        header_style = ParagraphStyle('Header', parent=self.styles['Heading2'], fontSize=12, textColor=self.accent_color, spaceBefore=15)

        story.append(Paragraph("COVERAGE COMPARISON REPORT", title_style))
        story.append(Paragraph(f"Policy: {policy_number} | Holder: {policy_holder_name}", header_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.primary_color, spaceAfter=20))

        table_data = [["Coverage Type", "Current", "Renewal", "Change"]]

        for curr, prop in zip(current_coverage, proposed_coverage):
            status = "No Change" if curr["limit"] == prop["limit"] else "Updated"
            row = [curr["type"], curr["limit"], prop["limit"], status]
            table_data.append(row)

        comparison_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        comparison_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, self.accent_color),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f7fafc")]),
        ]))
        story.append(comparison_table)

        doc.build(story)
        buffer.seek(0)

        pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return {
            "status": "success",
            "data": {
                "document_type": "coverage_comparison",
                "policy_number": policy_number,
                "pdf_base64": pdf_base64,
                "generated_at": datetime.now().isoformat()
            }
        }


TOOLS = [
    {
        "name": "generate_renewal_quote",
        "description": "Generate a renewal quote PDF document",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "policy_holder_name": {"type": "string"},
                "policy_type": {"type": "string"},
                "current_premium": {"type": "number"},
                "renewal_premium": {"type": "number"},
                "premium_change_pct": {"type": "number"},
                "effective_date": {"type": "string"},
                "expiration_date": {"type": "string"},
                "loyalty_discount_pct": {"type": "number"},
                "agent_name": {"type": "string"},
                "agent_phone": {"type": "string"}
            },
            "required": ["policy_number", "policy_holder_name", "policy_type", "current_premium", "renewal_premium", "premium_change_pct", "effective_date", "expiration_date"]
        }
    },
    {
        "name": "generate_coverage_comparison",
        "description": "Generate a side-by-side coverage comparison document",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "policy_holder_name": {"type": "string"},
                "current_coverage": {"type": "array"},
                "proposed_coverage": {"type": "array"}
            },
            "required": ["policy_number", "policy_holder_name", "current_coverage", "proposed_coverage"]
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    server = DocumentMCPServer()
    if hasattr(server, tool_name):
        return getattr(server, tool_name)(**arguments)
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}