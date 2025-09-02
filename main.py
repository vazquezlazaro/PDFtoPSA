"""Entry point for converting planogram PDFs into PSA data structures.

The script lets the user select one or more PDF files, runs the
``PlanogramExtractor`` on each file and prints the resulting structured data.
The data can subsequently be used to create PSA files.
"""
from __future__ import annotations

import json

from HelperFile import select_pdf
from planogram_extractor import PlanogramExtractor


def pdf_to_psa() -> None:
    """Run the planogram extraction pipeline on selected PDFs."""
    selected_files = select_pdf()
    extractor = PlanogramExtractor()
    for pdf_file in selected_files:
        print(f"Processing file: {pdf_file}")
        planogram_data = extractor.extract_planogram(pdf_file)
        print(json.dumps(planogram_data, indent=2))


if __name__ == "__main__":
    pdf_to_psa()
