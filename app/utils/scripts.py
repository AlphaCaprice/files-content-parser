import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
import wikipedia

from app.utils.file_parsers import load_pdf, load_docx, split_html, split_txt
from app.utils.io_handler import write_pages


ext_to_fun = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".doc": load_docx,
    ".html": split_html,
    ".xml": split_html,
    ".htm": split_html,
    ".xht": split_html,
    ".txt": split_txt,
}


def process_file(file_path: Path, saving_path: Path) -> None:
    """Processed file using one of the functions based on file extension.
    Writes all parsed string chunks from file in one txt file"""
    ext = file_path.suffix
    process_function = ext_to_fun[ext]
    pages = process_function(file_path)
    txt_path = saving_path.joinpath(f"{file_path.stem}.txt")
    write_pages(txt_path, pages)


def process_link(link: str, saving_path: Path) -> None:
    # if page source is wikipedia load content using wiki api
    parsed_url = urlparse(unquote(link))
    if "wikipedia.org" in link:
        lang = parsed_url.hostname.split(".", 1)[0]
        article_name = parsed_url.path.rsplit("/", 1)[-1]

        wikipedia.set_lang(lang)
        page = wikipedia.page(article_name)

        txt_path = saving_path.joinpath(f"wiki_{article_name}.txt")
        txt_path.write_text(page.content)
        return None

    r = requests.get(link)

    filename = parsed_url.path.replace('/', '_').rsplit(".", 1)[0]
    hashed_query = ""
    if parsed_url.query:
        hashed_query = hashlib.sha1(parsed_url.query.encode()).hexdigest()[:10]
    filename = Path("{}-{}-{}.html".format(parsed_url.netloc, filename, hashed_query))

    filename.write_bytes(r.content)
    pages = split_html(filename)
    os.remove(filename)

    txt_path = saving_path.joinpath(f"{filename.stem}.txt")
    write_pages(txt_path, pages)



