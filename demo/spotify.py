"""

Meant to emulate actually using spotify live.

thearyaskumar@icloud.com -> 21oobpw6ffqofvcjwggcrkxey

"""

import spotipy
import spotipy.util as util
import pickle
from scipy import spatial

#############
# CONSTANTS #
#############

USER_ID = "21oobpw6ffqofvcjwggcrkxey"

csv_metadata_headers = ["artist_name", "track_id", "track_name"]

csv_vector_headers = [
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "tempo",
    "valence",
    "popularity",
]

#############
# UTILITIES #
#############


def is_playlist_valid(sp, track_ids):
    """ Checks whether the (hardcoded) playlist_uri contains enough valid songs. """
    valid_ids = []

    playlist = sp.user_playlist("<username>", "<playlist_id>")
    for track in playlist["tracks"]["items"]:
        if track["track"]["id"] in track_ids:
            valid_ids.append(track["track"]["id"])

    return valid_ids


def add_to_playlist(sp, playlist_name, track_ids):
    """ Adds the track_ids to the playlist. """
    playlists = sp.user_playlists(USER_ID)
    found_playlist = False
    for p in playlists["items"]:
        if p["name"] == playlist_name:
            found_playlist = True
            sp.user_playlist_add_tracks(USER_ID, p["id"], track_ids)

    if not found_playlist:
        print("ERROR: Couldn't find the the playlist")


#############
# ALGORITHM #
#############


def gen_data_files(csv_metadata_headers, csv_vector_headers):

    import pandas as pd

    # read the data file:
    raw_csv = pd.read_csv("SpotifyAudioFeaturesApril2019.csv")

    # generate data subfiles.
    data_metadata = []
    data_vectors = []

    for vals in raw_csv.itertuples():
        data_metadata.append([vals._asdict()[k] for k in csv_metadata_headers])
        data_vectors.append([vals._asdict()[k] for k in csv_vector_headers])

    with open("data.pkl", "wb") as f:
        pickle.dump((data_metadata, data_vectors), f)


def load_tree():
    # load the files:
    with open("data.pkl", "rb") as f:
        data_metadata, data_vectors = pickle.load(f)

    tree = spatial.KDTree(data_vectors)

    return data_metadata, data_vectors, tree


#####################
# EXPOSED FUNCTIONS #
#####################


def get_auth():
    """ Returns an authorized spotify token. """

    scope = "playlist-modify-public"
    token = util.prompt_for_user_token(
        "thearyaskumar@icloud.com",
        scope,
        client_id="0a2c500ef2514d08a12f0bc13e7d64f2",
        client_secret="38a7c8c848284ca5b6d4f6aa12d26ce5",
        redirect_uri="http://localhost/",
    )

    return spotipy.Spotify(auth=token)


def get_sonos_playlist_names(sp):
    all_playlists = filter(
        lambda p: p["name"].startswith("SONOS_"), sp.user_playlists(USER_ID)["items"]
    )

    return [p["name"].split("SONOS_")[1] for p in all_playlists]


########
# MAIN #
########

if __name__ == "__main__":
    sp = get_auth()
    from pprint import pprint

    pprint(get_sonos_playlists(sp))