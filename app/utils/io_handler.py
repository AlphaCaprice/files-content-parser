import os
import shutil
from pathlib import Path
from typing import List


def clear_folder(path: str) -> None:
    """Deletes all files in the directory"""
    shutil.rmtree(path)
    os.mkdir(path)


def write_pages(save_path: Path, pages: List[List[str]]) -> None:
    """Writes 
    
    Args:
        save_path: where to save data
        pages: strings chunks
    """
    whole_text = "\n\n".join([paragraph for page in pages for paragraph in page])
    save_path.write_text(whole_text, encoding="utf-8")
