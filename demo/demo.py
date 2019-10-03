import soco
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g, request, jsonify

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
    return jsonify(sorted(list(g["rooms"].keys())))


@app.route("/api/<room>/pause")
def pause(room):
    for k in g["rooms"]:
        g["rooms"][k].pause()
    return "OK"


@app.route("/api/<room>/play")
def play(room):
    for k in g["rooms"]:
        if k != room:
            g["rooms"][k].pause()  # every other room should be off.
        else:
            g["rooms"][k].play()
    return "OK"


@app.route("/api/<room>/next")
def next(room):
    if room in g["rooms"]:
        play(room)
        g["rooms"][room].next()
    return "OK"


@app.route("/api/<room>/previous")
def previous(room):
    if room in g["rooms"]:
        play(room)
        g["rooms"][room].previous()
    return "OK"


@app.route("/api/<room>/currently_playing")
def currently_playing(room):
    if room in g["rooms"]:
        track_info = g["rooms"][room].get_current_track_info()
        if track_info["title"]:  # song is found.
            return jsonify(track_info)
    return jsonify({})


@app.route("/api/upcoming", methods=["POST"])
def upcoming():
    # Assert all arguments are passed:
    if not "playlist1" in request.args:
        return "ERROR: missing playlist1"
    elif not "playlist2" in request.args:
        return "ERROR: missing playlist2"
    elif not "method" in request.args:
        return "ERROR: missing method"

    # Assert the method exists.
    if request.args.method not in ["ripple", "shuffle"]:
        return "ERROR: method must be one of ['ripple', 'shuffle']"

    # TODO: apply actual intelligence to this.
    return jsonify([g["rooms"]["room1"].get_current_track_info() for _ in range(10)])


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
        g = {"rooms": {z.player_name: z for z in speakers}}

    app.run(host="0.0.0.0", port=8080, debug=True)
