# acapella_backend/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import requests
import yt_dlp
import uuid
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'  # Replace with env-secured key

@app.route('/playlist', methods=['GET'])
def get_playlist():
    playlist_url = request.args.get('url')
    if not playlist_url:
        return jsonify({'error': 'Query parameter "url" is required'}), 400

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            videos = []
            for entry in info.get('entries', []):
                videos.append({
                    'title': entry.get('title'),
                    'id': entry.get('id'),
                    'url': f'https://www.youtube.com/watch?v={entry.get("id")}'
                })

            return jsonify({'playlist_title': info.get('title'), 'results': videos})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_playlists_html', methods=['GET'])
def search_playlists_html():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+playlist&sp=EgIQAw%253D%253D"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Not perfect — YouTube uses JS for most content — we’d need yt-dlp or Selenium for full results
        titles = [tag.text for tag in soup.select('a#video-title')]
        return jsonify({'results': titles[:5]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_playlists', methods=['GET'])
def search_playlists():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'skip_download': True,
        'default_search': f"ytsearchdate5:{query}",  # Prioritize newer results
    }

    playlists = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            entries = info.get('entries', [])
            print(entries)
            for entry in entries:
                if entry.get('_type') == 'playlist':
                    playlists.append({
                        'title': entry.get('title'),
                        'uploader': entry.get('uploader'),
                        'playlist_url': f"https://www.youtube.com/playlist?list={entry.get('id')}"
                    })

        if not playlists:
            return jsonify({'message': 'No playlists found.', 'results': []}), 200

        return jsonify({'results': playlists})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search', methods=['GET'])
def search_youtube():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
        'default_search': 'ytsearch5'
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            for entry in info.get('entries', []):
                results.append({
                    'id': entry.get('id'),
                    'title': entry.get('title'),
                    'url': f'https://www.youtube.com/watch?v={entry.get("id")}'
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'results': results})

@app.route('/search_acapella', methods=['GET'])
def search_acapella_youtube():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
        'default_search': 'ytsearch5'
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(query)+" acapella version", download=False)
            for entry in info.get('entries', []):
                results.append({
                    'id': entry.get('id'),
                    'title': entry.get('title'),
                    'url': f'https://www.youtube.com/watch?v={entry.get("id")}'
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'results': results})



if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('acapellas', exist_ok=True)
    app.run(debug=True)
