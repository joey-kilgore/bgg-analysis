from utils import *
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
import os
import networkx as nx
from pyvis.network import Network

users = ['mrjoeboo123',
        'Schwingzilla',
        'ngeagan',
        'Wellsroderick',
        'withouthavingseen']


docsFolder = './docs/source/generated/'
os.makedirs(docsFolder, exist_ok=True)
bggGameLink = 'https://boardgamegeek.com/boardgame/'

collections = {}
for user in users:
    collections[user] = getCollection(user)

for user in users:
    print(f"{user} has {len(collections[user]):d} games listed on their account")

# get overall data into a tabulated form
headers = ['user','own','previosuly owned','want','wish','total']
status = []
for user in users:
    own = 0
    prev = 0
    want = 0
    wish = 0
    total = len(collections[user])
    for game in collections[user]:
        if game.own == 1: own += 1
        if game.prevowned == 1: prev += 1
        if game.want == 1: want += 1
        if game.wish != 0: wish += 1
    status.append([user, own, prev, want, wish, total])

table = tabulate(status, headers=headers, tablefmt="grid")
with open(docsFolder+'overview.md','w') as f:
    f.write('```\n'+table+'\n```\n\n')


# rating histograms
all_ratings = []
colors = []
binwidth = 0.5
bins=np.arange(1, 10 + binwidth, binwidth)
for user in users:
    ratings = []
    color = generate_random_hex_color()
    for game in collections[user]:
        if game.myrating != None:
            ratings.append(game.myrating)

    all_ratings.append(ratings)
    colors.append(color)
    plt.hist(ratings, bins=bins, label=user, color=color)
    plt.legend()
    plt.xlabel('Rating')
    plt.ylabel('Frequency of Rating')
    plt.xlim(1,10)
    plt.savefig('./docs/source/plots/'+user+'.png')
    plt.clf()


# common interests
minRating = 8
matches = {}
games = {}
for i in range(len(users)-1):
    for j in range(i+1, len(users)):
        for g1 in collections[users[i]]:
            if g1.myrating == None: continue
            for g2 in collections[users[j]]:
                if g2.myrating == None: continue
                if g1.objectid == g2.objectid and g1.myrating>minRating and g2.myrating>minRating:
                    
                    try:
                        if users[j] not in matches[g1.name]:
                            matches[g1.name].append(users[j])
                    except:
                        matches[g1.name] = [users[i], users[j]]
                        games[g1.name] = g1


out = "<table><tr><th>Game</th><th>Owns</th></tr>"
for k in matches.keys():
    out += f'<tr><td><a href="{bggGameLink+str(games[k].objectid)}"><img src="{games[k].thumbnail}" /></a></td><td>'
    for user in matches[k]:
        out += f"{user} "
    out += '</td>'
out += "</table>"

with open(docsFolder+'common_interests.html','w') as f:
    f.write(out)


# wish and own matches
print("Games matches for wishlist")
matches = [] # [(game,userWish,userOwn)]
for i in range(len(users)):
    for j in range(len(users)):
        for g1 in collections[users[i]]:
            for g2 in collections[users[j]]:
                if g1.objectid == g2.objectid and g1.wish!=0 and g2.own==1:
                    matches.append( (g1, users[i], users[j]) )

out = "<table><tr><th>Game</th><th>Wants to play</th><th>Owns</th></tr>"
for (game, userWish, userOwn) in matches:
    out += f'<tr><td><a href="{bggGameLink+str(game.objectid)}"><img src="{game.thumbnail}" /></a></td>'
    out += f"<td>{userWish}</td><td>{userOwn}</td>"
    out += '</tr>   '
      
out += "</table>"

with open(docsFolder+'wish_own.html','w') as f:
    f.write(out)

# common owns
print("Games both players own")
matches = {}
games = {}
for i in range(len(users)-1):
    for j in range(i+1, len(users)):
        for g1 in collections[users[i]]:
            for g2 in collections[users[j]]:
                if g1.objectid == g2.objectid and g1.own==1 and g2.own==1:
                    try:
                        if users[j] not in matches[g1.name]:
                            matches[g1.name].append(users[j])
                    except:
                        matches[g1.name] = [users[i], users[j]]
                        games[g1.name] = g1

out = "<table><tr><th>Game</th><th>Owns</th></tr>"
for k in matches.keys():
    out += f'<tr><td><a href="{bggGameLink+str(games[k].objectid)}"><img src="{games[k].thumbnail}" /></a></td><td>'
    for user in matches[k]:
        out += f"{user} "
    out += '</td></tr> '
out += "</table>"

with open(docsFolder+'multi_own.html','w') as f:
    f.write(out)


# building common own graph
graph = nx.Graph()

for user in users:
    graph.add_node(user)

    for g in collections[user]:
        if g.own != 1: continue
        graph.add_node(g.name)
        graph.add_edge(user,g.name)

nt = Network('800px', '800px')
nt.from_nx(graph)
nt.show_buttons(filter_=['physics'])
docsFolder = './docs/source/_static/'
os.makedirs(docsFolder, exist_ok=True)
nt.save_graph(docsFolder+'own_graph.html')
