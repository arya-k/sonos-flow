import soco
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g

app = Flask(__name__, static_url_path="")
static_file_dir = dirname(realpath(__file__))


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


# Serve mp3 files.
@app.route("/music/<music_name>.mp3")
def serve_music(music_name):
    return send_from_directory(static_file_dir, "{}.mp3".format(music_name))


#################
# API ENDPOINTS #
#################


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
    TESTING_MODE = True

    # discover all the speaker zones:
    if TESTING_MODE:
        print("You are in testing mode.")
    else:
        speakers = soco.discover()
        assert speakers is not None, "Error: no speakers found."
        g = {z.player_name: z for z in speakers}

    # run the main flask app:
    app.run(host="0.0.0.0", port=3000, debug=True)
