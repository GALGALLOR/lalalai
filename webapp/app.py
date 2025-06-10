from flask import Flask, render_template, request, redirect, url_for
from tools.api import lalalai_splitter
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)


def search_youtube(query, max_results=5, search_type='video'):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
    }
    results = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        for entry in info.get('entries', []):
            if search_type == 'playlist' and entry.get('_type') != 'playlist':
                continue
            if search_type == 'video' and entry.get('_type') == 'playlist':
                continue
            results.append({'title': entry.get('title'), 'url': entry.get('url') or entry.get('webpage_url')})
    return results


def download_audio(url):
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    return file_path, temp_dir


def convert_file(path, license_key, stem='vocals', filter_type=1, splitter='phoenix'):
    output_dir = tempfile.mkdtemp()
    lalalai_splitter.batch_process_for_file(license_key, path, output_dir, stem, filter_type, splitter)
    files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
    return files


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = search_youtube(query)
    return render_template('search.html', results=results)


@app.route('/search_playlist', methods=['GET', 'POST'])
def search_playlist():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            results = search_youtube(query, search_type='playlist')
    return render_template('search_playlist.html', results=results)


@app.route('/convert_song', methods=['GET', 'POST'])
def convert_song():
    results = []
    if request.method == 'POST':
        url = request.form.get('url')
        license_key = request.form.get('license')
        if url and license_key:
            file_path, _ = download_audio(url)
            results = convert_file(file_path, license_key)
    return render_template('convert_song.html', results=results)


@app.route('/convert_playlist', methods=['GET', 'POST'])
def convert_playlist():
    results = []
    if request.method == 'POST':
        url = request.form.get('url')
        license_key = request.form.get('license')
        if url and license_key:
            videos = search_youtube(url, search_type='video')
            for video in videos:
                file_path, _ = download_audio(video['url'])
                results.extend(convert_file(file_path, license_key))
    return render_template('convert_playlist.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
