from utils import *
import time
import pickle
from multiprocessing import Pool

if __name__ == '__main__':
    try:
        with open('usernames.pkl', 'rb') as f:
            users = pickle.load(f)
        with open('games.pkl', 'rb') as f:
            foundGames = pickle.load(f)
        with open('ratings.pkl', 'rb') as f:
            ratings = pickle.load(f)
    except:
        users = []
        foundGames = {} # key-game id, val-game obj
        ratings = {} # key-game id, val-(user,rating) list

    newUsers =['mrjoeboo123']
    for i in range(200):
        tmpUsers = []
        while len(tmpUsers) < 2:
            threadNum = randint(3000000, 3250000)
            try:
                tmpUsers = getUsersFromThread(threadNum)
                print('USING THREAD:'+str(threadNum)+'\tNUM USERS:'+str(len(tmpUsers)))
            except:
                print('MISSING THREAD:'+str(threadNum))
        
        for u in tmpUsers:
            if u not in newUsers:
                newUsers.append(u)
        time.sleep(1)

    for user in newUsers:
        if user in users: continue
        users.append(user)

    print(newUsers)

    with Pool(50) as pool:
        for games in pool.map(getCollection, newUsers):
            print('NUM GAMES:'+str(len(games)))
            for game in games:
                foundGames[game.objectid] = game
                if game.objectid in ratings:
                    ratings[game.objectid].append( (game.owner,game.myrating) )
    
                else:
                    ratings[game.objectid] = [ (game.owner, game.myrating)]

            time.sleep(2)

    print('TOTAL GAMES: '+str(len(foundGames)))
    print('TOTAL USERS: '+str(len(users)))

    numRatings = 0
    for k in ratings.keys():
        numRatings += len(ratings[k])
    print('NUM RATINGS: '+str(numRatings))

    with open('usernames.pkl', 'wb') as f:
        pickle.dump(users, f)
    with open('games.pkl', 'wb') as f:
        pickle.dump(foundGames, f)
    with open('ratings.pkl', 'wb') as f:
        pickle.dump(ratings, f)