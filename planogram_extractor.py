"""Planogram data extraction utilities.

This module provides the `PlanogramExtractor` class which uses a
pre-trained layout detection model and OCR to locate planogram tables in a
PDF document and return them in a structured format.  The output is a list
of dictionaries describing segments, fixtures and products that can be used
for PSA generation.
"""
from __future__ import annotations

import io
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

import pdfplumber
import pandas as pd
import layoutparser as lp


@dataclass
class Product:
    """Represents a single product on a shelf."""
    name: str
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    position: str | None = None


@dataclass
class Shelf:
    """Represents a shelf containing products."""
    name: str
    products: List[Product]


class PlanogramExtractor:
    """Extracts planogram data from PDFs.

    The extractor relies on a layout detection model from the
    `layoutparser` project (pre-trained on the PubLayNet dataset) to
    identify tables within each page.  Identified tables are then passed to
    Tesseract via `layoutparser`'s OCR interface and converted into pandas
    ``DataFrame`` objects.  Simple heuristics are applied to group rows into
    shelf and product records.
    """

    def __init__(self, ocr_lang: str = "eng") -> None:
        self.layout_model = lp.Detectron2LayoutModel(
            "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
        )
        self.ocr_agent = lp.TesseractAgent(languages=ocr_lang)

    def _table_to_dataframe(self, image) -> pd.DataFrame:
        """Perform OCR on a cropped table image and return a DataFrame."""
        ocr_result = self.ocr_agent.detect(image)
        text_stream = io.StringIO("\n".join(t for _, t in ocr_result))
        # Assume comma separated values after OCR for simplicity.
        return pd.read_csv(text_stream, sep=",", engine="python")

    def extract_planogram(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract planogram information from ``pdf_path``.

        Parameters
        ----------
        pdf_path:
            Path to the PDF file containing planogram tables.

        Returns
        -------
        list of dict
            Each dictionary describes a shelf with its associated products.
        """
        results: List[Dict[str, Any]] = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=300).original
                layout = self.layout_model.detect(image)
                for block in layout:
                    if block.type != "Table":
                        continue
                    table_image = image[block.block.y1:block.block.y2, block.block.x1:block.block.x2]
                    try:
                        df = self._table_to_dataframe(table_image)
                    except Exception:
                        continue

                    shelf_name = df.columns[0] if len(df.columns) else "Shelf"
                    products: List[Product] = []
                    for _, row in df.iterrows():
                        prod = Product(
                            name=str(row.get("Name", "")),
                            width=float(row.get("Width", 0) or 0),
                            height=float(row.get("Height", 0) or 0),
                            depth=float(row.get("Depth", 0) or 0),
                            position=str(row.get("Position", "")),
                        )
                        products.append(prod)

                    results.append(asdict(Shelf(name=shelf_name, products=products)))

        return results
