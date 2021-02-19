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
			            'title': m['title'],
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

@app.route('/', methods=['GET'])
def client_side():
	return render_template('home.html')

	

########## RENDER TEMPLATE ########## 
@app.route('/hello/<name>')
def hello(name=None):

	#Pass in a single string
	# return render_template('hello.html', name=name)

	#Pass in a json object
	url_raw = url_for('hello', name=name)
	resp_dict = {"query_string": url_raw,
				"username": name}
	resp_j = json.dumps(resp_dict)
	return render_template('hello.html', name=resp_j)




