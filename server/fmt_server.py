import os, pathlib, zipfile, io
from flask import Flask, abort, safe_join, send_file, request
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["DEFAULT_PATH"] = str(Path.home().joinpath("dev/fiverr/"))

pathlib.Path(app.config["DEFAULT_PATH"]).mkdir(exist_ok=True)

@app.route("/pull/<path:path>", methods=['GET'])
def pull(path):
    filename = os.path.abspath(app.config["DEFAULT_PATH"], path).split("/")[-1]
    safe_path = safe_join(app.config["DEFAULT_PATH"], path)
    try:
        if os.path.isdir(safe_path):
            memory_file = io.BytesIO()
            zip_file = zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED)
            zipdir(safe_path, zip_file)
            zip_file.close()
            memory_file.seek(0)
        else:
            return send_file(safe_path, mimetype= safe_path.split('.')[-1], as_attachment=True)
    except FileNotFoundError:
        abort(404, "directory not found!")
    
    try:
        return send_file(memory_file, attachment_filename=filename + ".zip", as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route("/push/<path:path>", methods=["POST"])
def push(path):
    print(path)
    path = "" if path == "none" else path
    print(request.files)
    file = request.files["file"]
    safe_path = safe_join(app.config["DEFAULT_PATH"], path)
    pathlib.Path(safe_path).mkdir(exist_ok=True)
    if file:
        filename = secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(safe_path, filename))
        if ".zip" in filename:
            with zipfile.ZipFile(os.path.join(safe_path, filename), "r") as zip_ref:
                zip_ref.extractall(safe_path)
                os.remove(os.path.join(safe_path, filename))
        return "saved file", 200
    return "no file found", 404

def zipdir(path, ziph):
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

app.run()

