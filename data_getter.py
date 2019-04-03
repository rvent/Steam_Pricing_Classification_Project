import numpy as np
import pandas as pd
import json
import time
import requests
import copy


CATS = ["Single-player", "Multi-player", 'Online Multi-Player', 'Local Multi-Player', 'Co-op', 
                'Online Co-op', 'Local Co-op', 'Shared/Split Screen', 'Cross-Platform Multiplayer', ]
GENRES = ['Action','Adventure', 'Indie', 'Casual', 'Massively Multiplayer', 'Racing', 'RPG', "Simulation", 
          "Strategy", "Sports", "Free to Play", "Early Access"]
PLATFORMS = ["windows", "mac", "linux"]

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
def get_steamlist():
    return requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/').json()

games = get_steamlist()['applist']["apps"]
ids_lst = [game["appid"] for game in games]

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

def retrieve_steam_reviews(start, end):
    """
    takes a list of game ids
    return a list of dictionaries of user reviews of all games in the id_list
    """
    data_from_steam_ = []
    for num, game in enumerate(games[start: end]):
        appid = game["appid"]
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

# the next two functions clean the data on any values that failed or were None
# helper for the clean non_id
def del_unwanted(dic, unwanted_lst):
    """
    takes a dictionary as dic
    takes a list of unwanted keys as unwanted_lst
    returns a copy of the dictionary dic with all the unwanted keys and values removed
    """
    dic_copy = copy.deepcopy(dic)
    for key in unwanted_lst:
        if key in dic_copy:
            del dic_copy[key]
    return dic_copy

def clean_non_id_data(games_data_lst, start, end):
    """
    takes a dictionary of game data as games_data_lst
    takes an index of the where to begin the slice of the games_data_lst as start
    takes an index of the where to end the slice of the games_data_lst as end
    returns a list of game data that has the unnecessary keys and values removed
    """
    data_dic_lst = []
    data_f = copy.deepcopy(games_data_lst)
    for game in data_f[start:end]:
        if type(game) == dict:
            for key, val in game.items():
                if "success" in val:
                        del val["success"]
                if val != {}:
                    # use the helper func del_unwated to remove unnecessary keys and values
                    new_val = del_unwanted(val["data"], ["header_image", "website", "packages", "package_groups",
                                                        "screenshots", "movies", "support_info", "background",
                                                        "content_descriptors", "controller_support", "drm_notice",
                                                        "ext_user_account_notice", "detailed_description", 
                                                        "short_description", "legal_notice", "linux_requirements",
                                                        "mac_requirements", "fullgame", "publishers", "demos",
                                                        "pc_requirements", "release_date", 'alternate_appid', 
                                                         "release_date","about_the_game", "reviews", "developers"])
            
                    data_dic_lst.extend([new_val])
    return data_dic_lst


# the following functions were used to further clean the data and set-up our dataframe structure

# functions to clean and format each feature
# this function is meant to work with data that has a description key like categories in the game data
def get_clean_dummies(raw_dic, desc_key, descriptions, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes a string of a key in the game data as desc_key
    takes in a list of descriptions we want in our final data
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the original data from raw_dic with the descriptions in desc_key split into dummy variables
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        for key in descriptions:
            data[key] = 0
        if desc_key in data:
            for cat in data[desc_key]:
                if cat["description"] in descriptions:
                    data[cat["description"]] = 1
            del data[desc_key]
    return cleaned


def get_platform_dummies(raw_dic, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the original data from raw_dic with the platforms being split into dummy variables
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned: 
        if "platforms" in data:
            for key in PLATFORMS:
                data[key] = 0 
                if key in data["platforms"]:
                    data[key] = int(data["platforms"][key])
        else:
            for key in platforms_lst:
                data[key] = 0 
        del data["platforms"]
    return cleaned

# this function is meant to work with the data that has a "total" key
def get_total_from_dic(raw_dic, desc_key, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes a string of a key in the game data as desc_key
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the original data except with the desc_key showing the total value only
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        if desc_key in data:
            data[desc_key] = data[desc_key]["total"]
        else:
            data[desc_key] = 0
    return cleaned

def get_metas_from_dic(raw_dic, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the original data except with the metacritic key only having a score
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        if "metacritic" in data:
            data["metacritic"] = data["metacritic"]["score"]
        else:
            data["metacritic"] = 0
    return cleaned

def clean_dev(raw_dic, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the original data except with the values of the developer key being a string
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    cleaned = copy.deepcopy(raw_dic)
    for data in cleaned:
        if "developers" in data:
            data["developers"] = ", ".join(data["developers"])
        else:
            data["developers"] = ""
    return cleaned

def dlc_reformatting(raw_dic, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the original data except with the values of the dlc key being the dlc count for the game
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        if "dlc" in data:
            data["dlc"] = len(data["dlc"])
        else:
            data["dlc"] = 0
    return cleaned

def convert_to_1_0(raw_dic, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the is_free feature as 1s and 0s not True or False
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        if "is_free" in data:
            data["is_free"] = int(data["is_free"])
        else:
            data["is_free"] = 0
    return cleaned

def clean_money(raw_dic, nans_to_zero=False, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the only the price_overview in USD
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        if "price_overview" in data:
            if data["price_overview"]["currency"] == "USD":
                data["price_overview"] = round(data["price_overview"]["final"]*.01, 2)
            else:
                data["price_overview"] = 0
        else:
            if nans_to_zero:
                data["price_overview"] = 0
    return cleaned

def clean_language(raw_dic, keep=True):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary with the number of supported language instead of the language itself
    """
    if keep:
        cleaned = copy.deepcopy(raw_dic)
    else:
        cleaned = raw_dic
    for data in cleaned:
        if "supported_languages" in data:
            data["num_supported_languages"] = len(data["supported_languages"].split(","))
            del data["supported_languages"]
        else:
             data["num_supported_languages"] = 1
        
    return cleaned


# cleans the data using all the feature cleaning functions
def clean_data(raw_dic, keep=False):
    """
    takes a dictionary of game data which went through an initial cleaning process of removing failures and None as raw_dic
    takes an optional boolean keep to determine if the raw_dic is changed or a new dictionary is returned
    returns a dictionary that has been completely cleaned by the the individual feature cleaning functions
    """
    clean_money(raw_dic, True, keep)
    clean_dev(raw_dic, keep)
    convert_to_1_0(raw_dic, keep)
    dlc_reformatting(raw_dic, keep)
    get_clean_dummies(raw_dic, "categories", CATS, keep)
    get_clean_dummies(raw_dic, "genres", GENRES, keep)
    get_total_from_dic(raw_dic, "recommendations", keep)
    get_total_from_dic(raw_dic, "achievements", keep)
    get_platform_dummies(raw_dic, keep)
    get_metas_from_dic(raw_dic, keep)
    clean_language(raw_dic, keep=keep)
    return pd.DataFrame(raw_dic)
            
# cleans and structures the review in a certain format    
def clean_review(lst_reviews):
    """
    takes in a list of unformatted reviews as lst_reviews
    returns a list of properly formatted reviews
    """
    check = ['review_score','total_positive', 'total_negative', 'total_reviews']
    data_storage = []
    for rev in lst_reviews:
        app_id = list(rev.keys())[0]
        review_dict = {}
        review_dict["steam_appid"] = int(app_id)
        review_dict["reviews"] = ""
        for key in check:
            if "query_summary" in rev[app_id]:
                if key in rev[app_id]["query_summary"]:
                    review_dict[key] = rev[app_id]["query_summary"][key]
        if "reviews" in rev[app_id]:
            for text in rev[app_id]["reviews"]:
                review_dict["reviews"] += " " + text["review"]
        data_storage.append(review_dict)
    return data_storage
