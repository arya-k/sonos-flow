from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g

app = Flask(__name__, static_url_path="")
static_file_dir = join(dirname(realpath(__file__)), "static")


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


@app.route("/static/<path:path>")
def send_statics(path):
    return send_from_directory("static", path)


@app.route("/api/temp")
def temp_api():
    g["Room"] = g.get("Room", 0)
    return "Room set to {}".format(g["Room"])


@app.route("/api/beep/<speaker_id>")
def beep(speaker_id):
    """ Makes the speaker with a certain ID, beep to
    indicate that the music is changing. """
    # TODO: this.


@app.route("/api/update_room/<phone_id>/<speaker_id>")
def update_room(phone_id, speaker_id):
    """ Adds the phones to the global context. Accordingly
        adjusts the music playing in each room, to match
        what all the users in the room would want to hear
        using the favorites API. """
    # TODO: this


def gather_rooms():
    """ Using the Sonos API, turns each speaker into
        its own group, and saves those rooms to the 
        global context. Each speaker has a UID, which
        is also linked to an NFC tag. The exact 
        implementation of this is unclear. """
    # TODO: this


if __name__ == "__main__":
    g = {"rooms": gather_rooms()}
    app.run(host="0.0.0.0", port=3000, debug=True)
