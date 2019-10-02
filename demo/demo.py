import soco
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g, jsonify

app = Flask(__name__, static_url_path="")
static_file_dir = join(dirname(realpath(__file__)), "web")


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


#################
# API ENDPOINTS #
#################


@app.route("/api/get_speaker_list")
def get_speaker_list():
    return jsonify(sorted(list(g.keys())))


@app.route("/api/<room>/pause")
def pause(room):
    for k in g:
        print(k)
        g[k].pause()
    return "OK"


@app.route("/api/<room>/play")
def play(room):
    for k in g:
        if k != room:
            g[k].pause()  # every other room should be off.
        else:
            g[k].play()
    return "OK"


# TODO: Select current speaker
# TODO: View current playing song
# TODO: Play/Pause, Skip forward, Skip Backward
# TODO: Select playlist 1
# TODO: Select playlist 2
# TODO: View upcoming songs in a list.

if __name__ == "__main__":
    TESTING_MODE = False

    # discover all the speaker zones:
    if TESTING_MODE:
        print("You are in testing mode.")
    else:
        speakers = soco.discover()
        assert speakers is not None, "Error: no speakers found."
        g = {z.player_name: z for z in speakers}

    # run the main flask app:
    app.run(host="0.0.0.0", port=8080, debug=True)
