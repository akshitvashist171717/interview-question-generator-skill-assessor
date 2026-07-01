"""utils/resume_parser.py — PDF/DOCX text + metadata extraction"""
import re, io #cleaning the extracted text, and pulling structured metadata out of it.
import pdfplumber #Used to read PDF files. It opens the PDF page by page and calls
import docx   #Used to read .docx Word files.


def extract_text(file_bytes: bytes, filename: str) -> str: # It's more reliable than alternatives like PyPDF2 because it preserves text order and handles multi-column layouts better.
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return _pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return _docx(file_bytes)
    raise ValueError(f"Unsupported file type: .{ext}")


def _pdf(b: bytes) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(b)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
    return _clean("\n".join(parts))


def _docx(b: bytes) -> str:
    doc = docx.Document(io.BytesIO(b))
    return _clean("\n".join(p.text for p in doc.paragraphs if p.text.strip()))


def _clean(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    return text.strip()


def extract_metadata(text: str) -> dict:
    return {
        "name":     _name(text),
        "email":    _email(text),
        "phone":    _phone(text),
        "linkedin": _linkedin(text),
    }


def _email(t):
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", t)
    return m.group(0) if m else None

def _phone(t):
    m = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", t)
    return m.group(0).strip() if m else None

def _linkedin(t):
    m = re.search(r"linkedin\.com/in/[\w\-]+", t, re.IGNORECASE)
    return "https://" + m.group(0) if m else None

def _name(t):
    for line in t.splitlines():
        line = line.strip()
        if not line:
            continue
        words = line.split()
        if 1 < len(words) <= 5 and all(re.match(r"^[A-Za-z\-'.]+$", w) for w in words):
            return line
    return None
