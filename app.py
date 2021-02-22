import flask
from flask import Flask, url_for, render_template
from flask_cors import CORS
from flask import jsonify

from markupsafe import escape
import json
import requests

# from azure.storage.blob import BlobClient, BlobServiceClient

app = Flask(__name__)
CORS(app)

#TODO: Store as an encrypted file
tmdb_key = "2e510746ca28d7041056c7e57108de4c"

########## ROUTING FEATURES ########## 
# @app.route('/')
# def index():
#     return 'index'

# @app.route('/hello')
# def hello():
#     return 'hello'

# ########## VARIABLE RULES ##########
# @app.route('/user/<username>')
# def show_user_profile(username):
#     # show the user profile for that user
#     # return 'User %s' % escape(username)

#     #URL Building
#     return '{}\'s profile'.format(escape(username))

# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     # show the post with the given id, the id is an integer
#     return 'Post %d' % post_id
# @app.route('/path/<path:subpath>')
# def show_subpath(subpath):
#     # show the subpath after /path/
#     return 'Subpath %s' % escape(subpath)

########## URL BUILDING ########## 
@app.route('/home', methods=['GET'])
def home():
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

	#DRIVER
	home = HomePage()
	home_doc_resp = flask.jsonify(home.home_doc)
	home_doc_resp.headers.add('Access-Control-Allow-Origin', '*')
	return home_doc_resp
	# return render_template('home.html', doc=home_doc_resp)
	# return render_template('xhr_test.html', doc=home_doc_resp)

@app.route('/search', methods=['GET'])
def client_side():
	class SearchPage():
	    def __init__(self):
	        #Supplied Parameters
	        self.tmdb_key = "2e510746ca28d7041056c7e57108de4c"
	        self.poster_base = "https:/www.themoviedb.org/t/p/w1280"
	        self.genre_files = ['genre_movie.json', 'genre_tv.json']
	        
	        #Computed Parameters
	        self.doc = dict()
	        self.genre_map = self.load_genres()
	        
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
	        
	        
	    def get_content(self, search_terms, content_type):
	        '''Gets content based off user content type and search terms.
	        search_terms - a string containing one or more words
	        content_type - "tv", "movie" '''
	        poster_base = "https:/www.themoviedb.org/t/p/w1280"

	        #Check if multiple search terms
	        terms_list = search_terms.split(' ')
	        if len(terms_list) >= 2: search_terms2 = "%20".join(terms_list)
	        else: search_terms2 = search_terms

	        endpoint = f"https://api.themoviedb.org/3/search/{content_type}?api_key={self.tmdb_key}&language=en-US&query={search_terms2}&include_adult=false"
	        r = requests.get(endpoint)

	        #Extract necesssary features
	        items = r.json()['results'][:10]
	        
	        #Check if feature exists, before extracting
	        desired_feats = [('id', 'i'), ('title', 's'), ('overview', 's'), ('poster_path', 'path'),
	                        ('release_date', 's'), ('vote_average', 'f'), ('vote_count', 'i'), ('genre_ids', 'l')]
	        type_null_map = {'s': 'Not Available', 'i': 0, 'l': 'Not Available', 'f': 0,
	                        'path': 'https://cinemaone.net/images/movie_placeholder.png'}
	        items_extract = list()
	        for idx, m in enumerate(items):
	            record = dict()
	            for feat in desired_feats:
	                if feat[0] not in m:
	#                     print(f'feat not found: {idx} {feat}')
	                    record[feat[0]] = type_null_map[feat[1]]
	                else:
	                    if m[feat[0]] == None: record[feat[0]] = type_null_map[feat[1]]
	                    else: record[feat[0]] = m[feat[0]]
	            items_extract.append(record)
	#         print(len(items_extract))
	#         print(items_extract)

	        #Feature engineering
	        for idx, m in enumerate(items_extract):
	            #Construct poster path, and add back to items_extract
	            poster_path = m['poster_path']
	#             print(poster_path)
	            if poster_path.split('/')[-1] == 'movie_placeholder.png': pass
	            else:
	                poster_full = f'{poster_base}{poster_path}'
	                items_extract[idx]['poster_path'] = poster_full

	            #Get the genre names
	            if m['genre_ids'] == 'Not Available': pass
	            else:
	                g_names = list()
	                for g_id in m['genre_ids']:
	                    g_name = self.genre_map[content_type][g_id]
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
	        
	#DRIVER
	content_type = "movie" #TODO: Extract from url that XHR will construct
	search_terms = "dark knight" #TODO: Extract from url that XHR will construct
	# search_terms = "joker"

	sp = SearchPage()
	sp.get_content(search_terms, content_type)
	search_doc_resp = flask.jsonify(sp.doc)
	search_doc_resp.headers.add('Access-Control-Allow-Origin', '*')
	return search_doc_resp


########## RENDER TEMPLATE ########## 
# @app.route('/hello/<name>')
# def hello(name=None):

# 	#Pass in a single string
# 	# return render_template('hello.html', name=name)

# 	#Pass in a json object
# 	url_raw = url_for('hello', name=name)
# 	resp_dict = {"query_string": url_raw,
# 				"username": name}
# 	resp_j = json.dumps(resp_dict)
# 	return render_template('hello.html', name=resp_j)




