from flask import Blueprint, request, jsonify
import os
import uuid
import yt_dlp
import requests
from bs4 import BeautifulSoup
from src.utils.lalalai_splitter import batch_process

routes = Blueprint('routes', __name__)

@routes.route('/process', methods=['POST'])
def process_song():
    data = request.get_json()
    youtube_url = data.get('url')
    lalal_license = os.getenv('lalalal_ai_license')
    if not youtube_url or not lalal_license:
        return jsonify({'error': 'URL and license required'}), 400

    filename = f"./downloads/{uuid.uuid4()}.mp3"
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': filename,
            'quiet': True,
            'ffmpeg_location': "C:/Users/galga/Downloads/ffmpeg-2025-06-04-git-a4c1a5b084-essentials_build/ffmpeg-2025-06-04-git-a4c1a5b084-essentials_build/bin",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except Exception as e:
        return jsonify({'error': f'Failed to download audio: {str(e)}'}), 500

    try:
        output_dir = os.path.join('acapellas', os.path.splitext(os.path.basename(filename))[0])
        os.makedirs(output_dir, exist_ok=True)
        batch_process(lalal_license, filename + '.mp3', output_dir, 'vocals', 'orion', False, 1)
    except Exception:
        return jsonify({'error': 'Lalal.ai processing failed'}), 500

    return jsonify({'message': 'Success', 'path': output_dir})

@routes.route('/playlist', methods=['GET'])
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

@routes.route('/search_playlists_html', methods=['GET'])
def search_playlists_html():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+playlist&sp=EgIQAw%253D%253D"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        titles = [tag.text for tag in soup.select('a#video-title')]
        return jsonify({'results': titles[:5]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes.route('/search_playlists', methods=['GET'])
def search_playlists():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'skip_download': True,
        'default_search': f"ytsearchdate5:{query}"
    }
    playlists = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            entries = info.get('entries', [])
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

@routes.route('/search', methods=['GET'])
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

def register_routes(app):
    app.register_blueprint(routes)
