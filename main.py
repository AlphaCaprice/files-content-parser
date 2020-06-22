from pathlib import Path
from zipfile import ZipFile

from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS
from requests.exceptions import ConnectionError
from werkzeug.utils import secure_filename

from app.utils.io_handler import clear_folder
from app.utils.scripts import process_file, process_link

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")
CORS(app)

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "html", "xml", "htm", "xht", "zip"}
DOWNLOADED = Path("tmp_files/downloaded")
PROCESSED = Path("tmp_files/processed")
ZIP_PATH = Path("tmp_files/zips")
for path in (DOWNLOADED, PROCESSED, ZIP_PATH):
    path.mkdir(exist_ok=True, parents=True)


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")


@app.route('/handler', methods=["POST"])
def handler():
    clear_folder(DOWNLOADED)

    links = request.form["links"]
    files = request.files.getlist("documents")

    if files and files[0].filename:
        for file in files:
            filename = secure_filename(file.filename)
            filename = DOWNLOADED.joinpath(filename)
            file.save(filename)
            process_file(filename, PROCESSED)

    if links:
        links = [link.strip() for link in links.split("\n") if link.strip()]
        for link in links:
            try:
                process_link(link, PROCESSED)
            except ConnectionError:
                print(f"Bad link. Skipped. {link}")

    with ZipFile(ZIP_PATH.joinpath("files.zip"), 'w') as zip_:
        for file in Path(PROCESSED).glob("*"):
            zip_.write(file, arcname=f"files/{file.name}")

    clear_folder(DOWNLOADED)
    clear_folder(PROCESSED)

    return send_from_directory(directory=ZIP_PATH.absolute(),
                               filename="files.zip",
                               attachment_filename="files.zip",
                               as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port="8888")
