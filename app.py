import flask
from flask import Flask, url_for, render_template, request, jsonify
from flask_cors import CORS

from markupsafe import escape
import json
import requests
import subprocess, ast

from views import HomePage, SearchPage, RespParser

# from azure.storage.blob import BlobClient, BlobServiceClient

app = Flask(__name__)
CORS(app)

########## URL BUILDING ########## 
@app.route('/home', methods=['GET'])
def home():

	#DRIVER
	home = HomePage()
	home_doc_resp = flask.jsonify(home.home_doc)
	home_doc_resp.headers.add('Access-Control-Allow-Origin', '*')
	return home_doc_resp
	# return render_template('home.html', doc=home_doc_resp)
	# return render_template('xhr_test.html', doc=home_doc_resp)

@app.route('/search', methods=['GET'])
def search():
	'''Search based off of content_type and search_terms.
	Ex: /search?content_type=tv&search_terms=office

	content_type - movie, tv, multi
	search_terms - a string of one or more tokens'''
	content_type = request.args['content_type']
	search_terms = request.args['search_terms']
	        
	#DRIVER
	sp = SearchPage(content_type, search_terms)
	sp.get_content()
	search_doc_resp = flask.jsonify(sp.doc)
	search_doc_resp.headers.add('Access-Control-Allow-Origin', '*')
	return search_doc_resp

@app.route('/detail', methods=['GET'])
def detail():
	'''Get details for a given entity_type and entity_id.
	Ex: /detail?entity_type=movie&entity_id=155

	entity_type - movie, tv
	entity_id - tmdb id to get details for'''

	entity_type = request.args['entity_type']
	entity_id = request.args['entity_id']
	        
	#DRIVER
	#Must load string to dict, before jsonifying 
	bundle = subprocess.run(['python', 'get_details.py', entity_type, entity_id], capture_output=True, text=True)
	bundle_j = json.loads(bundle.stdout)

	detail_resp = flask.jsonify(bundle_j)
	detail_resp.headers.add('Access-Control-Allow-Origin', '*')
	return detail_resp


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

############# URL QUERY STRING ############
#TEST URL: http://127.0.0.1:5000/query?content_type=movie&search_terms=dark+knight
@app.route("/query")
def query():
	args = request.args
	content_type = args['content_type']
	search_terms = args['search_terms']
	#Construct url


	return "Check console for output", 200




