from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


CLIENT_ID = os.environ.get("CLIENT_ID_SPOTIFY")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET_SPOTIFY")


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD\n")

print("Please wait, it will take a while ;)\n")

billboard_url = f"https://www.billboard.com/charts/hot-100/{date}"
response = requests.get(url=billboard_url)
soup = BeautifulSoup(response.text, "html.parser")
songs_list = [
    song.getText()
    for song in soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")
]
artists_list = [
    artist.getText().replace("Featuring", "feat")
    for artist in soup.find_all(
        name="span", class_="chart-element__information__artist text--truncate color--secondary"
    )
]


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://example.com/callback/",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
    )
)
user_id = sp.current_user()["id"]


songs_uri = []
for index, song in enumerate(songs_list):
    try:
        result = sp.search(q=f"{song} {artists_list[index]} ", limit=1, offset=1, type="track")
        songs_uri.append(result["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")


playlist_name = f"{date} Billboard 100"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
playlist_id = playlist["id"]

sp.playlist_add_items(playlist_id=playlist_id, items=songs_uri)

print(f"\nHere is link for your playlist: {playlist['external_urls']['spotify']}")
