import asyncio
import json
from aiohttp import ClientSession

import sys
import time

class RespParser():
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
                    if feat == "backdrop_path":
                        result[feat] = self.backdrop_null
                    else:
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
                        if feat == 'profile_path':
                            record[feat] = self.profile_null

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

async def get_response_async(url, session):
    """Get reponse from each of the three endpoints: details, credits, reviews"""
    try:
        response = await session.request(method='GET', url=url)
        response.raise_for_status()
        #print(f"Response status ({url}): {response.status}")
    except HTTPError as http_err:
        #print(f"HTTP error occurred: {http_err}")
        pass
    except Exception as err:
        #print(f"An error ocurred: {err}")
        pass

    response_json = await response.json()
    return response_json

async def run_program(entity_type, endpoint, session):
    """Wrapper for running program in an asynchronous fashion."""
    try:
        url = endpoint[1]
        response = await get_response_async(url, session)

        if endpoint[0] == 'details': #Details
            result = rparser.parse_response_details(entity_type, response)

        elif endpoint[0] == 'credits': #Credits
            result = rparser.parse_response_credits(entity_type, response)

        elif endpoint[0] == 'reviews': #Reviews
            result = rparser.parse_response_reviews(entity_type, response)
        return json.dumps(result, indent=2)

    except Exception as err:
        print(f"Exception occured: {err}")
        pass

#DRIVER
#frontend paramters
entity_type = sys.argv[1]
entity_id = sys.argv[2]

rparser = RespParser()
rparser.construct_feat_endpoints(entity_type, entity_id)

start = time.time()

async def get_parsed_responses():
    async with ClientSession() as session:
        details, credits, reviews = await asyncio.gather(*[run_program(entity_type, endpoint, session) for endpoint in rparser.feat_endpoints])
    
    bundle = {'details': json.loads(details),
             'credits': json.loads(credits),
             'reviews': json.loads(reviews)}

    #RESULT OUTPUTTED TO STDOUT HERE        
    print(json.dumps(bundle)) 
    end = time.time()
    # print('time: ', end-start)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_parsed_responses())
    loop.close()

if __name__ == '__main__':
    main()



