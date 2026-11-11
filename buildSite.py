"""Build a single-page site analysing one BGG user's collection and logged plays.

Usage:
    BGG_TOKEN=... python buildSite.py            # writes site/index.html

Optional environment variables:
    BGG_USERNAME   BGG account to analyse            (default: joeyLiu)
    ME_NAME        your name as logged in plays       (default: Joey)
    PARTNER_NAME   the player for the rivalry section (default: Mickey)
    BGG_CACHE_DIR  cache raw API responses here while developing
    SITE_DIR       output folder                      (default: site)
"""
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone

from bgg_api import get_collection, get_plays, get_things

USERNAME = os.environ.get('BGG_USERNAME', 'joeyLiu')
ME = os.environ.get('ME_NAME', 'Joey')
PARTNER = os.environ.get('PARTNER_NAME', 'Mickey')
SITE_DIR = os.environ.get('SITE_DIR', 'site')
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site_template.html')
NOT_PEOPLE = {'', 'anonymous player', 'automa', 'solo', 'bot'}


def is_me(p):
    return p['username'].lower() == USERNAME.lower() or p['name'].lower() == ME.lower()


def is_partner(p):
    return not is_me(p) and p['name'].lower() == PARTNER.lower()


def find(players, pred):
    return next((p for p in players if pred(p)), None)


def h_index(counts):
    h = 0
    for i, c in enumerate(sorted(counts, reverse=True), 1):
        if c >= i:
            h = i
    return h


def quarter(d):
    return f'{d[:4]} Q{(int(d[5:7]) - 1) // 3 + 1}'


def months_between(first, last):
    y, m = int(first[:4]), int(first[5:7])
    out = []
    while (y, m) <= (int(last[:4]), int(last[5:7])):
        out.append(f'{y:04d}-{m:02d}')
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def build():
    today = datetime.now(timezone.utc).date()
    print(f'Fetching collection for {USERNAME}')
    collection = get_collection(USERNAME)
    print(f'Fetching plays for {USERNAME}')
    plays = get_plays(USERNAME)
    played_ids = {p['gameId'] for p in plays}
    print(f'Fetching details for {len(played_ids | {g["id"] for g in collection})} games')
    things = get_things(played_ids | {g['id'] for g in collection})

    coll_by_id = {g['id']: g for g in collection}

    def thumb(gid):
        return (coll_by_id.get(gid) or {}).get('thumb') or (things.get(gid) or {}).get('thumb')

    # ---- per-game play stats --------------------------------------------
    gplays = Counter()
    first_play, last_play, game_names = {}, {}, {}
    for p in plays:
        gid = p['gameId']
        gplays[gid] += p['qty']
        game_names[gid] = p['game']
        first_play[gid] = min(first_play.get(gid, p['date']), p['date'])
        last_play[gid] = max(last_play.get(gid, p['date']), p['date'])

    def game_ref(gid, **extra):
        g = coll_by_id.get(gid, {})
        return {'id': gid, 'name': g.get('name') or game_names.get(gid), 'thumb': thumb(gid), **extra}

    total_plays = sum(gplays.values())
    year = str(today.year)
    last30 = (today - timedelta(days=30)).isoformat()
    owned = [g for g in collection if g['own']]

    overview = {
        'username': USERNAME, 'me': ME, 'partner': PARTNER,
        'generated': today.isoformat(),
        'totalPlays': total_plays,
        'uniqueGames': len(gplays),
        'owned': len(owned),
        'prevOwned': sum(g['prevowned'] for g in collection),
        'wishlist': sum(g['wishlist'] for g in collection),
        'hIndex': h_index(gplays.values()),
        'playsThisYear': sum(p['qty'] for p in plays if p['date'].startswith(year)),
        'playsLast30': sum(p['qty'] for p in plays if p['date'] >= last30),
        'firstDate': min((p['date'] for p in plays), default=None),
        'lastPlay': game_ref(plays[0]['gameId'], date=plays[0]['date']) if plays else None,
        'dimes': sum(c >= 10 for c in gplays.values()),
        'nickels': sum(c >= 5 for c in gplays.values()),
        'quarters': sum(c >= 25 for c in gplays.values()),
        'newByYear': dict(sorted(Counter(d[:4] for d in first_play.values()).items())),
        'playsByYear': dict(sorted(Counter(p['date'][:4] for p in plays for _ in range(p['qty'])).items())),
        'year': year,
    }

    # ---- activity --------------------------------------------------------
    daily = defaultdict(lambda: {'n': 0, 'games': []})
    monthly = defaultdict(Counter)
    weekday = [0] * 7
    for p in plays:
        daily[p['date']]['n'] += p['qty']
        daily[p['date']]['games'].append(p['game'])
        monthly[p['date'][:7]][p['game']] += p['qty']
        weekday[date.fromisoformat(p['date']).weekday()] += p['qty']
    months = months_between(overview['firstDate'], today.isoformat()) if plays else []
    activity = {
        'daily': {d: {'n': v['n'], 'games': sorted(set(v['games']))} for d, v in daily.items()},
        'monthly': [{'m': m, 'n': sum(monthly[m].values()),
                     'top': monthly[m].most_common(3)} for m in months],
        'weekday': weekday,
        'years': sorted({p['date'][:4] for p in plays}),
    }

    def play_view(p):
        return {
            'date': p['date'], 'qty': p['qty'], 'note': p['note'], 'expansions': p['expansions'],
            'game': game_ref(p['gameId']),
            'players': [{'name': x['name'], 'win': x['win'], 'new': x['new'], 'score': x['score'],
                         'me': is_me(x), 'partner': is_partner(x)} for x in p['players']],
        }

    recent = [play_view(p) for p in plays[:30]]

    top_games = [game_ref(gid, plays=n, first=first_play[gid], last=last_play[gid],
                          rating=(coll_by_id.get(gid) or {}).get('myrating'))
                 for gid, n in gplays.most_common(15)]

    # ---- rivalry with partner -------------------------------------------
    chron = list(reversed(plays))
    together = []
    for p in chron:
        me, pa = find(p['players'], is_me), find(p['players'], is_partner)
        if me and pa:
            if me['win'] and not pa['win']:
                result = 'me'
            elif pa['win'] and not me['win']:
                result = 'partner'
            elif me['win'] and pa['win']:
                result = 'both'
            else:
                result = 'neither'
            together.append((p, me, pa, result))

    def record(rows):
        c = Counter(r[3] for r in rows)
        return {k: c.get(k, 0) for k in ('me', 'partner', 'both', 'neither')}

    two_player = [r for r in together if len(r[0]['players']) == 2]

    by_quarter = defaultdict(Counter)
    for p, _, _, res in together:
        by_quarter[quarter(p['date'])][res] += 1
    quarters = []
    if together:
        q = quarter(together[0][0]['date'])
        end = quarter(today.isoformat())
        while True:
            quarters.append({'q': q, **{k: by_quarter[q].get(k, 0) for k in ('me', 'partner', 'both', 'neither')}})
            if q == end:
                break
            y, n = int(q[:4]), int(q[-1])
            q = f'{y + (n == 4)} Q{1 if n == 4 else n + 1}'

    per_game = defaultdict(list)
    for r in together:
        per_game[r[0]['gameId']].append(r)
    rivalry_games = sorted(
        (game_ref(gid, plays=len(rs), last=rs[-1][0]['date'], **record(rs))
         for gid, rs in per_game.items() if len(rs) >= 3),
        key=lambda g: (-g['plays'], g['name']))

    # streaks over plays with a winner between the two of us
    decided = [r for r in together if r[3] in ('me', 'partner')]
    streaks = {'me': None, 'partner': None}
    i = 0
    while i < len(decided):
        j = i
        while j + 1 < len(decided) and decided[j + 1][3] == decided[i][3]:
            j += 1
        who, length = decided[i][3], j - i + 1
        if not streaks[who] or length > streaks[who]['n']:
            streaks[who] = {'n': length, 'from': decided[i][0]['date'], 'to': decided[j][0]['date'],
                            'games': [g for g, _ in Counter(d[0]['game'] for d in decided[i:j + 1]).most_common(3)]}
        i = j + 1
    current = None
    if decided:
        who = decided[-1][3]
        n = 0
        for r in reversed(decided):
            if r[3] != who:
                break
            n += 1
        current = {'who': who, 'n': n}

    margins = []
    for p, me, pa, res in two_player:
        a, b = me['score'], pa['score']
        if a is None or b is None or max(abs(a), abs(b)) < 5:
            continue
        margins.append({'date': p['date'], 'game': game_ref(p['gameId']), 'me': a, 'partner': b,
                        'result': res, 'rel': abs(a - b) / max(abs(a), abs(b))})
    ties = [m for m in margins if m['me'] == m['partner']]
    closest = sorted((m for m in margins if m['me'] != m['partner']), key=lambda m: (m['rel'], m['date']))[:6]
    blowouts = sorted(margins, key=lambda m: -m['rel'])[:6]

    learned = {}
    for p, me, pa, _ in together:
        if me['new'] and pa['new'] and p['gameId'] not in learned:
            learned[p['gameId']] = game_ref(p['gameId'], date=p['date'])

    partner_words = PARTNER.lower()
    notes = [dict(play_view(p), partner=any(is_partner(x) for x in p['players']) or partner_words in p['note'].lower())
             for p in plays if p['note']]

    rivalry = {
        'together': sum(r[0]['qty'] for r in together),
        'share': sum(r[0]['qty'] for r in together) / total_plays if total_plays else 0,
        'first': game_ref(together[0][0]['gameId'], date=together[0][0]['date']) if together else None,
        'gamesTogether': len(per_game),
        'record': record(together),
        'record2p': record(two_player),
        'twoPlayerCount': len(two_player),
        'quarters': quarters,
        'games': rivalry_games,
        'streaks': streaks,
        'current': current,
        'closest': closest,
        'ties': len(ties),
        'blowouts': blowouts,
        'learned': sorted(learned.values(), key=lambda g: g['date'], reverse=True),
    }

    # ---- other people at the table -------------------------------------
    people = defaultdict(lambda: {'plays': 0, 'me': 0, 'them': 0, 'last': '', 'names': Counter()})
    for p in plays:
        me = find(p['players'], is_me)
        for x in p['players']:
            if is_me(x) or is_partner(x) or x['name'].lower() in NOT_PEOPLE:
                continue
            key = x['name'].lower()
            row = people[key]
            row['plays'] += p['qty']
            row['names'][x['name']] += 1
            row['last'] = max(row['last'], p['date'])
            if me and me['win'] and not x['win']:
                row['me'] += 1
            if me and x['win'] and not me['win']:
                row['them'] += 1
    opponents = sorted(({'name': v['names'].most_common(1)[0][0], 'plays': v['plays'], 'me': v['me'],
                         'them': v['them'], 'last': v['last']}
                        for k, v in people.items()), key=lambda r: -r['plays'])[:14]

    # ---- collection ------------------------------------------------------
    def plays_of(g):
        return max(gplays.get(g['id'], 0), g['numplays'])

    def coll_view(g, **extra):
        t = things.get(g['id'], {})
        return {'id': g['id'], 'name': g['name'], 'thumb': g['thumb'] or t.get('thumb'), 'year': g['year'],
                'rating': g['myrating'], 'bggavg': g['bggavg'], 'rank': g['rank'], 'weight': t.get('weight'),
                'plays': plays_of(g), 'minp': g['minp'], 'maxp': g['maxp'], 'time': g['time'],
                'best': t.get('best', []), 'own': g['own'], 'last': last_play.get(g['id']), **extra}

    owned_views = sorted((coll_view(g) for g in owned), key=lambda g: g['name'].lower())
    year_ago = (today - timedelta(days=365)).isoformat()
    shame = sorted((g for g in owned_views if g['plays'] == 0),
                   key=lambda g: (-(g['rating'] or 0), g['rank'] or 99999))
    dusty = sorted((g for g in owned_views if g['plays'] > 0 and g['last'] and g['last'] < year_ago),
                   key=lambda g: g['last'])

    rated = [coll_view(g) for g in collection if g['myrating'] is not None]
    scatter = [{'id': g['id'], 'name': g['name'], 'rating': g['rating'], 'plays': g['plays'], 'own': g['own']}
               for g in rated]
    takes = sorted(({'id': g['id'], 'name': g['name'], 'thumb': g['thumb'], 'rating': g['rating'],
                     'bggavg': round(g['bggavg'], 2), 'diff': round(g['rating'] - g['bggavg'], 2)}
                    for g in rated if g['bggavg']), key=lambda t: t['diff'])

    weight_bins = [0] * 8  # 1.0-1.5, ... 4.5-5.0
    for g in owned_views:
        if g['weight']:
            weight_bins[min(int((g['weight'] - 1) / 0.5), 7)] += 1

    mech = defaultdict(list)
    for g in rated:
        for m in things.get(g['id'], {}).get('mechanics', []):
            mech[m].append(g['rating'])
    mechanics = sorted(({'name': m, 'n': len(r), 'avg': round(sum(r) / len(r), 2)}
                        for m, r in mech.items() if len(r) >= 5), key=lambda m: -m['avg'])

    designers = Counter(d for g in owned for d in things.get(g['id'], {}).get('designers', []))
    designer_rows = []
    for d, n in designers.most_common(10):
        if n < 2:
            break
        gs = [g for g in owned_views if d in things.get(g['id'], {}).get('designers', [])]
        rs = [g['rating'] for g in gs if g['rating']]
        designer_rows.append({'name': d, 'n': n, 'avg': round(sum(rs) / len(rs), 2) if rs else None,
                              'games': [g['name'] for g in gs]})

    wishlist = sorted((coll_view(g, priority=g['wishpriority']) for g in collection if g['wishlist']),
                      key=lambda g: (g['priority'] or 9, g['rank'] or 99999))
    want_to_play = [coll_view(g) for g in collection if g['wanttoplay'] and not g['own']]

    collection_data = {
        'owned': owned_views,
        'shame': shame,
        'dusty': dusty,
        'scatter': scatter,
        'takes': {'love': takes[::-1][:8], 'meh': takes[:8]},
        'weightBins': weight_bins,
        'mechanics': mechanics,
        'designers': designer_rows,
        'wishlist': wishlist,
        'wantToPlay': want_to_play,
        'avgWeight': round(sum(g['weight'] for g in owned_views if g['weight']) /
                           max(1, sum(1 for g in owned_views if g['weight'])), 2),
        'avgRating': round(sum(g['rating'] for g in rated) / len(rated), 2) if rated else None,
        'ratedCount': len(rated),
    }

    return {'overview': overview, 'activity': activity, 'recent': recent, 'topGames': top_games,
            'rivalry': rivalry, 'notes': notes, 'opponents': opponents, 'collection': collection_data}


def render(data):
    with open(TEMPLATE, encoding='utf-8') as f:
        html = f.read()
    payload = json.dumps(data, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
    html = html.replace('/*__DATA__*/null', payload)
    os.makedirs(SITE_DIR, exist_ok=True)
    out = os.path.join(SITE_DIR, 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    with open(os.path.join(SITE_DIR, '.nojekyll'), 'w') as f:
        f.write('')
    print(f'Wrote {out} ({len(html) / 1024:.0f} KB)')


if __name__ == '__main__':
    render(build())
