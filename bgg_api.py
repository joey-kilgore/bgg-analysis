"""Small BGG XML API v2 client used to build the collection/plays page.

Requests are authorized with the BGG_TOKEN environment variable. Set
BGG_CACHE_DIR to a folder to cache raw XML responses locally, which makes
iterating on the page fast and avoids hammering the API.
"""
import hashlib
import os
import re
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://boardgamegeek.com/xmlapi2'
THING_BATCH = 20  # BGG rejects more than 20 ids per thing request

_session = requests.Session()
_session.headers['User-Agent'] = 'bgg-analysis-site'
if os.environ.get('BGG_TOKEN'):
    _session.headers['Authorization'] = f"Bearer {os.environ['BGG_TOKEN']}"


def fetch(url, retries=12):
    """GET an XML API url, retrying while BGG queues the request (202) or throttles (429)."""
    cache_dir = os.environ.get('BGG_CACHE_DIR')
    cache_file = None
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, hashlib.sha1(url.encode()).hexdigest() + '.xml')
        if os.path.exists(cache_file):
            with open(cache_file, encoding='utf-8') as f:
                return f.read()

    delay = 3
    for _ in range(retries):
        r = _session.get(url, timeout=60)
        if r.status_code == 401:
            raise RuntimeError('BGG API returned 401 Unauthorized - check that BGG_TOKEN is set and valid')
        queued = r.status_code == 202 or (r.status_code == 200 and '<message>' in r.text[:300])
        if r.status_code == 200 and not queued:
            if cache_file:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(r.text)
            return r.text
        if r.status_code not in (202, 429, 500, 502, 503) and not queued:
            r.raise_for_status()
        print(f'  waiting on BGG ({r.status_code}) for {url}')
        time.sleep(delay)
        delay = min(delay * 2, 30)
    raise RuntimeError(f'BGG never returned data for {url}')


def _soup(text):
    return BeautifulSoup(text, 'xml')


def _num(value, cast=float):
    try:
        v = cast(value)
    except (TypeError, ValueError):
        return None
    return v


def get_collection(username):
    """Return a list of dicts for every board game (not expansion) in the user's collection."""
    text = fetch(f'{BASE_URL}/collection?username={username}&stats=1&excludesubtype=boardgameexpansion')
    games = []
    for item in _soup(text).find_all('item'):
        status = item.find('status')
        stats = item.find('stats')
        rating = item.find('rating')
        rank = item.find('rank', attrs={'name': 'boardgame'})
        games.append({
            'id': int(item['objectid']),
            'name': item.find('name').text.strip(),
            'year': _num(item.find('yearpublished').text, int) if item.find('yearpublished') else None,
            'thumb': item.find('thumbnail').text.strip() if item.find('thumbnail') else None,
            'own': status['own'] == '1',
            'prevowned': status['prevowned'] == '1',
            'fortrade': status['fortrade'] == '1',
            'preordered': status['preordered'] == '1',
            'wanttoplay': status['wanttoplay'] == '1',
            'wishlist': status['wishlist'] == '1',
            'wishpriority': _num(status.get('wishlistpriority'), int),
            'modified': status.get('lastmodified'),
            'numplays': _num(item.find('numplays').text, int) or 0,
            'myrating': _num(rating['value']) if rating else None,
            'bggavg': _num(item.find('average')['value']) if item.find('average') else None,
            'rank': _num(rank['value'], int) if rank else None,
            'minp': _num(stats.get('minplayers'), int) if stats else None,
            'maxp': _num(stats.get('maxplayers'), int) if stats else None,
            'time': _num(stats.get('playingtime'), int) if stats else None,
        })
    return games


_TAG = re.compile(r'#\w+')
_EXPANSIONS = re.compile(r'Played with expansions:.*', re.S)
_THING = re.compile(r'\[thing=\d+\](.*?)\[/thing\]')


def get_plays(username):
    """Return every logged play for the user, newest first."""
    plays = []
    page = 1
    while True:
        soup = _soup(fetch(f'{BASE_URL}/plays?username={username}&page={page}'))
        batch = soup.find_all('play')
        for p in batch:
            item = p.find('item')
            raw = p.find('comments').text if p.find('comments') else ''
            note = _EXPANSIONS.sub('', _TAG.sub('', raw)).strip()
            players = []
            for pl in p.find_all('player'):
                score = _num(pl.get('score'))
                players.append({
                    'name': (pl.get('name') or '').strip(),
                    'username': pl.get('username') or '',
                    'win': pl.get('win') == '1',
                    'new': pl.get('new') == '1',
                    'score': score,
                })
            plays.append({
                'id': int(p['id']),
                'date': p['date'],
                'qty': _num(p.get('quantity'), int) or 1,
                'length': _num(p.get('length'), int) or 0,
                'location': p.get('location') or '',
                'incomplete': p.get('incomplete') == '1',
                'nowinstats': p.get('nowinstats') == '1',
                'game': item['name'],
                'gameId': int(item['objectid']),
                'note': note,
                'expansions': _THING.findall(raw),
                'players': players,
            })
        total = int(soup.find('plays')['total'])
        if page * 100 >= total or not batch:
            break
        page += 1
        time.sleep(1)
    plays.sort(key=lambda x: (x['date'], x['id']), reverse=True)
    return plays


def get_things(ids):
    """Return {id: details} with weight, mechanics, designers and best player counts."""
    ids = sorted(set(ids))
    out = {}
    for i in range(0, len(ids), THING_BATCH):
        chunk = ids[i:i + THING_BATCH]
        soup = _soup(fetch(f"{BASE_URL}/thing?id={','.join(map(str, chunk))}&stats=1"))
        for item in soup.find_all('item'):
            weight = item.find('averageweight')
            best = item.find('result', attrs={'name': 'bestwith'})
            best_counts = []
            if best:
                # e.g. "Best with 3–4 players" / "Best with 2, 4 players"
                for a, b in re.findall(r'(\d+)(?:\s*[–-]\s*(\d+))?', best['value']):
                    best_counts += list(range(int(a), int(b or a) + 1))
            thumb = item.find('thumbnail')
            out[int(item['id'])] = {
                'type': item.get('type'),
                'thumb': thumb.text.strip() if thumb else None,
                'weight': _num(weight['value']) if weight else None,
                'mechanics': [l['value'] for l in item.find_all('link', type='boardgamemechanic')],
                'categories': [l['value'] for l in item.find_all('link', type='boardgamecategory')],
                'designers': [l['value'] for l in item.find_all('link', type='boardgamedesigner')
                              if l['value'] != '(Uncredited)'],
                'best': best_counts,
            }
        if i + THING_BATCH < len(ids):
            time.sleep(2)
    return out
