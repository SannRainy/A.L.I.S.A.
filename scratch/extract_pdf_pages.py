import pypdf

pdf_path = r"SKRIPSI 2026\26_Juni_2026_Skripsi.pdf"
output_path = r"scratch\extracted_pdf_pages.txt"

reader = pypdf.PdfReader(pdf_path)
num_pages = len(reader.pages)
print(f"Total pages: {num_pages}")

# We want pages 162++ (which is 161++ in 0-indexed terms).
# Let's extract pages 155 to 190 (0-indexed: 154 to 189) to be safe and cover page numbers in text.
start_page = 154
end_page = 195

with open(output_path, "w", encoding="utf-8") as f:
    for i in range(start_page, min(end_page, num_pages)):
        f.write(f"\n--- PAGE {i+1} ---\n")
        text = reader.pages[i].extract_text()
        f.write(text)

print(f"Successfully extracted pages {start_page+1} to {min(end_page, num_pages)} to {output_path}")
