from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.8nebtyu.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
   return render_template('index.html')

@app.route("/all_user", methods=["GET"])
def playlist_get():
    all_playlist = list(db.test.find({}, {'_id': False}))
    return jsonify({'playlists':all_playlist})

@app.route("/user", methods=["GET"])
def user_id():
    id_receive = 'id_give'
    # other_receive = 'id_give'
    return render_template(my_id=id_receive)




if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

