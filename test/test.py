import os
import requests

# === CONFIGURATION ===
BASE_URL = "http://127.0.0.1:5000"
SEARCH_QUERY = "trop parler"

def test_search():
    print("🔍 Testing /search...")
    response = requests.get(f"{BASE_URL}/search", params={"q": SEARCH_QUERY})
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            print(f"✅ Found {len(results)} results.")
            return results  # Return results
        else:
            print("❌ No search results.")
            return None
    else:
        print(f"❌ Search failed: {response.status_code} - {response.text}")
        return None

def test_process(video_url):
    print("🎵 Testing /process...")
    payload = {
        "url": video_url
    }
    response = requests.post(f"{BASE_URL}/process", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Process Success: {data}")
    else:
        print(f"❌ Process failed: {response.status_code} - {response.text}")

def test_youtube_playlist():
    print("📺 Testing /playlist...")

    YOUTUBE_PLAYLIST_URL = "https://music.youtube.com/playlist?list=PL5Ul7b7LCxhyMRsITIKlukrgfFXaPemXm&si=Ielnrgczn11asOE-"  # Replace with a real public playlist URL

    response = requests.get(f"{BASE_URL}/playlist", params={"url": YOUTUBE_PLAYLIST_URL})
    if response.status_code == 200:
        data = response.json()
        playlist_title = data.get("playlist_title")
        videos = data.get("results", [])
        
        

        print(f"✅ Playlist: {playlist_title}")
        print(f"🎵 Found {len(videos)} videos:")
        for i, video in enumerate(videos[:5], 1):  # Show first 5 only
            print(f"{i}. {video['title']} → {video['url']}")
        return videos
        
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    test_process("https://www.youtube.com/watch?v=k4yXQkG2s1E")
