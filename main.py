from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
from split_pdf import split_pdf_by_size, create_zip_file

app = FastAPI()

# Route to split the PDF and return a zip link
@app.post("/split-pdf/")
async def split_pdf(file: UploadFile = File(...), max_size_mb: float = 1):
    output_folder = "output"
    pdf_path = os.path.join(output_folder, file.filename)

    # Save the uploaded PDF file
    with open(pdf_path, 'wb') as f:
        f.write(await file.read())

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Split the PDF
    split_files = split_pdf_by_size(pdf_path, output_folder, max_size_mb=max_size_mb)

    # Zip the split PDF files
    zip_path = os.path.join(output_folder, "split_pdfs.zip")
    create_zip_file(split_files, zip_path)

    # Return the download link for the zip file
    return {"download_link": f"/download-zip/{os.path.basename(zip_path)}"}

# Route to download the zip file
@app.get("/download-zip/{zip_filename}")
def download_zip(zip_filename: str):
    zip_path = os.path.join("output", zip_filename)

    if not os.path.exists(zip_path):
        return {"error": "File not found"}

    return FileResponse(path=zip_path, filename=zip_filename, media_type='application/zip')
