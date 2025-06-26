import io
from typing import Union
from pdfminer.high_level import extract_text_to_fp
import docx2txt
import os

def parse_resume_file(uploaded_file: Union[io.BytesIO, any], filename: str) -> str:
    ext = filename.split('.')[-1].lower()
    print(f"[DEBUG] File extension: {ext}")

    if ext == "pdf":
        try:
            output = io.StringIO()
            extract_text_to_fp(uploaded_file, output)
            return output.getvalue()
        except Exception as e:
            print(f"[ERROR] PDF parse failed: {e}")
            return ""
        
    elif ext == "docx":
        try:
            # Save the uploaded in-memory file to disk temporarily
            temp_path = "temp_resume.docx"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            text = docx2txt.process(temp_path)

            os.remove(temp_path)  # Clean up the temp file
            return text
        except Exception as e:
            print(f"[ERROR] DOCX parse failed: {e}")
            return ""

    else:
        print("[ERROR] Unsupported file type.")
        return ""
