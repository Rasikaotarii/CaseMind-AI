# ===========================================
# CaseMind AI — File Handler Utilities
# ===========================================
# Provides helper functions for extracting text content from
# uploaded evidence files (PDF and TXT).
#
# Image files are intentionally skipped — image analysis is
# handled by a separate agent.

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pdfplumber

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

# File extensions that this module can extract text from
DOCUMENT_EXTENSIONS = {"pdf", "txt"}

# File extensions handled by the Image Agent
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def extract_text_from_pdf(uploaded_file: "UploadedFile") -> str:
    """
    Extract all text content from an uploaded PDF file.

    Uses ``pdfplumber`` for reliable text extraction across a wide
    range of PDF structures.

    Args:
        uploaded_file: A Streamlit ``UploadedFile`` object.

    Returns:
        The concatenated text of all pages, separated by newlines.
    """
    text_parts: list[str] = []

    # Reset the file pointer to the beginning
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())

    return "\n\n".join(text_parts)


def extract_text_from_txt(uploaded_file: "UploadedFile") -> str:
    """
    Extract text content from an uploaded TXT file.

    Attempts UTF-8 decoding first, falling back to latin-1 if necessary.

    Args:
        uploaded_file: A Streamlit ``UploadedFile`` object.

    Returns:
        The decoded text content.
    """
    uploaded_file.seek(0)
    raw_bytes = uploaded_file.read()

    try:
        return raw_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw_bytes.decode("latin-1").strip()


def _get_extension(filename: str) -> str:
    """Return the lowercased file extension without the dot."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def extract_all_text(uploaded_files: list["UploadedFile"]) -> str:
    """
    Extract and combine text from all document files in the upload list.

    Image files (png, jpg, jpeg) are silently skipped.

    Args:
        uploaded_files: List of Streamlit ``UploadedFile`` objects.

    Returns:
        A single string containing the combined text from all documents,
        with file-level separators for clarity.
    """
    sections: list[str] = []

    for f in uploaded_files:
        ext = _get_extension(f.name)

        if ext == "pdf":
            text = extract_text_from_pdf(f)
        elif ext == "txt":
            text = extract_text_from_txt(f)
        else:
            # Skip non-document files (images, etc.)
            continue

        if text:
            sections.append(f"--- [File: {f.name}] ---\n{text}")

    return "\n\n".join(sections)


def has_document_files(uploaded_files: list["UploadedFile"]) -> bool:
    """Check whether the upload list contains at least one PDF or TXT file."""
    return any(
        _get_extension(f.name) in DOCUMENT_EXTENSIONS for f in uploaded_files
    )


def get_image_files(uploaded_files: list["UploadedFile"]) -> list["UploadedFile"]:
    """Return only the image (PNG/JPG/JPEG) files from the upload list."""
    return [f for f in uploaded_files if _get_extension(f.name) in IMAGE_EXTENSIONS]


def has_image_files(uploaded_files: list["UploadedFile"]) -> bool:
    """Check whether the upload list contains at least one image file."""
    return any(_get_extension(f.name) in IMAGE_EXTENSIONS for f in uploaded_files)


def read_image_bytes(uploaded_file: "UploadedFile") -> bytes:
    """Read the raw bytes of an uploaded image file, resetting the pointer first."""
    uploaded_file.seek(0)
    return uploaded_file.read()
