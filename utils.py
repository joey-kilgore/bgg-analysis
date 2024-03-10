from bs4 import BeautifulSoup
import requests
import time
from random import randint

baseURL = 'https://www.boardgamegeek.com'

class Game:
    def __init__(self, game, username):
        if game['subtype'] != 'boardgame': self = None

        self.name = game.find('name').text
        self.objectid = int(game['objectid'])
        self.own = int(game.find('status')['own'])
        self.prevowned = int(game.find('status')['prevowned'])
        self.want = int(game.find('status')['want'])
        self.owner = username
        try:
            self.myrating = float(game.find('rating')['value'])
        except:
            self.myrating = None

def getCollection(username, gamesDict=None):
    url = baseURL+'/xmlapi/collection/'+username
    flag = True
    while flag:
        url_link = requests.get(url)
        soup = BeautifulSoup(url_link.text, "lxml")

        if len(soup.find_all('message'))==0:
            flag = False
        else:
            time.sleep(10)
            print('REQUSTING AGAIN '+username)

    items = soup.find_all('item')
    games = []
    for i in items:
        games.append(Game(i, username))

    return games

def getUsersFromThread(threadId):
    url = baseURL+'/xmlapi2/thread?id='+str(threadId)

    url_link = requests.get(url)
    soup = BeautifulSoup(url_link.text, "lxml")
    articles = soup.find_all('article')

    usernames = []
    for article in articles:
        if article['username'] not in usernames:
            usernames.append(article['username'])

    return usernames

def score(game):
    try:
        return float(game.myrating)
    except:
        return 0.0