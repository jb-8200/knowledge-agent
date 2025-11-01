# Spec 05 – Parse and chunk uploaded documents

This specification outlines how to extract text from various file types and split it into passages suitable for embedding.

## Parsing Modules

Implement separate parsers for each supported file type:

* **PDF** – Use `pdfplumber` to iterate through pages and extract text.  Normalize whitespace and handle encoding errors.
* **DOCX** – Use `python-docx` to read paragraphs and headings.
* **Markdown** – Use the `markdown` or `markdown2` library to convert markdown to HTML, then strip HTML tags to plain text.

Example implementation:

```python
import pdfplumber
from docx import Document
import markdown as md
from bs4 import BeautifulSoup

def parse_pdf(file_path: str) -> str:
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)

def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

def parse_markdown(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        html = md.markdown(f.read())
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")
```

## Chunking Strategy

After extracting the full text, split it into chunks suitable for embedding.  Use a character‑ or token‑based splitter with overlap to preserve context.  LangChain’s `RecursiveCharacterTextSplitter` works well:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " "]
)

def chunk_text(text: str) -> list[dict]:
    chunks = splitter.split_text(text)
    return [
        {
            "text": chunk,
            "metadata": {"chunk_index": idx}
        }
        for idx, chunk in enumerate(chunks)
    ]
```

Include additional metadata such as page numbers for PDFs or section headings for DOCX when available.  Store the original filename, document ID and chunk index with each chunk.

## Error Handling

Handle parsing errors gracefully.  If a parser fails, log the error and skip the document or fallback to a default extraction method (e.g., `pdfplumber` for PDFs).  Ensure that empty documents are filtered out before embedding.
