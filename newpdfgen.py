from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import json
import re

class PDFReportGenerator:
    def __init__(self, json_path, pdf_path):
        self.json_path = json_path
        self.pdf_path = pdf_path
        self.llm_questions = [
            "Questions", 
            "Was the content interesting and as per the guidelines provided?",
            "Who are you and what are your skills, expertise, and personality traits?",
            "Why are you the best person to fit this role?",
            "How are you different from others?",
            "What value do you bring to the role?",
            "Did the speech have a structure of Opening, Body, and Conclusion?",
            "How was the quality of research for the topic? Did the student's speech demonstrate a good depth? Did they cite sources of research properly?",
            "How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity?"
        ]
        
        self.qualitative_questions = [
            "Was the content interesting and as per the guidelines provided?",
            "Who are you and what are your skills, expertise, and personality traits?",
            "Why are you the best person to fit this role?",
            "How are you different from others?",
            "What value do you bring to the role?"
        ]

    def clean_answer(self, answer):
        return re.sub(r'^\d+\.\s*', '', answer).strip()

    def create_pdf(self):
        with open(self.json_path, 'r') as json_file:
            data = json.load(json_file)

        doc = SimpleDocTemplate(self.pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph("Evaluation Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Scores
        posture_text = f"<b>Posture Score: {data['posture']}</b>"
        eye_text = f"<b>Eye Contact Score: {data['Eye Contact']}</b>"
        elements.append(Paragraph(posture_text, styles['Normal']))
        elements.append(Paragraph(eye_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Tone Analysis Section
        if 'tone_analysis' in data:
            elements.append(Paragraph("Tone Analysis:", styles['Heading2']))
            tone_data = [['Aspect', 'Analysis']]
            for aspect, analysis in data['tone_analysis'].items():
                tone_data.append([aspect, analysis])
            
            tone_table = Table(tone_data, colWidths=[2*inch, 4*inch])
            tone_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2196F3")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            elements.append(tone_table)
            elements.append(Spacer(1, 24))

        # Qualitative Analysis
        elements.append(Paragraph("Qualitative Analysis:", styles['Heading2']))
        llm_answers = re.split(r'\n(?=\d+\.)', data['LLM'])
        
        # First Table (Qualitative Questions)
        qualitative_data = [['Question', 'Response']]
        for question in self.qualitative_questions:
            idx = self.llm_questions.index(question)
            answer = self.clean_answer(llm_answers[idx]) if idx < len(llm_answers) else "N/A"
            qualitative_data.append([
                Paragraph(f"<b>{question}</b>", styles['BodyText']),
                Paragraph(f"<b>{answer}</b>", styles['BodyText'])
            ])

        qual_table = Table(qualitative_data, colWidths=[2.5*inch, 4.5*inch])
        qual_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(qual_table)
        elements.append(Spacer(1, 24))

        # Second Table (Structural Questions)
        structural_data = [['Question', 'Response']]
        structural_questions = self.llm_questions[5:]
        
        for i, question in enumerate(structural_questions, 5):
            answer = self.clean_answer(llm_answers[i]) if i < len(llm_answers) else "N/A"
            structural_data.append([
                Paragraph(f"<b>{question}</b>", styles['BodyText']),
                Paragraph(f"<b>{answer}</b>", styles['BodyText'])
            ])

        struct_table = Table(structural_data, colWidths=[2.5*inch, 4.5*inch])
        struct_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FF9800")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(struct_table)

        doc.build(elements)