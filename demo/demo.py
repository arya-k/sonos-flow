import soco
from soco.music_services import MusicService
from spotify import (
    get_auth,
    get_sonos_playlist_names,
    ripple_merge_playlists,
    ripple_merge_pt_2,
    blend_playlists,
    blend_merge_pt_2,
    load_tree,
)
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


@app.route("/api/upcoming/<p1>/<p2>/<method>")
def upcoming(p1, p2, method):
    if method == "ripple":
        track_ids = ripple_merge_playlists(
                g["auth"],
                "SONOS_" + p1,
                "SONOS_" + p2,
                g["matching_data"],
                num_tracks=30,
            )
        
        update_queue(track_ids)
        return jsonify(ripple_merge_pt_2(
                g["auth"],
                track_ids,
                g["matching_data"]
                ))

    if method == "blend":
        json = blend_playlists(
                g["auth"],
                "SONOS_" + p1,
                "SONOS_" + p2,
                g["matching_data"],
                num_tracks=30,
            )
        update_queue(json[0]["track_ids"])
        return jsonify(blend_merge_pt_2(g["auth"], json[0]["track_ids"], json[0]["matching_data"], json[0]["indexes"]))

    return "ERROR: method must be one of ['ripple', 'shuffle']"

def update_queue(track_ids):
    # print(track_ids)
    full_sonos_uri = "x-sonos-spotify:spotify%3atrack%3a"
    uri_end = "?sid=12flags=8224&sn=1"
    for zone in g["zones"]:
        # print(g["zones"][zone].coordinator.get_current_transport_info())
        if (g["zones"][zone].coordinator.get_current_transport_info()['current_transport_state']):
            g["zones"][zone].coordinator.clear_queue()
            for uri in track_ids:
                sonos_uri = full_sonos_uri + uri + uri_end
                # print(sonos_uri)
                g["zones"][zone].coordinator.add_uri_to_queue(sonos_uri)


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
        "matching_data": load_tree(),
    }

    app.run(host="0.0.0.0", port=8080, debug=True)
