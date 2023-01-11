from flask import Flask, render_template, request, jsonify
import hashlib

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.irjpymr.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def insertForm():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']

   # user_all = list(db.users.find({'name': id_receive},{'age': pw_receive}))
   # user_all = list(db.users.find({'name': id_receive}))


   db_info = db.users.find_one({'name': id_receive},{'_id':False})
   # id = db.users.find_one({'name': id_receive})['name']
   # pw = db.users.find_one({'age': pw_new})['age']
   print(db_info)
   print(id_receive)

   test = str(db_info['age'])

   input_hash= hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
   receive_hash = hashlib.sha256(test.encode('utf-8')).hexdigest()

   if id_receive == id:
      if receive_hash == input_hash:
         return render_template("test.html", id_sender = 'id' )
      else:
         return jsonify({'msg':'패스워드를 입력하세요!'})
   else:
      return jsonify({'msg':'ID를 입력하세요!'})
@app.route("/regist", methods=["GET"])
def registForm():
   return render_template('registForm.html')

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

