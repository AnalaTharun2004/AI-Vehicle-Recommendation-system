import os
import re
import sqlite3
import time
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATABASE = os.path.join(BASE_DIR, 'database', 'vehicle.db')
IMAGE_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
API_URL = 'https://commons.wikimedia.org/w/api.php'
WIKIPEDIA_SUMMARY_URL = 'https://en.wikipedia.org/api/rest_v1/page/summary/'


def api_request(params):
    query = urlencode({'format': 'json', **params})
    request = Request(
        f'{API_URL}?{query}',
        headers={'User-Agent': 'AI-Vehicle-Recommendation-System/1.0'},
    )
    with urlopen(request, timeout=20) as response:
        return response.read()


def safe_name(brand, model):
    return re.sub(r'[^a-z0-9]+', '-', f'{brand}-{model}'.lower()).strip('-')


def find_image_url(brand, model):
    candidates = [
        f'{brand} {model}',
        f'{brand} {model} car',
        model,
    ]
    for candidate in candidates:
        try:
            request = Request(
                f'{WIKIPEDIA_SUMMARY_URL}{quote(candidate.replace(" ", "_"))}',
                headers={'User-Agent': 'AI-Vehicle-Recommendation-System/1.0'},
            )
            import json
            summary = json.loads(urlopen(request, timeout=20).read())
            image_url = summary.get('thumbnail', {}).get('source')
            if image_url:
                return image_url
        except Exception:
            continue

    search = api_request({
        'action': 'query',
        'generator': 'search',
        'gsrsearch': f'{brand} {model} vehicle',
        'gsrnamespace': 6,
        'gsrlimit': 1,
        'prop': 'imageinfo',
        'iiprop': 'url',
        'iiurlwidth': 900,
    })
    import json
    pages = json.loads(search).get('query', {}).get('pages', {})
    for page in pages.values():
        image_info = page.get('imageinfo', [{}])[0]
        image_url = image_info.get('thumburl') or image_info.get('url')
        if image_url:
            return image_url
    return None


def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    vehicles = conn.execute('SELECT DISTINCT brand, name FROM vehicles ORDER BY brand, name').fetchall()

    for brand, model in vehicles:
        filename = f'{safe_name(brand, model)}.jpg'
        local_path = os.path.join(IMAGE_DIR, filename)
        relative_path = f'uploads/{filename}'
        if not os.path.exists(local_path):
            image_url = None
            try:
                image_url = find_image_url(brand, model)
                if not image_url:
                    print(f'No image found: {brand} {model}')
                    continue
                request = Request(image_url, headers={'User-Agent': 'AI-Vehicle-Recommendation-System/1.0'})
                with urlopen(request, timeout=30) as response, open(local_path, 'wb') as image_file:
                    image_file.write(response.read())
                print(f'Downloaded: {brand} {model}')
                time.sleep(0.25)
            except Exception as error:
                if image_url:
                    conn.execute(
                        'UPDATE vehicles SET image_path = ? WHERE brand = ? AND name = ?',
                        (image_url, brand, model),
                    )
                    print(f'Using remote image: {brand} {model}')
                else:
                    print(f'Failed: {brand} {model}: {error}')
                continue
        conn.execute(
            'UPDATE vehicles SET image_path = ? WHERE brand = ? AND name = ?',
            (relative_path, brand, model),
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()