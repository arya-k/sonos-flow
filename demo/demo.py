import soco
from os.path import join, dirname, realpath
from flask import Flask, send_from_directory, g

app = Flask(__name__, static_url_path="")
static_file_dir = join(dirname(realpath(__file__)), "web")


@app.route("/")
def main_page():
    return send_from_directory(static_file_dir, "index.html")


#################
# API ENDPOINTS #
#################

# TODO: Select current speaker
# TODO: View current playing song
# TODO: Play/Pause, Skip forward, Skip Backward
# TODO: Select playlist 1
# TODO: Select playlist 2
# TODO: View upcoming songs in a list.

if __name__ == "__main__":
    # run the main flask app:
    app.run(host="0.0.0.0", port=8080, debug=True)
