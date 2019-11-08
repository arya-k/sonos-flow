import pickle
import spotipy
import numpy as np
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials
from scipy import spatial

#############
# CONSTANTS #
#############

USER_ID = "<FILL IN USER ID HERE>"

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
    # "popularity",
]

#############
# UTILITIES #
#############

# TRACK_IDS_LIST = []

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
        if p["name"] == "SONOS_queue":
            found_playlist = True
            sp.user_playlist_replace_tracks(USER_ID, p["id"], track_ids)

    if not found_playlist:
        print("ERROR: Couldn't find the the playlist")

    return track_ids


#############
# ALGORITHM #
#############


def gen_data_files(csv_metadata_headers, csv_vector_headers):

    import pandas as pd

    # read the data file:
    raw_csv = pd.read_csv("SpotifyAudioFeaturesApril2019.csv")
    # raw_csv = pd.read_csv("newdata.csv")
    print("reading", raw_csv)

    # generate data subfiles.
    data_metadata = []
    data_vectors = []

    for vals in raw_csv.itertuples():
        data_metadata.append([vals._asdict()[k] for k in csv_metadata_headers])
        data_vectors.append(np.array([vals._asdict()[k] for k in csv_vector_headers]))

    with open("data.pkl", "wb") as f:
        pickle.dump(
            {
                "data_vectors": data_vectors,
                "data_metadata": data_metadata,
                "track_id_to_index": {t[1]: i for i, t in enumerate(data_metadata)},
                "tree": spatial.KDTree(data_vectors),
            },
            f,
        )


def load_tree():
    with open("data.pkl", "rb") as f:
        return pickle.load(f)


#####################
# EXPOSED FUNCTIONS #
#####################


def get_auth():
    """ Returns an authorized spotify token. """

    # client_credentials_manager = SpotifyClientCredentials()
    scope = "playlist-modify-public"
    token = util.prompt_for_user_token(
        "<YOUR USERNAME>",
        scope,
        client_id="<YOUR CLIENT ID>",
        client_secret="<YOUR CLIENT SECRET>",
        redirect_uri="http://localhost/",
    )
    return spotipy.Spotify(auth=token)


def get_sonos_playlist_names(sp):
    all_playlists = filter(
        lambda p: p["name"].startswith("SONOS_"), sp.user_playlists(USER_ID)["items"]
    )

    return [p["name"].split("SONOS_")[1] for p in all_playlists]


def get_playlist_vector(sp, track_ids, track_id_to_index, data_vectors):
    """ Return the average vector for a whole playlist. """

    to_ret = np.zeros(len(csv_vector_headers))
    for track_id in track_ids:
        to_ret += data_vectors[track_id_to_index[track_id]]

    return to_ret / float(len(track_ids))

def blend_playlists(sp, playlist1, playlist2, matching_data, num_tracks=30):
    """ Given two playlist names, gets the average playlist vector. """
    playlists = sp.user_playlists(USER_ID)["items"]

    p1_vector = []
    p2_vector = []

    for playlist in playlists:
        if playlist["name"].lower() in [playlist1.lower(), playlist2.lower()]:

            all_track_ids = []

            results = sp.user_playlist(USER_ID, playlist["id"], fields="tracks,next")
            tracks = results["tracks"]

            all_track_ids += [t["track"]["id"] for t in tracks["items"]]

            while tracks["next"]:
                tracks = sp.next(tracks)
                all_track_ids += [t["track"]["id"] for t in tracks["items"]]

            if playlist["name"].lower() == playlist1.lower():
                p1_vector = all_track_ids.copy()

            if playlist["name"].lower() == playlist2.lower():
                p2_vector = all_track_ids.copy()

    indexes = matching_data["tree"].query(
        [
            (
                get_playlist_vector(
                    sp,
                    p1_vector,
                    matching_data["track_id_to_index"],
                    matching_data["data_vectors"],
                )
                + get_playlist_vector(
                    sp,
                    p2_vector,
                    matching_data["track_id_to_index"],
                    matching_data["data_vectors"],
                )
            )
            / 2.0
        ],
        num_tracks,
    )[1]

    tracks = sp.tracks(matching_data["data_metadata"][i][1] for i in indexes.flatten())[
        "tracks"
    ]

    track_ids = [matching_data["data_metadata"][i][1] for i in indexes.flatten()]
    add_to_playlist(sp, "SONOS_queue", track_ids)

    album_art = [t["album"]["images"][0]["url"] for t in tracks]
    song_metadata = [matching_data["data_metadata"][i] for i in indexes.flatten()]

    return [
        {"track_ids": track_ids, "matching_data": matching_data, "indexes": indexes}
    ]

def blend_merge_pt_2(sp, track_ids, matching_data, indexes):
    
    tracks = sp.tracks(track_ids)["tracks"]
    
    album_art = [t["album"]["images"][0]["url"] for t in tracks]
    song_metadata = [matching_data["data_metadata"][i] for i in indexes.flatten()]
    

    return [
        {"title": title, "artist": artist, "album": album_art}
        for (artist, _, title), album_art in zip(song_metadata, album_art)
    ]


def ripple_merge_playlists(sp, playlist1, playlist2, matching_data, num_tracks=30):
    """ Literally just merge the first n songs of the playlists"""
    playlists = sp.user_playlists(USER_ID)["items"]

    p1_vector = []
    p2_vector = []

    for playlist in playlists:
        if playlist["name"].lower() in [playlist1.lower(), playlist2.lower()]:

            all_track_ids = []

            results = sp.user_playlist(USER_ID, playlist["id"], fields="tracks,next")
            tracks = results["tracks"]

            all_track_ids += [t["track"]["id"] for t in tracks["items"]]

            while tracks["next"]:
                tracks = sp.next(tracks)
                all_track_ids += [t["track"]["id"] for t in tracks["items"]]

            if playlist["name"].lower() == playlist1.lower():
                p1_vector = all_track_ids.copy()

            if playlist["name"].lower() == playlist2.lower():
                p2_vector = all_track_ids.copy()

    accepted_trackids = [p for p12 in zip(p1_vector, p2_vector) for p in p12][
        :num_tracks
    ]

    tracks = sp.tracks(accepted_trackids)["tracks"]
    album_art = [t["album"]["images"][0]["url"] for t in tracks]
    song_metadata = [
        matching_data["data_metadata"][
            matching_data["track_id_to_index"][trackid["id"]]
        ]
        for trackid in tracks
    ]

    track_ids = accepted_trackids
    # self.TRACK_IDS_LIST = track_ids
    add_to_playlist(sp, "SONOS_queue", track_ids)

    return track_ids

    # return [
    #     {"title": title, "artist": artist, "album": album_art}
    #     for (artist, _, title), album_art in zip(song_metadata, album_art)
    # ]

def ripple_merge_pt_2(sp, track_ids, matching_data):
    tracks = sp.tracks(track_ids)["tracks"]
    album_art = [t["album"]["images"][0]["url"] for t in tracks]
    song_metadata = [
        matching_data["data_metadata"][
            matching_data["track_id_to_index"][trackid["id"]]
        ]
        for trackid in tracks
    ]

    return [
        {"title": title, "artist": artist, "album": album_art}
        for (artist, _, title), album_art in zip(song_metadata, album_art)
]


########
# MAIN #
########

if __name__ == "__main__":
    sp = get_auth()
    gen_data_files(csv_metadata_headers, csv_vector_headers)

    matching_data = load_tree()
