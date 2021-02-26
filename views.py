import json
import requests

import asyncio
from aiohttp import ClientSession

class HomePage():
    def __init__(self):
        self.tmdb_key = "2e510746ca28d7041056c7e57108de4c" #TODO: Read from file on backend
        self.backdrop_base = 'https://www.themoviedb.org/t/p/w1920_and_h800_multi_faces'
        self.home_doc = dict() 
        self.get_trending()
        self.get_airing()
    
    def get_trending(self): # called by __init__()
        #Local parameters
        endpoint_trend = f'https://api.themoviedb.org/3/trending/movie/week?api_key={self.tmdb_key}'
        r = requests.get(endpoint_trend)

        #Extract necessary features
        items = r.json()['results'][:5]
        items_trend = [{'tmdb_id': m['id'], 
                    'backdrop_path': m['backdrop_path'],
                    'name': m['title'],
                    'release_date': m['release_date']
                    } for m in items]

        #Construct backdrop path, and add back to items_trend
        for idx, m in enumerate(items_trend):
            backdrop_path = m['backdrop_path']
            backdrop_full = f'{self.backdrop_base}{backdrop_path}'
            items_trend[idx]['backdrop_path'] = backdrop_full
        self.home_doc['trending'] = items_trend 
        
    def get_airing(self): # called by __init__()
        #Local parameters
        endpoint_airing = f'https://api.themoviedb.org/3/tv/airing_today?api_key={self.tmdb_key}'
        r = requests.get(endpoint_airing)

        #Extract necessary features
        items = r.json()['results'][:5]
        items_air = [{'tmdb_id': m['id'], 
                    'backdrop_path': m['backdrop_path'],
                    'name': m['name'],
                    'first_air_date': m['first_air_date']
                    } for m in items]

        #Construct backdrop path, and add back to items_air
        for idx, m in enumerate(items_air):
            backdrop_path = m['backdrop_path']
            backdrop_full = f'{self.backdrop_base}{backdrop_path}'
            items_air[idx]['backdrop_path'] = backdrop_full
        self.home_doc['airing'] = items_air

class SearchPage():
    def __init__(self, content_type, search_terms):
        #Supplied Parameters
        self.tmdb_key = "2e510746ca28d7041056c7e57108de4c"
        self.poster_base = "https:/www.themoviedb.org/t/p/w1280"
        self.genre_files = ['genre_movie.json', 'genre_tv.json']
        
        #Computed Parameters
        self.doc = dict()
        self.genre_map = self.load_genres()
        
        #Search params parsed from url constructed by XHR request
        self.content_type = content_type
        self.search_terms = search_terms
        
    def load_genres(self): #called by __init__
        '''Loads genre files into memory, given a genre_files object.
        genre_files: ['genre_movie.json', 'genre_tv.json']'''
        genre_map = dict()
        for file in self.genre_files:
            content_type = file.split('_')[1].split('.')[0]
            fd = open(file, 'r')
            data = json.loads(fd.readline())

            #Construct dict of key=id, value=name and append to genre_map
            g_dict = dict()
            for kv_pair in data['genres']:
                g_dict[kv_pair['id']] = kv_pair['name']
            genre_map[content_type] = g_dict
        return genre_map
        
    def get_content(self):
        '''Gets content based off user content type and search terms.
        search_terms - a string containing one or more words
        content_type - "tv", "movie" '''
        poster_base = "https:/www.themoviedb.org/t/p/w1280"

        #Check if multiple search terms
        terms_list = self.search_terms.split(' ')
        if len(terms_list) >= 2: search_terms2 = "%20".join(terms_list)
        else: search_terms2 = self.search_terms

        endpoint = f"https://api.themoviedb.org/3/search/{self.content_type}?api_key={self.tmdb_key}&language=en-US&query={search_terms2}&include_adult=false"
        r = requests.get(endpoint)

        #Extract necesssary features
        items = r.json()['results'][:10]
        
        #Check if feature exists, before extracting
        movie_feats = [('id', 'i'), ('title', 's'), ('overview', 's'), ('poster_path', 'path'),
                       ('release_date', 's'), ('vote_average', 'f'), ('vote_count', 'i'), ('genre_ids', 'l'), ('media_type', 's')]
        tv_feats = [('id', 'i'), ('name', 's'), ('overview', 's'), ('poster_path', 'path'),
                    ('first_air_date', 's'), ('vote_average', 'f'), ('vote_count', 'i'), ('genre_ids', 'l'), ('media_type', 's')]
        
        type_null_map = {'s': 'Not Available', 'i': 0, 'l': 'Not Available', 'f': 0,
                        'path': 'https://cinemaone.net/images/movie_placeholder.png'}
        
        #Set initial desired_feats, based on search content_type
        if self.content_type == "movie":
            desired_feats = movie_feats
        elif self.content_type == "tv":
            desired_feats = tv_feats
        
        #Construct list of records, and handle null values
        items_extract = list()
        for idx, m in enumerate(items):
            
            #For content_type=multi, handle switching desired_feats for each record
            if 'media_type' not in m: pass
            elif 'media_type' in m:
                if m['media_type'] == 'movie':
                    desired_feats = movie_feats
                elif m['media_type'] == 'tv':
                    desired_feats = tv_feats
                else:
                	continue
            
            record = dict()
            for feat in desired_feats:
                if feat[0] not in m:
                    if feat[0] == "media_type":
                        record[feat[0]] = self.content_type
                    else:
                        record[feat[0]] = type_null_map[feat[1]]
                else:
                    if m[feat[0]] == None: record[feat[0]] = type_null_map[feat[1]]
                    else: record[feat[0]] = m[feat[0]]
            items_extract.append(record)

        #Feature engineering
        for idx, m in enumerate(items_extract):
            #Construct poster path, and add back to items_extract
            poster_path = m['poster_path']
            if poster_path.split('/')[-1] == 'movie_placeholder.png': pass
            else:
                poster_full = f'{poster_base}{poster_path}'
                items_extract[idx]['poster_path'] = poster_full

            #Get the genre names
            if m['genre_ids'] == 'Not Available': pass
            else:
                g_names = list()
                for g_id in m['genre_ids']:
                    #Get genre based on media_type
                    if self.content_type in ["movie", "tv"]: g_type = self.content_type
                    elif self.content_type == "multi": g_type = m["media_type"]

                    g_name = self.genre_map[g_type][g_id]
                    g_names.append(g_name)
                items_extract[idx].pop('genre_ids', None)
                items_extract[idx]['genres'] = g_names
            
            #Convert rating from 10-scale to 5-scale
            if m['vote_average'] == 0: pass
            else:
                avg_adj = str(round(m['vote_average']/2, 2))
                avg_adj_str = f'{avg_adj}/5'
                items_extract[idx]['vote_average'] = avg_adj_str
            
        self.doc['search_result'] = items_extract

class RespParser():
    '''Used for parsing details for a given movie or tv id. '''
    def __init__(self):
        self.tmdb_key = "2e510746ca28d7041056c7e57108de4c"
        
        self.poster_base = "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"
        self.backdrop_base = 'https://www.themoviedb.org/t/p/w1920_and_h800_multi_faces'
        self.profile_base = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2'

        self.poster_null = "https://cinemaone.net/images/movie_placeholder.png"
        self.backdrop_null = "https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/movie-placeholder.jpg"
        self.profile_null = 'https://bytes.usc.edu/cs571/s21_JSwasm00/hw/HW6/imgs/person-placeholder.png'
        
        self.entity_feat_map = dict()
        self.entity_feat_map['movie'] = {'details': ['id', 'title', 'overview', 'runtime', 'release_date', 'spoken_languages', 
                                                     'vote_average', 'vote_count', 'poster_path', 'backdrop_path', 'genres'],
                                         'credits': ['name', 'profile_path', 'character'],
                                         'reviews': ['username', 'content', 'rating', 'created_at']}
        self.entity_feat_map['tv'] = {'details': ['id', 'name', 'overview', 'episode_run_time', 'first_air_date', 
                                                  'spoken_languages', 'vote_average', 'vote_count', 'poster_path', 
                                                  'backdrop_path', 'genres', 'number_of_seasons'],
                                      'credits': ['name', 'profile_path', 'character'],
                                      'reviews': ['username', 'content', 'rating', 'created_at']}
        
    def construct_feat_endpoints(self, entity_type, entity_id):
        '''Construct a list of endpoints to hit, based on entity_type and entity_id.
        entity_type - either "movie" or "tv"
        entity_id - the tmdb id of the entity'''
        self.feat_endpoints = [('details', f"https://api.themoviedb.org/3/{entity_type}/{entity_id}?api_key={self.tmdb_key}&language=en-US"),
                                 ('credits', f"https://api.themoviedb.org/3/{entity_type}/{entity_id}/credits?api_key={self.tmdb_key}&language=en-US"),
                                 ('reviews', f"https://api.themoviedb.org/3/{entity_type}/{entity_id}/reviews?api_key={self.tmdb_key}&language=en-US&page=1")
                           ]
        
    def parse_response_details(self, entity_type, response):
        '''Parse the response gotten for tmdb credits, customized to response formatting.
        entity_type - "movie" or "tv"
        endpoint - should look like ('details', <url>)'''

        #Result will be a dict
        result = dict()

        #Get the feat_set that will be used to extract feats from response
        r = response
        
        #Get the desired feats to extract
        feat_set = self.entity_feat_map[entity_type]['details']

        #Extract and clean features from response
        for feat in feat_set:
            if feat in r:

                #Handle nulls 
                if r[feat] in [None, ""]:
                    result[feat] = ""

                #Handle not nulls
                #release_date - extract year
                elif feat in ['release_date', 'first_air_date']:
                    result[feat] = r[feat].split('-')[0]

                #language
                elif feat == 'spoken_languages':
                    langs = [item['english_name'] for item in r[feat]]
                    result[feat] = langs

                #vote average
                elif feat == 'vote_average':
                    result[feat] = str(round(r[feat]/2, 2)) + '/5'

                #poster_path
                elif feat == 'poster_path':
                    if r[feat] == None:
                        result[feat] = self.poster_null
                    else:
                        poster_path = r[feat]
                        result[feat] = f'{self.poster_base}{poster_path}'

                #background_path
                elif feat == 'backdrop_path':
                    if r[feat] == None:
                        result[feat] = self.backdrop_null
                    else:
                        backdrop_path = r[feat]
                        result[feat] = f'{self.backdrop_base}{backdrop_path}'

                #genres
                elif feat == "genres":
                    genres = [item['name'] for item in r[feat]]
                    result[feat] = genres

                #All others - no further processing needed
                else:
                    result[feat] = r[feat]

            else:
                print(f'{feat} not in response')
                result[feat] = ""
        return result

    def parse_response_credits(self, entity_type, response):
        '''Parse the response gotten for tmdb credits, customized to response formatting.
        entity_type - "movie" or "tv"
        endpoint - should look like ('credits', <url>)'''
        result = list()

        #Get the feat_set that will be used to extract feats from response
        r = response
        cast_list = r['cast']
    
        #Get the desired feats to extract
        feat_set = self.entity_feat_map[entity_type]['credits']

        for person in cast_list[:8]:
            record = dict()

            #Extract and clean features from response
            for feat in feat_set:
                if feat in person:
                    #Handle nulls
                    if person[feat] in [None, ""]:
                        record[feat] = ""

                    #Handle not-nulls
                    #profile path
                    elif feat == 'profile_path':
                        if person[feat] == None:
                            record[feat] = self.profile_null
                        else:
                            profile_path = person[feat]
                            record[feat] = f'{self.profile_base}{profile_path}'
                    else:
                        record[feat] = person[feat]
                else:
                    print(f'{feat} not in response')
                    record[feat] = ""

            result.append(record)
        return result
    
    def parse_response_reviews(self, entity_type, response):
        '''Parse the response gotten for tmdb reviews, customized to response formatting.
        entity_type - "movie" or "tv"
        endpoint - should look like ('reviews', <url>)'''
        result = list()

        #Get the feat_set that will be used to extract feats from response
        r = response
        
        #Get the desired feats to extract
        feat_set = self.entity_feat_map[entity_type]['reviews']

        review_list = r['results']
        for review in review_list[:5]:
            record = dict()

            #Extract and clean features from response
            for feat in feat_set:
                #Handle not-nulls
                #username and rating
                if feat in ['username', 'rating']:
                    if review['author_details'][feat] in [None, '']:
                        record[feat] = ''
                    else:
                        if feat == 'rating':
                            #Covert from 10-scale to 5-scale
                            record[feat] = str(round(review['author_details'][feat]/2, 2)) + '/5'
                        else:
                            record[feat] = review['author_details'][feat]

                #created_at
                elif feat == 'created_at':
                    if review[feat] in [None, '']:
                        record[feat] = ''
                    else:
                        record[feat] = str(review[feat]).split('T')[0]

                #everything else
                elif feat == 'content':
                    if review[feat] in [None, '']:
                        record[feat] = ''
                    else:
                        record[feat] = review[feat]
                else:
                    print(f'{feat} not in response')
                    record[feat] = ""

            result.append(record)
        return result