# NOTE: This module have all functions to process the resume documents
# Typing libs
from fastapi import UploadFile
from pathlib import Path
from typing  import Any
from typing  import List
from typing  import Dict
from typing  import Union
from typing  import Optional
# Procesators
import pdfplumber
import pytesseract
import PyPDF2
from pdfminer.high_level    import extract_pages
from pdfminer.pdfparser     import PDFParser
from pdfminer.pdfdocument   import PDFDocument
from pdfminer.pdfpage       import PDFPage
from pdfminer.pdftypes      import resolve1, PDFObjRef
from pdf2image              import convert_from_path
# Utilitaries
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import requests
import tempfile
import re

def _get_valid_url(uri_str: str) -> str:

    if any(x in uri_str.lower() for x in ["mailto:", "tel:", "wikipedia.org", "gmail.com"]):
        return ''
        
    url_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.(?:com|ai|org|net|edu|gov|mil|in|info|co\.br)(?:/[a-zA-Z0-9./-]*)?'
    try:
        matches = re.findall(url_pattern, uri_str)
        if not matches:
            return ''
        
        url = matches[0]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        return url
    except Exception as e:
        return ''

def _validate_resume_content(text: str) -> bool:
    
    resume_keywords = [
        "experience", "education", "skills", "qualification",
        "projects", "certification", "work", "employment",
        "job", "profile", "accomplishment", "achievement",
        "responsibility", "university", "college", "degree"
    ]
    
    text_lower = text.lower()
    matches = sum(1 for keyword in resume_keywords 
                if any(word.startswith(keyword) 
                    for word in text_lower.split()))

    min_required = 3 if len(text_lower.split()) < 200 else 4

    is_resume = matches >= min_required

    return is_resume

def _extract_plain_text_links(text: str) -> List[str]:
    links = []
    url_pattern = r'(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|mil|in|info|co\.br)(?:/[a-zA-Z0-9./-]*)?'
    
    matches = re.findall(url_pattern, text)
    for match in matches:
        valid_url = _get_valid_url(match.rstrip('/'))
        if valid_url:
            links.append(valid_url)
            
    return list(set(links))


# Image extraction
async def extract_text_from_image(image_path: Path) -> Dict[str, Union[str, List[str]]]:
    
    try:
        image    = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(image)

        cleaned_text = re.sub(r"[^a-zA-Z0-9\s@+./:,-_|]", " ", ocr_text)
        cleaned_text = cleaned_text.replace("\n", " ").replace("  ", " ")

        is_resume   = _validate_resume_content(cleaned_text)
        plain_links = _extract_plain_text_links(cleaned_text)

        return {
            "status": True,
            "cleaned_text": cleaned_text,
            "links": plain_links,
            "is_resume": is_resume
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }
    
# Pdf processing
async def extract_hyperlinks(pdf_path: Path) -> List[str]:
    links_list = []
    
    try:
        with open(pdf_path, 'rb') as file:
            parser = PDFParser(file)
            document = PDFDocument(parser)
            
            for page_num, page in enumerate(PDFPage.create_pages(document)):
                
                if 'Annots' not in page.attrs:
                    continue
                    
                annotations = resolve1(page.attrs['Annots'])
                if not annotations:
                    continue
                    
                for annot in annotations:
                    try:
                        annot = resolve1(annot)
                        if annot.get('Subtype').name != 'Link' or 'A' not in annot:
                            continue
                            
                        uri = resolve1(annot['A'])
                        if 'URI' not in uri:
                            continue
                            
                        uri_obj = uri['URI']
                        if isinstance(uri_obj, PDFObjRef):
                            uri_obj = resolve1(uri_obj)
                            
                        uri_str = uri_obj.decode('utf-8') if isinstance(uri_obj, bytes) else str(uri_obj)
                        uri_str = uri_str.rstrip('/')
                        
                        valid_url = _get_valid_url(uri_str)
                        if valid_url:
                            links_list.append(valid_url)
                            
                    except Exception as e:
                        continue
                        
        unique_links = list(set(links_list))
        return unique_links
        
    except Exception as e:
        raise

async def extract_text_from_pdf(pdf_path: Path) -> Dict[str, Union[str, List[str]]]:
    
    try:
        extracted_text = ""
        has_tables = False
        pages_with_images = []
        is_resume = False
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                if page.extract_tables():
                    has_tables = True
                if page.images:
                    pages_with_images.append(page_num)
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                extracted_text += page.extract_text() + "\n"
        
        # Handle tables if present
        if has_tables:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    for table in page.extract_tables():
                        for row in table:
                            formatted_row = "|".join([str(cell) if cell is not None else "" for cell in row])
                            extracted_text += formatted_row + "\n"
                        extracted_text += "\n"
        
        # Handle images with OCR if present
        if pages_with_images:
            pages = convert_from_path(
                pdf_path,
                first_page=min(pages_with_images) + 1,
                last_page=max(pages_with_images) + 1
            )
            
            def ocr_page(page):
                return pytesseract.image_to_string(page)
            
            with ThreadPoolExecutor() as executor:
                ocr_results = list(executor.map(ocr_page, pages))
                
            for page_num, ocr_result in enumerate(ocr_results):
                extracted_text += ocr_result + "\n"
        
        cleaned_text = re.sub(r"[^a-zA-Z0-9\s@+./:,-_|]", " ", extracted_text)
        cleaned_text = cleaned_text.replace("\n", " ").replace("  ", " ")

        # Validate if it's a resume
        is_resume = _validate_resume_content(cleaned_text)

        plain_links = _extract_plain_text_links(cleaned_text)
        
        return {
            "status": True,
            "cleaned_text": cleaned_text,
            "links": plain_links,
            "is_resume": is_resume
        }
        
    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }

# Main process
async def process_docs(source: Union[str, UploadFile]) -> Dict:

    tmp_path: Optional[Path] = None
    try:
        # Validation
        if isinstance(source, str):
            ext = Path(source).suffix.lower() or ".pdf"
        else:
            ext = Path(source.filename).suffix.lower()

        is_image = ext in {".jpg", ".jpeg", ".png"}
        suffix = ext if is_image else ".pdf"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            if isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
                
                response = requests.get(source)
                response.raise_for_status()
                tmp_file.write(response.content)

            else:
                content = await source.read()
                tmp_file.write(content)

            tmp_path = Path(tmp_file.name)

        if is_image:

            text_result = await extract_text_from_image(tmp_path)
            if not text_result["status"]:
                raise Exception(text_result["error"])

            all_links = text_result["links"]
        
        else:
            text_result = await extract_text_from_pdf(tmp_path)
            if not text_result["status"]:
                raise Exception(text_result["error"])

            hyperlinks = await extract_hyperlinks(tmp_path)

            all_links = list(set(hyperlinks + text_result["links"]))

        return {
            "status": True,
            "cleaned_text": text_result["cleaned_text"],
            "links": all_links,
            "is_resume": text_result.get("is_resume", False)
        }

    except Exception as e:
        
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()
        return {
            "status": False,
            "error": str(e)
        }
    
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()
