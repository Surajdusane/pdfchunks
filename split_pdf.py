import os
import zipfile
from fastapi import HTTPException
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_by_size(input_pdf_path, output_folder, max_size_mb=1):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the original PDF
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    part_number = 1
    start_page = 0
    pdf_parts = []  # List to store split PDF file paths

    while start_page < total_pages:
        writer = PdfWriter()
        current_size = 0
        end_page = start_page

        while end_page < total_pages:
            writer.add_page(reader.pages[end_page])
            temp_pdf_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(input_pdf_path))[0]}_part{part_number}.pdf')

            with open(temp_pdf_path, 'wb') as temp_pdf:
                writer.write(temp_pdf)

            current_size = os.path.getsize(temp_pdf_path) / (1024 * 1024)  # size in MB

            if current_size > max_size_mb:
                # Remove the last page added as it caused the size to exceed the limit
                writer = PdfWriter()
                for i in range(start_page, end_page):
                    writer.add_page(reader.pages[i])
                temp_pdf_path = os.path.join(output_folder, f'{os.path.splitext(os.path.basename(input_pdf_path))[0]}_part{part_number}.pdf')
                with open(temp_pdf_path, 'wb') as temp_pdf:
                    writer.write(temp_pdf)
                break

            end_page += 1

        pdf_parts.append(temp_pdf_path)
        part_number += 1
        start_page = end_page

    return pdf_parts

def create_zip_file(file_paths, output_zip_path):
    try:
        with zipfile.ZipFile(output_zip_path, 'w') as zipf:
            for file in file_paths:
                zipf.write(file, os.path.basename(file))
        return output_zip_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create zip: {str(e)}")
