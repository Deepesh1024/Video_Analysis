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

        # Add LLM Responses in a table format
        table_data = [['Question', 'Response']]  # Table headers

        # Extract LLM answers and split them based on numbering pattern
        llm_answers = re.split(r'\n(?=\d+\.)', data['LLM'])

        # Iterate through questions and assign corresponding answers
        for i, question in enumerate(self.llm_questions):
            # Get the answer or a default message if it's missing
            answer = llm_answers[i].strip() if i < len(llm_answers) else "No answer provided."
            response = Paragraph(answer, styles['BodyText'])
            ques = Paragraph(question, styles['BodyText'])  # Wrap the text using Paragraph
            table_data.append([ques, response])

            # Insert Posture and Eye Contact Scores after Question 5
            if i == 5:
                posture_text = Paragraph(f"Posture Score: {data['Posture']}", styles['BodyText'])
                eye_text = Paragraph(f"Eye Contact Score: {data['Eye']}", styles['BodyText'])
                table_data.append([Paragraph("Posture Score", styles['BodyText']), posture_text])
                table_data.append([Paragraph("Eye Contact Score", styles['BodyText']), eye_text])

        # Create table with specific column widths to fit the content
        table = Table(table_data, colWidths=[2 * inch, 5.5 * inch])  # Adjust column widths

        # Add table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top of the cell
        ]))

        elements.append(table)

        # Build the PDF
        doc.build(elements)

        print("PDF generated successfully:", self.pdf_path)

# Example usage
json_data = {
    "LLM": "1. Yes, the content was interesting and followed the guidelines.\n"
           "2. I am a software engineer with expertise in AI and NLP.\n"
           "3. I have experience and passion in this domain, and I am committed to continuous learning.\n"
           "4. I stand out due to my practical experience and ability to apply theoretical knowledge in real-world scenarios.\n"
           "5. I bring great value by blending technical expertise with a focus on user needs.\n"
           "6. Yes, it had a clear structure, which helped in understanding the main points.\n"
           "7. The research quality was excellent, demonstrating good depth and citation of sources.\n"
           "8. The overall speech was convincing, persuasive, and I would consider them for the job opportunity.",
    "Posture": "Satisfactory",  # Qualitative descriptor for Posture Score
    "Eye": "Excellent"  # Qualitative descriptor for Eye Contact Score
}

# Save JSON data to a file for the PDF generator
with open('evaluation_data.json', 'w') as f:
    json.dump(json_data, f)

# Generate the PDF with the data
pdf_generator = PDFReportGenerator('evaluation_data.json', 'evaluation_report.pdf')
pdf_generator.create_pdf()
