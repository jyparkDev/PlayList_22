from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import hashlib
import os

f = open(os.getcwd()+'\dbproperties','r',encoding="utf-8");
dbdata = f.readline();

client = MongoClient(dbdata)
db = client.playlist

app = Flask(__name__)

@app.route('/',methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/regist", methods=["GET"])
def registForm():
    return render_template('registForm.html')

@app.route("/regist/idcheck", methods=["GET"])
def idCheck():
    id = request.args.get('id');
    checkid = db.users.find_one({'userId':id},{'_id': False});
    msg = 'fail' if checkid is not None else 'ok';
    return jsonify({'msg':msg});

@app.route("/regist", methods=["POST"])
def user_save():
    id = request.form['id'];
    pwd = hashlib.sha256(request.form['pwd'].encode("utf-8")).hexdigest();
    name = request.form['name'];
    doc = {
        'userId' : id,
        'userPwd' : pwd,
        'userName' : name
    }
    db.users.insert_one(doc);
    checkid = db.users.find_one({'userId': id}, {'_id': False});
    return render_template('index.html');

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
