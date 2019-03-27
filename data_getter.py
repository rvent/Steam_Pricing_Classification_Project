from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import requests
import numpy as np
import copy

def get_appid(name, games):
    for i in range(len(games['name'])):
        if games['name'][i].title() == name.title():
            return games['appid'][i]
    return "Did not find"

def get_game_info(appid):
    url = 'https://store.steampowered.com'
    ids = str(appid)
    r = requests.get(url+'/api/appdetails?appids='+ids).json()
    return r

def retrieve_steam_data(start, end):
    data_from_steam_ = []
    for num, game in enumerate(games[start: end]):
        if game["appid"] >= 10:
            data_from_steam_.append(get_game_info(game["appid"]))
        if num % 1000 == 0 and num >0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            save_data(data_from_steam_, f"{num}_data_{start}.json")
            print(num, "Saved!")
            time.sleep(t)
        elif num % 100 == 0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            print(num, t)
            time.sleep(t)
    return data_from_steam_ 

def retrieve_steam_reviews(id_lst):
    data_from_steam_ = []
    for num, appid in enumerate(id_lst):
        data_from_steam_.append(get_reviews(game["appid"]))
        if num % 1000 == 0 and num >0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            save_data(data_from_steam_, f"{num}_data_{start}.json")
            print(num, "Saved!")
            time.sleep(t)
        elif num % 100 == 0:
            t = np.random.choice([1,1.1,1.2,1.3,1.4,1.5])
            print(num, t)
            time.sleep(t)
    return data_from_steam_ 

def get_reviews(appid, start_offset=0, fil='updated', review_type='all'):
    url = 'https://store.steampowered.com'
    reviews = '/appreviews/'
    p = {'day_range':'9223372036854775807', 
         'start_offset':start_offset, 
         'language':'english', 
         'filter':fil, 
         'review_type':review_type,
         'purchase_type':'all'}
    r = requests.get(url+reviews+str(appid)+'?json=1?', params=p).json()
    return r

def open_save_data(file_to_open):
        """takes in a filename to open
           return """
        with open(file_to_open) as datajson:
            new_data =json.load(datajson)
        return new_data
    
def save_data(data, file_to_save_to):
        """takes in a filename to save to"""
        with open(file_to_save_to, 'w') as outfile:
            json.dump(data, outfile)
            
games = open_save_data("games.json")