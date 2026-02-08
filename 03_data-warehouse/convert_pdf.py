from pdf2image import convert_from_path
import os

pdf_path = 'ml-model-cheatsheet.pdf'
output_path = 'ml-model-cheatsheet.png'

if os.path.exists(pdf_path):
    try:
        images = convert_from_path(pdf_path, first_page=0, last_page=1)
        if images:
            images[0].save(output_path, 'PNG')
            print(f"Successfully saved {output_path}")
        else:
            print("No images converted.")
    except Exception as e:
        print(f"Error converting PDF: {e}")
else:
    print(f"File not found: {pdf_path}")
