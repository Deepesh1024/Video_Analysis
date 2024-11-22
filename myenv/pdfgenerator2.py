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

    # Function to extract qualitative bullet points from LLM response
    def extract_qualitative_points(self, llm_output):
        bullet_pattern = r'•\s.*'  # Matches lines starting with "•"
        bullet_points = re.findall(bullet_pattern, llm_output)
        return bullet_points

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
        posture_text = f"Posture Score: {data['Posture']}"
        eye_text = f"Eye Contact Score: {data['Eye']}"
        elements.append(Paragraph(posture_text, styles['Normal']))
        elements.append(Paragraph(eye_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Add Qualitative Analysis heading
        qualitative_heading = Paragraph("Qualitative Analysis", styles['Heading2'])
        elements.append(qualitative_heading)
        elements.append(Spacer(1, 12))

        # Extract the LLM response containing qualitative analysis
        llm_output = data["LLM"]
        qualitative_points = self.extract_qualitative_points(llm_output)

        # Add the four bullet points to the PDF
        for point in qualitative_points:
            elements.append(Paragraph(point, styles['Bullet']))
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
json_path = "output.json"  # Path to your JSON file
pdf_path = "evaluation_report.pdf"  # Path where you want the PDF to be saved

# Create the PDF report generator object
pdf_generator = PDFReportGenerator(json_path, pdf_path)

# Generate the PDF
pdf_generator.create_pdf()
