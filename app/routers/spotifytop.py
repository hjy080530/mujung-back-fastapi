import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter

load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
# Get an access token from the Spotify API
response = requests.post('https://accounts.spotify.com/api/token', data={'grant_type': 'client_credentials'}, auth=(client_id, client_secret))
access_token = response.json()['access_token']

router = APIRouter()

# Set up the headers for the HTTP GET request
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
}
@router.get("", )
def get_top_tracks():
    # Send the HTTP GET request to the Spotify API for the top tracks
    response = requests.get('https://api.spotify.com/v1/playlists/4cRo44TavIHN54w46OqRVc/tracks?limit=5', headers=headers)
    top_tracks = response.json()['items']
    print("Status:", response.status_code)
    print("Text:", response.text[:500])
    print('Top tracks:',top_tracks)

    # Print out the track names and artists in a nice, formatted table
    print('{:<5} {:<35} {}'.format('Rank', 'Track Name', 'Artist(s)'))
    print('-'*55)

    result = []
    for i, track in enumerate(top_tracks):
        rank = str(i+1) + '.'
        name = track['track']['name']
        artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        print('{:<5} {:<35} {}'.format(rank, name, artists))
        result.append({
            "rank": i + 1,
            "track_name": name,
            "artists": artists
        })
    return result
