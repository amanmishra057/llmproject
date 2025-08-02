import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

ALLOWED_EXTENSIONS = {'pdf'}

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Save uploaded file to disk
def save_file(file, upload_folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path

# Extract text from PDF (one page at a time)
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return texts
