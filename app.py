from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import hashlib

f = open('dbproperties', 'r', encoding="utf-8");
dbdata = f.readline();

client = MongoClient(dbdata)
db = client.playlist

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.8nebtyu.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/', methods=["GET"])

def home():
    return render_template('index.html')


@app.route("/regist", methods=["GET"])
def registForm():
    return render_template('registForm.html')


@app.route("/regist/idcheck", methods=["GET"])
def idCheck():
    id = request.args.get('id');
    checkid = db.users.find_one({'userId': id}, {'_id': False});
    msg = 'fail' if checkid is not None else 'ok';
    return jsonify({'msg': msg});


@app.route("/regist", methods=["POST"])
def user_save():
    id = request.form['id'];
    pwd = hashlib.sha256(request.form['pwd'].encode("utf-8")).hexdigest();
    name = request.form['name'];
    doc = {
        'userId': id,
        'userPwd': pwd,
        'userName': name
    }
    db.users.insert_one(doc);
    checkid = db.users.find_one({'userId': id}, {'_id': False});
    return render_template('index.html');


@app.route("/", methods=["POST"])
def insertForm():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    userInfo = db.users.find_one({'userId': id_receive}, {'_id': False})
    find_id = userInfo['userId'];
    find_pwd = userInfo['userPwd'];
    input_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    receive_hash = hashlib.sha256(find_pwd.encode('utf-8')).hexdigest()
    if id_receive == find_id:
        if receive_hash == input_hash:
            return render_template("test.html", id_sender='id')
        else:
            return jsonify({'msg': '패스워드를 입력하세요!'})
    else:
        return jsonify({'msg': 'ID를 입력하세요!'})

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
    app.run('0.0.0.0', port=5000, debug=True)
