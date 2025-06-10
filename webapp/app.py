from flask import Flask, render_template, request, redirect, url_for
import requests

API_BASE = 'http://127.0.0.1:5000'

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('search_song'))

@app.route('/search')
def search_song():
    query = request.args.get('q')
    results = []
    if query:
        r = requests.get(f'{API_BASE}/search', params={'q': query})
        if r.ok:
            results = r.json().get('results', [])
    return render_template('search.html', results=results)

@app.route('/search_playlist')
def search_playlist():
    query = request.args.get('q')
    results = []
    if query:
        r = requests.get(f'{API_BASE}/search_playlists', params={'q': query})
        if r.ok:
            results = r.json().get('results', [])
    return render_template('search_playlist.html', results=results)

@app.route('/convert_song', methods=['GET', 'POST'])
def convert_song():
    result = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            r = requests.post(f'{API_BASE}/process', json={'url': url})
            if r.ok:
                data = r.json()
                result = {'title': url, 'url': data.get('path')}
    return render_template('convert_song.html', result=result)

@app.route('/convert_playlist', methods=['GET', 'POST'])
def convert_playlist():
    results = []
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            resp = requests.get(f'{API_BASE}/playlist', params={'url': url})
            if resp.ok:
                playlist = resp.json().get('results', [])
                for video in playlist:
                    pr = requests.post(f'{API_BASE}/process', json={'url': video['url']})
                    if pr.ok:
                        data = pr.json()
                        results.append({'title': video['title'], 'url': data.get('path')})
    return render_template('convert_playlist.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
