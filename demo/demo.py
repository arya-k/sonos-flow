import soco
from spotify import get_auth, get_sonos_playlist_names
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g, request, jsonify


#################
# SERVING FILES #
#################

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
    return jsonify(sorted(list(g["zones"].keys())))


@app.route("/api/<zone>/is_playing")
def is_playing(zone):
    if zone in g["zones"]:
        return g["zones"][zone].coordinator.get_current_transport_info()
    else:
        return "PLAYING"


@app.route("/api/<zone>/pause")
def pause(zone):
    for k in g["zones"]:
        g["zones"][k].coordinator.pause()
    return "OK"


@app.route("/api/<zone>/play")
def play(zone):
    for k in g["zones"]:
        if k != zone:
            g["zones"][k].coordinator.pause()  # every other room should be off.
        else:
            g["zones"][k].coordinator.play()
    return "OK"


@app.route("/api/<zone>/next")
def next_track(zone):
    if zone in g["zones"]:
        play(zone)
        g["zones"][zone].coordinator.next()
    return "OK"


@app.route("/api/<zone>/previous")
def previous_track(zone):
    if zone in g["zones"]:
        play(zone)
        g["zones"][zone].coordinator.previous()
    return "OK"


@app.route("/api/<zone>/currently_playing")
def currently_playing(zone):
    if zone in g["zones"]:
        track_info = g["zones"][zone].coordinator.get_current_track_info()
        if track_info["title"]:  # song is found.
            return jsonify(track_info)
    return jsonify({})


@app.route("/api/get_playlists")
def get_playlists():
    return jsonify(get_sonos_playlist_names(g["auth"]))


@app.route("/api/upcoming", methods=["POST"])
def upcoming():
    print(request.form)
    # Assert all arguments are passed:
    if not "p1" in request.form:
        return "ERROR: missing p1"
    elif not "p2" in request.form:
        return "ERROR: missing p2"
    elif not "method" in request.form:
        return "ERROR: missing method"
    elif not "room" in request.form:
        return "ERROR: missing room"

    # Assert the mewthod exists.
    if request.form["method"] not in ["ripple", "shuffle"]:
        return "ERROR: method must be one of ['ripple', 'shuffle']"

    # TODO: apply actual intelligence to this.
    return jsonify([g["rooms"][request.form["room"]].get_current_track_info() for _ in range(10)])


# TODO: Select playlist 1
# TODO: Select playlist 2
# TODO: View upcoming songs in a list.

if __name__ == "__main__":
    speakers = soco.discover()
    assert speakers is not None, "Error: no speakers found."

    g = {
        "rooms": {z.player_name: z for z in speakers},
        "zones": {
            "+".join(x.player_name for x in z.members): z
            for z in list(speakers)[0].all_groups
        },
        "auth": get_auth(),
    }

    app.run(host="0.0.0.0", port=8080, debug=True)
