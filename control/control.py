import soco
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g

app = Flask(__name__, static_url_path="")
static_file_dir = dirname(realpath(__file__))


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


# Serving Files
@app.route("/music/connected.mp3")
def connected_music():
    return send_from_directory(static_file_dir, "connected.mp3")


@app.route("/music/disconnected.mp3")
def disconnected_music():
    return send_from_directory(static_file_dir, "disconnected.mp3")


# API Endpoints
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


@app.route("/api/<room>/connected")
def connected(room):
    if room in g:
        g[room].play_uri("AryasMacbook.local:3000/music/connected.mp3")
    return "OK"


@app.route("/api/<room>/disconnected")
def disconnected(room):
    if room in g:
        g[room].play_uri("AryasMacbook.local:3000/music/disconnected.mp3")
    return "OK"


if __name__ == "__main__":

    # discover all the speakers:
    speakers = soco.discover()
    if speakers is not None:
        g = {z.player_name: z for z in speakers}
    else:
        print("No speakers found.")
        print("You are in testing mode.")

    # run the main flask app:
    app.run(host="0.0.0.0", port=3000, debug=True)
