from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import json
import re



from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from Overall_Analyser import VideoResumeEvaluator 



# Register a custom font
pdfmetrics.registerFont(TTFont('Arial', r'ARIAL.TTF'))
pdfmetrics.registerFont(TTFont('Arial-Bold', r'ArialBD.ttf'))
styles = getSampleStyleSheet() 
styles['BodyText'].fontName = 'Arial'
def create_combined_pdf(logo_path, json_path):
    # Load quality analysis data
    with open(json_path, 'r') as fp:
        tabular_data = json.load(fp)

    # Predefined questions for evaluation (static questions)
    llm_questions = [
        "Questions", 
        "Did the Speaker Speak with Confidence ?", 
        "Was the content interesting and as per the guidelines provided?",
        "Who are you and what are your skills, expertise, and personality traits?",
        "Why are you the best person to fit this role?",
        "How are you different from others?",
        "What value do you bring to the role?",
        "Did the speech have a structure of Opening, Body, and Conclusion?",
        "How was the quality of research for the topic? Did the student's speech demonstrate a good depth? Did they cite sources of research properly?",
        "How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity?"
    ]

    # Function to clean answers (remove numbering)
    def clean_answer(answer):
        return re.sub(r'^\d+\.\s*', '', answer).strip()

    # Extract answers from JSON
    llm_answers = re.split(r'\n(?=\d+\.)', tabular_data['LLM'])  # Splitting answers based on numbered format

    # Create PDF document
    doc = SimpleDocTemplate("reports/combined_report.pdf", 
                            pagesize=letter,
                            topMargin=1.5*inch,
                            bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()
    flowables = []

    # ===================== Header/Footer Function =====================
    def add_header_footer(canvas, doc):
            canvas.saveState()
            
            # Add logo
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.drawOn(canvas, (letter[0]-2*inch)/2, letter[1]-1.2*inch)
            website_text = "https://some.education"
            canvas.setFont("Arial", 9)
            canvas.linkURL("https://some.education",
                        (0.5*inch, 0.3*inch, 2.5*inch, 0.5*inch),
                        relative=1)
            canvas.drawString(0.5*inch, 0.3*inch, website_text)

            # Page number (right bottom)
            page_num = canvas.getPageNumber()
            canvas.drawRightString(letter[0]-0.5*inch, 0.3*inch, f"Page {page_num}")

            canvas.restoreState()
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['BodyText'],
        fontName='Arial-Bold',
        fontSize=10,
        spaceAfter=12,
        leading=16
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        leftIndent=10
    )

    # Add these variables at the top of your function
    name = tabular_data['User Name'] 
    now = datetime.now() # Replace with your variable
    """Use -d instead of #d incase of linux/Mac"""
    formatted_date = now.strftime("%-d %B %Y")
    current_date = str(formatted_date)# Replace with your variable

# Modified title paragraph with centered alignment
    title = Paragraph(
        f"<para alignment='center'><b>{name}</b><br/></para>"
        f"<para alignment='center'>{current_date}</para>", 
        styles['Title']
    )
    flowables.append(title)
    flowables.append(Spacer(1, 24))

    def add_quality_section(title, items):
        
        flowables.append(Paragraph(title, section_style))
        bullet_list = []
        for item in items:
            bullet_list.append(Paragraph(f"• {item}", bullet_style))
        flowables.extend(bullet_list)
        flowables.append(Spacer(1, 18))
    with open(r'json/quality_analysis.json', 'r') as fp:
        quality_data = json.load(fp)
    add_quality_section("Qualitative Analysis - Positive", quality_data["Qualitative Analysis"])
    add_quality_section("Qualitative Analysis - Areas of Imrpovement", quality_data["Quantitative Analysis"])

    # ========== Page Break for Table Section ==========
    flowables.append(PageBreak()) 
    section_style = ParagraphStyle('SectionStyle', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=10, spaceAfter=12, leading=16)
    flowables.append(Paragraph("<b>Detailed Evaluation Metrics</b>", section_style))
    flowables.append(Spacer(1, 24))

    # Table styles and creation
    normal_style = ParagraphStyle('NormalStyle', parent=styles['BodyText'], fontSize=10, leading=12, spaceAfter=6)
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')

    # Table header row (DO NOT MODIFY THIS)
    table_data = [
        [
            Paragraph("<b>No.</b>", bold_style),
            Paragraph("<b>Items to look out for</b>", bold_style),
            Paragraph("<b>5 point scale</b>", bold_style)
        ]
    ]

    # Add dynamic rows from JSON
    for i, question in enumerate(llm_questions[1:], 1):  # Skip first "Questions" entry
        if i == 1:
            # Special handling for the confidence question with sub-items
            sub_items = [
                ("Posture", "posture"),
                ("Smile", "Smile Score"),
                ("Eye Contact", "Eye Contact"),
                ("Energetic Start", "Energetic Start")
            ]
            # Build the Items text with main question and sub-items
            items_text = "Did the speaker speak with confidence?<br/>" + "<br/>".join([f"• {item[0]}" for item in sub_items])
            # Extract scores from JSON
            print("Items in sub items --> ") 
            scores = [ ]
            for items in sub_items:
                if tabular_data.get(items[1]) == 1:
                    scores.append("Needs Improvement") 
                elif tabular_data.get(items[1]) == 2:
                    scores.append("Poor") 
                elif tabular_data.get(items[1]) == 3:
                    scores.append("Satisfactory") 
                elif tabular_data.get(items[1])== 4:
                    scores.append("Good") 
                elif tabular_data.get(items[1]) == 5:
                    scores.append("Excellent")
                else:
                    scores.append("N/A") 
                
            
            
            scores_text = "<br/>" + "<br/>".join([f"<b>{score}</b>" for score in scores])
            # Add row to table
            table_data.append([
                Paragraph(f"{i}.", normal_style),
                Paragraph(items_text, normal_style),
                Paragraph(scores_text, normal_style)
            ])
        else:
            # Handle other questions normally
            answer = clean_answer(llm_answers[i]) if i < len(llm_answers) else "N/A"
            table_data.append([
                Paragraph(f"{i}.", normal_style),
                Paragraph(question, normal_style),
                Paragraph(answer, normal_style)
            ])

    # Create Table
    table = Table(table_data, colWidths=[40, 300, 200])
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))

    flowables.append(table)

    # Build document with header/footer
    doc.build(flowables, 
              onFirstPage=add_header_footer,
              onLaterPages=add_header_footer)

    print("PDF generated successfully with dynamic table!")

