import soco
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g

app = Flask(__name__, static_url_path="")
static_file_dir = join(dirname(realpath(__file__)), "control")


@app.route("/")
def main_page():
    return "TODO: THIS"
    return send_from_directory(static_file_dir, "index.html")


@app.route("/api/<room>/pause")
def pause(room):
    if room in g:
        g[room].pause()
    return "OK"


@app.route("/api/<room>/play")
def play(room):
    if room in g:
        g[room].play()
    return "OK"


if __name__ == "__main__":
    g = {z.player_name: z for z in soco.discover()}
    app.run(host="0.0.0.0", port=3000, debug=True)
