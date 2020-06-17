from pathlib import Path
from typing import List, Union, BinaryIO

import tika
from tika import parser
from bs4 import BeautifulSoup
from docx import Document

tika.initVM()


def paginate(list_of_paragraphs: List, max_page_length=1000) -> List[List]:
    """Split list of paragraphs into pages.

    Args:
        list_of_paragraphs: List of paragraphs.
        max_page_length: Approximate length of pages. Maximum number of characters for
            one page.

    Returns:
        List of pages.
    """
    pages = []
    one_page = []
    page_len = 0
    for par in list_of_paragraphs:
        if page_len >= max_page_length:
            pages.append(one_page)
            one_page = []
            page_len = 0
        one_page.append(par)
        page_len += len(par)
    else:
        pages.append(one_page)
    return pages


def load_docx(file_path: str) -> List[List]:
    """Load a docx file and split document to pages.

    Args:
        file_path: path to docx file.
    """
    doc = Document(file_path)
    return [[str(p.text) for p in doc.paragraphs]]


def load_pdf(pdf: Union[str, Path, BinaryIO]) -> List[List]:
    """Load a PDF file and split document to pages.

    Args:
        pdf: PDF file or path to file

    Returns:
        list of pages.
    """
    # tika's parser requires only str-like paths
    if isinstance(pdf, Path):
        pdf = str(pdf)
    if isinstance(pdf, str):
        parser_ = parser.from_file
    else:
        parser_ = parser.from_buffer

    parsed: BeautifulSoup = BeautifulSoup(parser_(pdf, xmlContent=True)["content"],
                                          features="lxml")

    list_of_pages = []
    for div in parsed.find_all("div", {"class": "page"}):
        list_of_paragraphs = []
        for p in div.find_all("p"):
            par = p.text.replace("-\n", "").replace("\n", "")
            if par:
                list_of_paragraphs.append(par)
        if list_of_paragraphs:
            list_of_pages.append(list_of_paragraphs)
    return list_of_pages


def split_html(file_path: Path) -> List[List]:
    """Split html content to pages.

    Args:
        file_path: path to file

    Returns:
        list of pages
    """
    try:
        raw_html = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw_html = file_path.read_text(encoding="windows-1252")

    soup = BeautifulSoup(raw_html, features="lxml")
    [s.extract() for s in
     soup(['style', 'script', 'head', 'title', 'meta', '[document]'])]
    # replace non-breaking space
    soup = soup.get_text(strip=False).replace("\xa0", " ")
    lines = [line.strip() for line in soup.splitlines() if line.strip()]
    return paginate(lines)


def split_txt(file_path: Path) -> List[List]:
    """Split text to pages.

    Args:
        file_path: path to file

    Returns:
        list of pages.
    """
    file_content = file_path.read_text().split("\n")
    return paginate(file_content)
