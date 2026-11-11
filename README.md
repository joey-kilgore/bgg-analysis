# bgg-analysis
 Analysis of the Board Game Geek

# My collection & plays
Live page - https://joey-kilgore.github.io/bgg-analysis/

`buildSite.py` pulls one BGG account's collection, logged plays and game details
(weight, mechanics, designers, best player counts) from the BGG XML API and renders
a single self-contained page to `site/index.html`: play calendar, monthly activity,
recent plays, a head-to-head rivalry section, play notes, ratings vs. plays,
hot takes vs. the BGG average, a "what should we play tonight" picker, shelf of
shame and a searchable collection table. A GitHub Action rebuilds it every Monday.

To build locally (PowerShell):
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
. .\set_env.ps1                    # sets BGG_TOKEN, see set_env.example.ps1
$env:BGG_CACHE_DIR = ".bgg_cache"   # optional: cache API responses while iterating
.venv\Scripts\python buildSite.py
start site\index.html
```

Optional settings (environment variables): `BGG_USERNAME` (default `joeyLiu`),
`ME_NAME` (your name in logged plays, default `Joey`), `PARTNER_NAME`
(the rivalry section, default `Mickey`).

The page layout and charts live in `site_template.html`; `buildSite.py` injects
the computed data as JSON.

# initial setup
To start collecting BGG data, we will grab random threads to easily get a random collection of usernames. We will then grab the ratings and games that each of those users has, and from there the data is aggregated into three pickled objects.

You are welcome to run spider yourself to get your own random data, but a sample dataset of my own collecting is available on google drive at the following link:

https://drive.google.com/drive/folders/1a4hezOIohPHHbpyJ8lmThzMPAvsUX5Fo?usp=drive_link

# Analysis
Checkout `overallAnalysis.ipynb` for a sample script that looks through how to analyze this data by looking at overall ratings, and trying to find ways to link similar gamers together. 
