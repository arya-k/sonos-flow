from os.path import join, dirname, realpath
from flask import Flask, send_from_directory

app = Flask(__name__)
static_file_dir = join(dirname(realpath(__file__)), "static")


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


@app.route("/api/temp")
def temp_api():
    return "I DID A THING."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
