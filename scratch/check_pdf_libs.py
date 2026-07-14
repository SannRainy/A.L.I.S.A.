import os
import sys

# Try to import pdf libraries to see what is available
pdf_libs = ['pypdf', 'PyPDF2', 'pdfplumber', 'fitz', 'docx']
for lib in pdf_libs:
    try:
        __import__(lib)
        print(f"Library {lib} is installed.")
    except ImportError:
        print(f"Library {lib} is NOT installed.")
