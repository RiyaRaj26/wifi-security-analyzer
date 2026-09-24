import os
import logging
from datetime import datetime

logger = logging.getLogger("PDFGenerator")

# Import reportlab components
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab is not installed. PDF generation will fail.")

class PDFGenerator:
    def __init__(self):
        pass

    def generate_report(self, file_path: str, scan_info: dict, networks: list[dict], advisor_advice: dict) -> bool:
        """
        Generates a professional PDF report containing the scan summary,
        network audit table, detected security risks, and mitigations.
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("Cannot generate PDF because reportlab is not installed.")
            return False

        try:
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            
            styles = getSampleStyleSheet()
            
            # Custom Palette
            c_dark = colors.HexColor("#0F172A") # slate 900
            c_blue = colors.HexColor("#0EA5E9") # sky 500
            c_green = colors.HexColor("#10B981") # emerald 500
            c_gray_dark = colors.HexColor("#334155") # slate 700
            c_gray_light = colors.HexColor("#F8FAFC") # slate 50
            
            # Custom Styles
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=24,
                leading=28,
                textColor=c_dark,
                spaceAfter=15
            )
            
            section_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=c_blue,
                spaceBefore=15,
                spaceAfter=8,
                keepWithNext=True
            )
            
            body_style = ParagraphStyle(
                'ReportBody',
                parent=styles['BodyText'],
                fontSize=10,
                leading=14,
                textColor=c_gray_dark
            )

            body_bold = ParagraphStyle(
                'ReportBodyBold',
                parent=body_style,
                fontName='Helvetica-Bold'
            )

            cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontSize=8.5,
                leading=11,
                textColor=c_gray_dark
            )

            cell_header_style = ParagraphStyle(
                'TableCellHeader',
                parent=cell_style,
                textColor=colors.white,
                fontName='Helvetica-Bold'
            )

            risk_title_style = ParagraphStyle(
                'RiskTitle',
                parent=body_bold,
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#991B1B") # Dark red
            )
            
            story = []

            # --- Header Block ---
            story.append(Paragraph("Wi-Fi Security Audit Report", title_style))
            
            # Metadata Table
            timestamp = scan_info.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            net_count = scan_info.get("network_count", len(networks))
            avg_score = scan_info.get("avg_score", 0.0)
            
            meta_data = [
                [Paragraph(f"<b>Scan Date:</b> {timestamp}", body_style), 
                 Paragraph(f"<b>Networks Audited:</b> {net_count}", body_style)],
                [Paragraph(f"<b>Average Security Score:</b> {avg_score:.1f}/100", body_style),
                 Paragraph(f"<b>Threat Status:</b> {advisor_advice.get('status_level', 'Unknown')}", body_style)]
            ]
            
            meta_table = Table(meta_data, colWidths=[260, 260])
            meta_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 15))

            # --- Executive Summary Callout ---
            summary_html = f"<b>Executive Summary:</b> {advisor_advice.get('summary', '')}"
            summary_para = Paragraph(summary_html, body_style)
            
            summary_table = Table([[summary_para]], colWidths=[520])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), c_gray_light),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # --- Detected Networks Table ---
            story.append(Paragraph("Audited Networks", section_style))
            
            # Table headers
            table_data = [[
                Paragraph("SSID", cell_header_style),
                Paragraph("BSSID", cell_header_style),
                Paragraph("RSSI (dBm)", cell_header_style),
                Paragraph("Channel", cell_header_style),
                Paragraph("Security", cell_header_style),
                Paragraph("Encryption", cell_header_style),
                Paragraph("Score", cell_header_style)
            ]]

            for net in networks:
                # Color code score in table cells
                score_val = net.get("security_score", net.get("score", 0))
                if score_val >= 80:
                    score_color_str = "#10B981" # Green
                elif score_val >= 50:
                    score_color_str = "#F59E0B" # Orange
                else:
                    score_color_str = "#EF4444" # Red
                
                score_html = f"<b><font color='{score_color_str}'>{score_val}</font></b>"
                
                table_data.append([
                    Paragraph(net.get("ssid", "<Hidden>"), cell_style),
                    Paragraph(net.get("bssid", "00:00:00:00:00:00"), cell_style),
                    Paragraph(str(net.get("rssi", -100)), cell_style),
                    Paragraph(str(net.get("channel", 0)), cell_style),
                    Paragraph(net.get("security_type", "Open"), cell_style),
                    Paragraph(net.get("encryption", "None"), cell_style),
                    Paragraph(score_html, cell_style)
                ])

            # ColWidths sum up to 520 (matches letter width minus margins)
            net_table = Table(table_data, colWidths=[110, 110, 50, 45, 95, 70, 40])
            net_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), c_dark),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_light]),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(net_table)
            story.append(Spacer(1, 20))

            # --- Security Risk Breakdown ---
            # Compile unique risks across all audited networks
            unique_risks = {}
            for net in networks:
                for risk in net.get("risks", []):
                    risk_name = risk.get("name")
                    if risk_name not in unique_risks:
                        unique_risks[risk_name] = {
                            "level": risk.get("level", "Low"),
                            "explanation": risk.get("explanation", ""),
                            "mitigation": risk.get("mitigation", ""),
                            "affected_networks": []
                        }
                    ssid_val = net.get("ssid", "<Hidden>")
                    unique_risks[risk_name]["affected_networks"].append(f"{ssid_val} ({net.get('bssid')})")

            if unique_risks:
                story.append(Paragraph("Security Vulnerability Assessment", section_style))
                
                for r_name, r_details in unique_risks.items():
                    r_level = r_details["level"]
                    if r_level == "Critical":
                        level_color = "#EF4444" # Red
                    elif r_level == "High":
                        level_color = "#EA580C" # Dark Orange
                    elif r_level == "Medium":
                        level_color = "#F59E0B" # Yellow-Orange
                    else:
                        level_color = "#64748B" # Gray

                    affected = ", ".join(r_details["affected_networks"])
                    
                    risk_story = [
                        Paragraph(f"<b>{r_name}</b> — <font color='{level_color}'><b>[{r_level} Risk]</b></font>", risk_title_style),
                        Spacer(1, 4),
                        Paragraph(f"<b>Affected Access Points:</b> {affected}", body_style),
                        Spacer(1, 2),
                        Paragraph(f"<b>Explanation:</b> {r_details['explanation']}", body_style),
                        Spacer(1, 2),
                        Paragraph(f"<b>Recommended Mitigation:</b> {r_details['mitigation']}", body_style),
                        Spacer(1, 10)
                    ]
                    # Keep each vulnerability block together on the page
                    story.append(KeepTogether(risk_story))
            else:
                story.append(Paragraph("Security Vulnerability Assessment", section_style))
                story.append(Paragraph("No critical, high, or medium security vulnerabilities were identified in the scanned networks.", body_style))
            
            story.append(Spacer(1, 20))

            # --- Disclaimer / Footer ---
            disclaimer_text = (
                "<b>Disclaimer:</b> This report is generated by Wi-Fi Security Analyzer for educational, "
                "defensive, and security awareness purposes only. The recommendations provided are general security "
                "best practices and do not guarantee complete immunity against sophisticated cyber threats."
            )
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=body_style,
                fontSize=8,
                leading=11,
                textColor=colors.HexColor("#94A3B8"),
                alignment=1 # Centered
            )
            story.append(KeepTogether([
                Spacer(1, 10),
                Paragraph(disclaimer_text, disclaimer_style)
            ]))

            # Build document
            doc.build(story)
            logger.info(f"PDF report successfully saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}", exc_info=True)
            return False
