import pandas as pd
import json
import time
import requests

# these two functions are for opening and saving json files
def open_save_data(file_to_open):
        """takes in a json file to open
           return a list of dictionaries"""
        with open(file_to_open) as datajson:
            new_data =json.load(datajson)
        return new_data
    
def save_data(data, file_to_save_to):
        """takes in a filename to save to"""
        with open(file_to_save_to, 'w') as outfile:
            json.dump(data, outfile)

# a list of steam appids and game names
games = open_save_data("games.json")

# these next two function collect game info and reviews for an individual game
def get_game_info(appid):
    """
    takes a game's appid as an integer
    return a json file with a game's steam information
    """
    url = 'https://store.steampowered.com/api/appdetails?appids='
    ids = str(appid)
    r = requests.get(url+ids).json()
    return r

def get_reviews(appid, start_offset=0):
    """
    takes a game's appid as a string and an optional offset integer
    return a json file with user reviews for a game
    """
    url = 'https://store.steampowered.com'
    reviews = '/appreviews/'
    p = {'day_range':'9223372036854775807', 
         'start_offset':start_offset, 
         'language':'english', 
         'filter':'updated', 
         'review_type':all,
         'purchase_type':'all'}
    r = requests.get(url+reviews+str(appid)+'?json=1?', params=p).json()
    return r

# these next two functions collect game info and reviews for multiple gamess
def retrieve_steam_data(start, end):
    """
    takes a start index and end index as integers to slice the games list above
    return a list of dictionaries of game info
    """
    data_from_steam_ = []
    for num, game in enumerate(games[start: end]):
        if game["appid"] >= 10:
            data_from_steam_.append(get_game_info(game["appid"]))
        # save the data as a json after every thousand iterations
        if num % 1000 == 0 and num >0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            save_data(data_from_steam_, f"data_{start}_to_{end}.json")
            print(num, "Saved!")
            time.sleep(t)
        # pause making request to the site after every 100 iterations
        elif num % 100 == 0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            print(num, t)
            time.sleep(t)
    return data_from_steam_ 

def retrieve_steam_reviews(id_lst):
    """
    takes a list of game ids
    return a list of dictionaries of user reviews of all games in the id_list
    """
    data_from_steam_ = []
    for num, appid in enumerate(id_lst):
        data_from_steam_.append({appid: get_reviews(appid)})
        if num % 1000 == 0 and num >0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            save_data(data_from_steam_, f"upto_{num}_reviews.json")
            print(num, "Saved!")
            time.sleep(t)
        elif num % 100 == 0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            print(num, t)
            time.sleep(t)
    return data_from_steam_ 



            
