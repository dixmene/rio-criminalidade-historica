"""
Script de Extração de Texto Multi-Formato.
Suporta: PDF (pypdf / pdfplumber), HTML (BeautifulSoup), TXT, JSON e CSV.
"""
import sys
from pathlib import Path
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import pypdf
import pdfplumber

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def extract_from_pdf(pdf_path: Path) -> Dict[str, any]:
    """Extrai texto e páginas de arquivo PDF."""
    pages_content: List[Dict[str, any]] = []
    full_text = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_content.append({
                "page_number": idx,
                "text": text
            })
            full_text.append(text)

    return {
        "file_type": "pdf",
        "total_pages": total_pages,
        "full_text": "\n\n".join(full_text),
        "pages": pages_content,
    }


def extract_from_html(html_path: Path) -> Dict[str, any]:
    """Extrai texto limpo e parágrafos de arquivo HTML."""
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Remove scripts e estilos
    for elem in soup(["script", "style", "nav", "footer", "header"]):
        elem.extract()

    title = soup.title.string if soup.title else ""
    paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
    full_text = "\n\n".join(paragraphs)

    return {
        "file_type": "html",
        "title": title,
        "full_text": full_text,
        "paragraphs": paragraphs,
    }


def extract_from_txt(txt_path: Path) -> Dict[str, any]:
    """Extrai conteúdo de arquivo texto."""
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    return {
        "file_type": "txt",
        "full_text": content,
    }


def extract_text(file_path: Path) -> Dict[str, any]:
    """Roteador polimórfico de extração baseado na extensão."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext in (".html", ".htm"):
        return extract_from_html(file_path)
    elif ext in (".txt", ".md", ".json", ".csv"):
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Formato não suportado para extração direta: {ext}")


if __name__ == "__main__":
    print("Módulo de Extração de Texto Multi-Formato pronto.")
