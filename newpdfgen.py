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
            "How was the quality of research for the topic? Did the student’s speech demonstrate a good depth? Did they cite sources of research properly?",
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
        """Remove numbering like 1., 2., 3., etc., from the beginning of the answer."""
        return re.sub(r'^\d+\.\s*', '', answer).strip()

    def create_pdf(self):
        # Load JSON data
        with open(self.json_path, 'r') as json_file:
            data = json.load(json_file)

        # Create PDF document
        doc = SimpleDocTemplate(self.pdf_path, pagesize=letter)
        elements = []

        # Add title
        styles = getSampleStyleSheet()
        title = Paragraph("Evaluation Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Add Posture and Eye Contact Score
        posture_text = f"<b>Posture Score: {data['posture']}</b>"
        eye_text = f"<b>Eye Contact Score: {data['Eye Contact']}</b>"
        elements.append(Paragraph(posture_text, styles['Normal']))
        elements.append(Paragraph(eye_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Extract LLM answers and split them based on numbering pattern
        llm_answers = re.split(r'\n(?=\d+\.)', data['LLM'])

        # Create Qualitative Remarks Table
        elements.append(Paragraph("Qualitative Analysis:", styles['Heading2']))
        elements.append(Spacer(1, 12))

        qualitative_data = [['Question', 'Response']]  # Table headers with bold text
        for question in self.qualitative_questions:
            idx = self.llm_questions.index(question)
            answer = self.clean_answer(llm_answers[idx]) if idx < len(llm_answers) else "No answer provided."
            response = Paragraph(f"<b>{answer}</b>", styles['BodyText'])  # Make the response bold
            ques = Paragraph(f"<b>{question}</b>", styles['BodyText'])    # Make the question bold
            qualitative_data.append([ques, response])

        qualitative_table = Table(qualitative_data, colWidths=[2 * inch, 5.5 * inch])

        # Stylish Table Style for Qualitative Remarks with bold content
        qualitative_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),  # Set all text to bold
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8F5E9")),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
        ]))

        elements.append(qualitative_table)
        elements.append(Spacer(1, 24))

        # Add remaining questions in a different table
        table_data = [['Question', 'Response']]  # Table headers with bold text

        for i, question in enumerate(self.llm_questions):
            if question not in self.qualitative_questions:
                answer = self.clean_answer(llm_answers[i]) if i < len(llm_answers) else "No answer provided."
                response = Paragraph(f"<b>{answer}</b>", styles['BodyText'])  # Make the response bold
                ques = Paragraph(f"<b>{question}</b>", styles['BodyText'])    # Make the question bold
                table_data.append([ques, response])

        # Create table with specific column widths to fit the content
        table = Table(table_data, colWidths=[2 * inch, 5.5 * inch])

        # Add table style with bold content
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),  # Set all text to bold
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
        ]))

        elements.append(table)

        # Build the PDF
        doc.build(elements)

        print("PDF generated successfully:", self.pdf_path)
