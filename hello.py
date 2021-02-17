from flask import Flask, url_for, render_template
from markupsafe import escape
import json
import requests

app = Flask(__name__)

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
@app.route('/')
def index():
	return 'fart'

@app.route('/login')
def login():
	return 'fart'

@app.route('/user/<username>')
def profile(username):

	#Test: Return a json object based on query string params
	url_raw = url_for('profile', username=username)
	resp_dict = {"query_string": url_raw,
				"username": username}
	resp_j = json.dumps(resp_dict)
	return resp_dict

@app.route('/home')
def home():
	endpoint_trend = f'https://api.themoviedb.org/3/trending/movie/week?api_key={tmdb_key}'
	r = requests.get(endpoint_trend)
	return r.json()



########## RENDER TEMPLATE ########## 
@app.route('/hello/<name>')
def hello(name=None):

	#Pass in a single string
	return render_template('hello.html', name=name)



