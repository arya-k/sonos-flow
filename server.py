from os.path import join, dirname, realpath
from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path="")


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


@app.route("/static/<path:path>")
def send_statics(path):
    return send_from_directory("static", path)


@app.route("/api/temp")
def temp_api():
    return "I DID A THING."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
