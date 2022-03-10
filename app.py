from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, url_for, redirect
import config
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)

client = MongoClient(config.Mongo_key)
db = client.dbsparta

SECRET_KEY = config.SECRET_KEY


@app.route('/')
def home():
    return render_template('home.html')


### sign_up api ###
@app.route('/signup')
def sign_up():
    return render_template('sign_up.html')


@app.route('/signup/save', methods=['POST'])
def sign_up_save():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pwcheck_receive = request.form['pwcheck_give']

    # 패스워드 일치하는지 검사
    if pw_receive == pwcheck_receive:
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.users.insert_one({'id': id_receive, 'pw': pw_hash})
        return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})
    elif pw_receive != pwcheck_receive:
        return jsonify({'result': 'fail', 'msg': '패스워드가 일치 하지 않습니다.'})


@app.route('/signup/idcheck', methods=['POST'])
def sign_up_idcheck():
    # 아이디중복검사
    id_receive = request.form['id_give']
    result = db.users.find_one({'id': id_receive}, {"_id": False})
    if result is not None:
        return jsonify({'result': 'fail', 'msg': '중복된 아이디가 존재합니다.'})
    elif result is None:
        return jsonify({'result': 'success', 'msg': '아이디 중복체크완료!'})


### login api #####
@app.route('/sign_in', methods=['POST'])  # 로그인 API
def sign_in():
    id_receive = request.form['give_id']
    pw_receive = request.form['give_pw']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()  # 패스워드 암호화

    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})  # 동일한 유저가 있는지 확인

    if result is not None:  # 동일한 유저가 없는게 아니면, = 동일한 유저가 있으면,
        payload = {
            'id': id_receive,

            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            # .decode('utf8')  # 토큰을 건내줌.


        return jsonify({'result': 'success', 'token': token})
    else:  # 동일한 유저가 없으면,
        return jsonify({'result': 'fail', 'msg': '아이디/패스워드가 일치하지 않습니다.'})


###top10###
@app.route('/top10')
def top10():
    return render_template('top10.html')


### review_list api ###
@app.route('/main/post', methods=['POST'])
def review_post():
    title_receive = request.form['title_give']
    loc_receive = request.form['loc_give']
    star_receive = request.form['star_give']
    review_receive = request.form['review_give']

    if 'file_give' in request.files:
        file = request.files["file_give"]
        filename = secure_filename(file.filename)
        file.save("./static/upload/"+filename)

    reviews_list = list(db.reviews.find({}, {'_id': False}))
    count = len(reviews_list) + 1

    doc = {
        'num' : count,
        'title': title_receive,
        'loc': loc_receive,
        'star': star_receive,
        'review': review_receive,
        'img_file':filename
    }

    db.reviews.insert_one(doc)

    return jsonify({'msg': '저장완료!'})


### 리뷰 수정 ###
@app.route('/main/post/update', methods=['POST'])
def review_post_upadte():
    num_receive = request.form['num_give']
    title_receive = request.form['title_give']
    loc_receive = request.form['loc_give']
    star_receive = request.form['star_give']
    review_receive = request.form['review_give']


    db.reviews.update_one({'num':int(num_receive)},
                          {'$set':{'title':title_receive,'loc':loc_receive,'star':star_receive,'review':review_receive}})


    return jsonify({'msg': '수정완료!'})


@app.route('/main/get', methods=['GET'])
def review_get():
    review_list = list(db.reviews.find({}, {'_id': False}))
    return jsonify({'reviews': review_list})


@app.route('/top10/api', methods=['GET'])
def top10_api():
    top10_list = list(db.top10.find({}, {'_id': False}))

    return jsonify({'top10': top10_list})


################
@app.route('/main')
def main_main():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})

        return render_template('review_list.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("home", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("home", msg="로그인 정보가 존재하지 않습니다."))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
