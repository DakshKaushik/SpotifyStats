from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, redirect, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  


client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

if not client_id or not client_secret or not redirect_uri:
    raise ValueError("Missing environment variables for Spotify credentials")

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-library-read user-top-read"
)

@app.route('/')
def home():
    if not session.get('token_info'):
        return render_template('home.html')
    return redirect(url_for('top_tracks')) 

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('top_tracks'))

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('home')) 

@app.route('/top-tracks')
def top_tracks():
    if not session.get('token_info'):
        return redirect(url_for('home')) 

    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    time_range = request.args.get('time_range', 'medium_term')  
    results = sp.current_user_top_tracks(time_range=time_range, limit=20) 
    return render_template('top-tracks.html', tracks=results['items'], time_range=time_range) 

@app.route('/top-artists')
def top_artists():
    if not session.get('token_info'):
        return redirect(url_for('home'))  

    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    time_range = request.args.get('time_range', 'medium_term') 
    results = sp.current_user_top_artists(time_range=time_range, limit=20)  
    return render_template('top-artists.html', artists=results['items'], time_range=time_range)  

@app.route('/top-genres')
def top_genres():
    if not session.get('token_info'):
        return redirect(url_for('home')) 

    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    time_range = request.args.get('time_range', 'medium_term') 
    results = sp.current_user_top_artists(time_range=time_range, limit=50)  
    genres = {}
    for artist in results['items']:
        for genre in artist['genres']:
            genres[genre] = genres.get(genre, 0) + 1 
    sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)  
    return render_template('top-genres.html', genres=sorted_genres[:20], time_range=time_range)

if __name__ == '__main__':
    app.run(debug=True)  
