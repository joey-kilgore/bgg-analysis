from utils import *
import time
import pickle

try:
    with open('usernames.pkl', 'rb') as f:
        users = pickle.load(f)
    with open('games.pkl', 'rb') as f:
        foundGames = pickle.dump(f)
    with open('ratings.pkl', 'rb') as f:
        ratings = pickle.dump(f)
except:
    users = []
    foundGames = {} # key-game id, val-game obj
    ratings = {} # key-game id, val-(user,rating) list

newUsers =[]
while len(newUsers) < 10:
    threadNum = randint(3000000, 3250000)
    try:
        newUsers = getUsersFromThread(threadNum)
        print('USING THREAD:'+str(threadNum)+'\tNUM USERS:'+str(len(newUsers)))
        time.sleep(2)
    except:
        print('MISSING THREAD:'+str(threadNum))

for user in newUsers:
    if user in users: continue
    users.append(user)
    print(user)
    games = getCollection(user)
    print('NUM GAMES:'+str(len(games)))
    for game in games:
        print(game.name)
        foundGames[game.name] = game
        if game.objectid in ratings:
            ratings[game.objectid].append( (user,game.myrating) )
        else:
            ratings[game.objectid] = []

    time.sleep(2)

print('TOTAL GAMES: '+str(len(foundGames)))
print('TOTAL USERS: '+str(len(users)))

numRatings = 0
for k in ratings.keys():
    numRatings += len(ratings[k])

with open('usernames.pkl', 'wb') as f:
    pickle.dump(users, f)
with open('games.pkl', 'wb') as f:
    pickle.dump(foundGames, f)
with open('ratings.pkl', 'wb') as f:
    pickle.dump(ratings, f)