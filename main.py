import tkinter as tk
from tkinter import filedialog
import os

import PyPDF2 as PyPDF2
import tabula as tabula

from HelperFile import select_pdf

def PDF_TO_PSA():
    selected_Files = select_pdf()
    for pdf_file in selected_Files:
        print("Processing file:", pdf_file)
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)

        # Extract text content from each page
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text_content = page.extract_text()
            print("Text content from page", page_num + 1, ":\n", text_content)

        # Extract tables using tabula-py
        tables = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
        if tables:
            for table_num, table in enumerate(tables, start=1):
                print("Table", table_num, ":\n", table)


if __name__ == '__main__':
    PDF_TO_PSA()
