from datetime import datetime
from summary import Summarization

if __name__ == '__main__':
    start_time = datetime.now()
    doc_option = int(input("1. Pdf\n2. Word Document\n3. Article URL\nPlease enter a document type to summarize: "))
    summary = Summarization(doc_option)
    if doc_option == 1:
        summary.get_pdf_content()
    elif doc_option == 2:
        summary.get_docx_content()
    elif doc_option == 3:
        summary.get_url_content()
    summary_option = int(input("1. Extractive\n2. Abstractive\nPlease choose the type of summarization: "))
    if summary_option == 1:
        summary.extractive_summarize()
    elif summary_option == 2:
        summary.abstractive_summarize()

    print(f"Runtime of the program: {datetime.now() - start_time}")