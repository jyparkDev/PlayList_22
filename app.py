from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import hashlib

# 웹 크롤링
import requests
from bs4 import BeautifulSoup

f = open('dbproperties', 'r', encoding="utf-8");
dbdata = f.readline();

client = MongoClient(dbdata)
db = client.playlist

app = Flask(__name__)

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
    db_info = db.users.find_one({'userId': id_receive}, {'_id': False})
    pw_test = db_info['userPwd']
    input_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    if id_receive == db_info['userId']:
        if pw_test == input_hash:
            return jsonify({'msg':"ok", 'id' : id_receive })
        else:
            return jsonify({'msg': '패스워드를 입력하세요!'})
    else:
        return jsonify({'msg': 'ID를 입력하세요!'})


# get , post
# get -> https(프로토콜)://www.naver.com(=192.168.312.123=ip):5000/come/hi?name=재용&id=1&pwd=2
# request.args.get('name') = 재용 / id = request.args.get('id') = 1 / request.args.get('pwd') =



@app.route("/come", methods=["GET"])
def playlist():
    id = request.args.get('id')
    return render_template('playlist.html', user_id=id);


@app.route("/others_playlist", methods=["GET"])
def other_list():
    userid_receive = request.args.get('id_give')
    all_playlist = list(db.users.find({}, {'_id': False}))
    name = [all_name['userName'] for all_name in all_playlist]
    userid = [all_id['userId'] for all_id in all_playlist]
    return jsonify({'my_id' : userid_receive , 'other_name' : name , 'others_id' : userid})


@app.route("/my_playlist", methods=["GET"])
def my_list():
    userid_receive = request.args.get('id_give')
    users = db.users.find({'userId': userid_receive})
    users_by_name = [user['userName'] for user in users]
    return jsonify({'id' : userid_receive , 'user_name': users_by_name })

# 내 플레이리스트 조회
@app.route('/playlist/me', methods=["GET"])
def findPlayListByMe():
    userid_receive = request.args.get('userid_give')  #근호님한테 userid 받음
    # username을 로그인 db에서 찾아오자
    username = request.args.get('username_give')
    return render_template('playListByMe.html', userid = userid_receive, username = username)

# 타인 플레이리스트 조회
@app.route('/playlist/others', methods=["GET"])
def findPlayListByOthers():
    # username을 로그인 db에서 찾아오자
    # userid_receive = request.args.get("userid_give")   # 근호님한테 userid 받음
    # loginid_receive = request.args.get("loginid_give")    # 근호님한테 loginid 받음
    userid_receive = request.args.get("userid_give")
    loginid_receive = request.args.get("loginid_give")
    username_receive = request.args.get("username_give")
    return render_template('playListByothers.html', loginid = loginid_receive, userid = userid_receive, username = username_receive)


# 음악 등록
@app.route("/music", methods=["POST"])
def music_post():
    url_receive = request.form['url_give']
    introduce_receive = request.form['introduce_give']
    userid_receive = request.form['userid_give']

    # 웹 크롤링(멜론은 노래 상세 페이지의 html이 두가지 종류 존재함)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    if soup.select_one('#conts > div.section_info > div > div.entry > div.info > div.song_name') is not None:
        title = soup.select_one('#conts > div.section_info > div > div.entry > div.info > div.song_name').text[4:].strip()
    else:
        title = soup.select_one('#downloadfrm > div > div > div.entry > div.info > div.song_name').text[3:].strip()
    if soup.select_one('#d_album_org > img') is not None:
        img = soup.select_one('#d_album_org > img')['src']
    else :
        img  = soup.select_one('#downloadfrm > div > div > div.thumb > a > img')['src']
    if soup.select_one('#conts > div.section_info > div > div.entry > div.info > div.artist > a > span:nth-child(1)') is not None:
        singer = soup.select_one('#conts > div.section_info > div > div.entry > div.info > div.artist > a > span:nth-child(1)').text
    else :
        singer = soup.select_one('#downloadfrm > div > div > div.entry > div.info > div.artist > a:nth-child(1) > span:nth-child(1)').text

    #  넘어온 loginid값의 playlist가 DB에 없으면 생성
    if db.playlist.find_one({'userid': userid_receive}) is None:
        db.playlist.insert_one({'userid': userid_receive})

    # playlist에 음악 추가
    db.playlist.update_one({"userid": userid_receive},
                    {'$addToSet': {'music':  {'title' : title, 'img' : img, 'singer' : singer, 'introduce' : introduce_receive, 'url' : url_receive}}})

    return jsonify({'msg':'선택하신 음악을 플레이리스트에 추가했습니다!'})

# 음악 리스트 조회
@app.route("/music", methods=["GET"])
def movie_get():
    userid_receive = request.args.get("userid_give")
    play_list = db.playlist.find_one({'userid': userid_receive})

    # 노래 개수
    # print(len(play_list['music']))

    return jsonify({'musics': play_list['music']})

# 댓글 등록
@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']
    userid_receive = request.form['userid_give']
    login_receive = request.form['loginid_give']

    # login한 사람 이름을 login db에서 받기
    loginname = "철수"

    # playlist에 댓글 달기
    db.playlist.update_one({"userid": userid_receive},
                    {'$addToSet': {'comments':  {'author' : loginname, 'comment' : comment_receive}}})
    return jsonify({'msg': '댓글을 달았습니다!'})

# 댓글 리스트 조회
@app.route("/comment", methods=["GET"])
def comment_get():
    userid_receive = request.args.get("userid_give")

    play_list = db.playlist.find_one({'userid': userid_receive},{'_id':0, 'userid':0, 'introduce':0})
    return jsonify({'comments': play_list['comments']})

# 뮤직 삭제
@app.route("/delete", methods=["POST"])
def music_delete():
    userid_receive = request.form['userid_give']
    title_receive = request.form['title_give']
    singer_receive = request.form['singer_give']
    introduce_receive = request.form['introduce_give']
    play_list = db.playlist.find_one({'userid': userid_receive}, {'_id': 0, 'userid': 0, 'introduce': 0})
    print(play_list['music'])

    # 플레이리스트 안의 뮤직 삭제
    db.playlist.update_one(
        {},
        { '$pull': {
            'music': {
                'title' : title_receive
            }
    }   },
    # {'multi':'true'}
    );




    return jsonify({'msg': '해당 음악을 삭제했습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
