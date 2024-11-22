from pdfgen import PDFReportGenerator

def main():
    json_path = r"C:\Users\ayush\RE-LLM\myenv\output.json"  # Path to your JSON file
    pdf_path = "evaluation_report.pdf"  # Desired output PDF file path

    # Create an instance of PDFReportGenerator
    pdf_report_generator = PDFReportGenerator(json_path, pdf_path)

    # Generate the PDF report
    pdf_report_generator.create_pdf()

if __name__ == "__main__":
    main()
