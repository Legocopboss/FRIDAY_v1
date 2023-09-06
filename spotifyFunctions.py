import json.decoder
import logging
import os
import base64
import random
import string
import requests

import spotifyOAuth

#import spotifyOAuth

client_id = str(os.getenv("SPOTIFY_CLIENT_ID"))
client_secret = str(os.getenv("SPOTIFY_CLIENT_SECRET"))
state = ''.join(random.choices(string.ascii_letters, k=16))
code = str(os.getenv("SPOTIFY_CODE"))
refreshToken = str(os.getenv("SPOTIFY_REFRESH_TOKEN"))
accessToken = None
scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-playback-position user-top-read  user-read-recently-played user-library-modify user-library-read'


def newOAuth():
    global accessToken

    spotifyOAuth.oAuth()

    encoded_creds = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")

    resp = requests.post(
        url="https://accounts.spotify.com/api/token",
        data={'grant_type': 'authorization_code', 'code': str(os.getenv("SPOTIFY_CODE")),
              'redirect_uri': 'http://localhost'},
        headers={'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + encoded_creds}
    )

    try:
        accessToken = resp.json()["access_token"]
        if "refresh_token" in resp.json():
            os.environ["SPOTIFY_REFRESH_TOKEN"] = resp.json()["refresh_token"]
    except KeyError:
        logging.error("Error retrieving new authorization code")

def getAccessToken():
    global accessToken
    encoded_creds = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")

    print("attempting refresh token")
    resp = requests.post(
        url = "https://accounts.spotify.com/api/token",
        data = {'grant_type': 'refresh_token', 'refresh_token': str(os.getenv("SPOTIFY_REFRESH_TOKEN"))},
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + encoded_creds}
    )

    try:
        accessToken = resp.json()["access_token"]
        if "refresh_token" in resp.json():
            os.environ["SPOTIFY_REFRESH_TOKEN"] = resp.json()["refresh_token"]
            print(resp.json()["refresh_token"])
    except KeyError:
        print("failed refresh token. attempting auth code")

        resp = requests.post(
            url="https://accounts.spotify.com/api/token",
            data={'grant_type': 'authorization_code', 'code': str(os.getenv("SPOTIFY_CODE")),
                  'redirect_uri': 'http://localhost'},
            headers={'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + encoded_creds}
        )

        try:
            accessToken = resp.json()["access_token"]
            if "refresh_token" in resp.json():
                os.environ["SPOTIFY_REFRESH_TOKEN"] = resp.json()["refresh_token"]
                print(resp.json()["refresh_token"])
        except KeyError:
            print("failed auth code. getting new auth code")
            newOAuth()


if accessToken is None:
    getAccessToken()
header = {'Authorization': 'Bearer ' + accessToken}

def getMyPlaylists():
    resp = requests.get(
        url = "https://api.spotify.com/v1/me/playlists",
        headers = header
    )
    return str([{"name": x["name"], "playlist_id": x["uri"]} for x in resp.json()["items"]])

def getCurrentlyPlaying():
    resp = requests.get(
        url = "https://api.spotify.com/v1/me/player/currently-playing?market=US",
        headers = header
    )
    return resp.json()


def musicQuery(query, device_id, adjustment=None):
    method = "PUT"
    data = None
    if query == "player" or query == "currently-playing":
        if query == "player": query = ""
        resp = requests.get(
            url=f"https://api.spotify.com/v1/me/player/{query}",
            headers=header,
        )
        return str(resp.json())
    elif query == "next" or query == "previous": method = "PUSH"
    if query == 'volume': query+=f'?volume_percent={adjustment}'
    if query == 'play' and adjustment is not None:
        if device_id != 'None': query += f"?device_id={device_id}"
        resp = requests.request(
            method=method,
            url=f"https://api.spotify.com/v1/me/player/{query}",
            headers=header,
            data = {"context_uri": adjustment}
        )
        if str(resp.json()) is not None:
            return str(resp.json())
        else:
            return "Successfully executed command"
    resp = requests.request(
        method= method,
        url = f"https://api.spotify.com/v1/me/player/{query}",
        headers = header,
    )
    if str(resp.json()) is not None:
        return str(resp.json())
    else:
        return "Successfully executed command"


def newMusicQuery(endpoint, method, queryParams=None, body=None):
    try:
        response = requests.request(
            method=method,
            url = f'https://api.spotify.com/v1/{endpoint}',
            headers = header,
            params= queryParams,
            data = body,
        )
        print(response)
        if response.status_code == 204:
            return "Successful API Call"
        else:
            return str(response.json())
    except:
        raise RuntimeError("Failed to make Spotify API request")




def getActiveDevices():
    resp = requests.get(
        url="https://api.spotify.com/v1/me/player/devices",
        headers = header
    )
    return str(resp.json()['devices'])

#print(musicQuery('play', 'None'))