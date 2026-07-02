"""
OCR service.

Extracts raw text from an uploaded lab report, which may be a native-text
PDF, a scanned/image-only PDF, or a plain image (PNG/JPEG/TIFF).

Strategy:
    1. If the file is a PDF, try direct text extraction first (PyMuPDF /
       pdfplumber) — this is fast and perfectly accurate for digitally
       generated reports.
    2. If that yields little/no text (i.e. it's a scanned document), fall
       back to rasterizing each page and running Tesseract OCR on it.
    3. If the file is an image, preprocess it with OpenCV (grayscale,
       denoise, threshold) before running Tesseract, which meaningfully
       improves OCR accuracy on photographed lab reports.

All heavy dependencies are imported lazily / defensively so the rest of the
app keeps working even in environments where they are not yet installed.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import OCRProcessingException, UnsupportedFileTypeException

logger = logging.getLogger(__name__)

MIN_CHARS_FOR_NATIVE_TEXT = 40  # below this, assume the PDF is scanned


class OCRService:
    def __init__(self):
        self._configure_tesseract()

    def _configure_tesseract(self) -> None:
        try:
            import pytesseract

            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        except ImportError:
            logger.warning("pytesseract not installed — OCR fallback for images will not work.")

    def extract_text(self, file_path: str) -> str:
        """Entry point: dispatch based on file extension."""
        suffix = Path(file_path).suffix.lower()

        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeException(f"Unsupported file type: {suffix}")

        try:
            if suffix == ".pdf":
                return self._extract_from_pdf(file_path)
            return self._extract_from_image(file_path)
        except UnsupportedFileTypeException:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("OCR extraction failed for %s", file_path)
            raise OCRProcessingException(str(exc)) from exc

    # ------------------------------------------------------------------ #
    # PDF handling
    # ------------------------------------------------------------------ #
    def _extract_from_pdf(self, file_path: str) -> str:
        text = self._extract_pdf_native_text(file_path)
        if len(text.strip()) >= MIN_CHARS_FOR_NATIVE_TEXT:
            logger.info("Extracted native text from PDF (%d chars).", len(text))
            return text

        logger.info("Native PDF text too short — falling back to OCR rasterization.")
        return self._ocr_pdf_pages(file_path)

    def _extract_pdf_native_text(self, file_path: str) -> str:
        chunks: list[str] = []
        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    chunks.append(page_text)
        except ImportError:
            logger.warning("pdfplumber not installed; skipping native text extraction.")
        return "\n".join(chunks)

    def _ocr_pdf_pages(self, file_path: str) -> str:
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise OCRProcessingException(
                "OCR dependencies (PyMuPDF/pytesseract/Pillow) are not installed."
            ) from exc

        text_chunks: list[str] = []
        doc = fitz.open(file_path)
        try:
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                # Render at 2x zoom for better OCR accuracy
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                preprocessed = self._preprocess_image(img)
                page_text = pytesseract.image_to_string(preprocessed)
                text_chunks.append(page_text)
        finally:
            doc.close()

        return "\n".join(text_chunks)

    # ------------------------------------------------------------------ #
    # Image handling
    # ------------------------------------------------------------------ #
    def _extract_from_image(self, file_path: str):
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise OCRProcessingException(
                "OCR dependencies (pytesseract/Pillow) are not installed."
            ) from exc

        image = Image.open(file_path)
        preprocessed = self._preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed)
        logger.info("OCR extracted %d characters from image.", len(text))
        return text

    def _preprocess_image(self, pil_image):
        """
        Improve OCR accuracy using OpenCV: grayscale -> denoise -> adaptive
        threshold. Falls back to the original image if OpenCV is missing.
        """
        try:
            import cv2
            import numpy as np
            from PIL import Image

            img_array = np.array(pil_image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
            )
            return Image.fromarray(thresh)
        except ImportError:
            logger.warning("OpenCV not installed — using raw image for OCR without preprocessing.")
            return pil_image
