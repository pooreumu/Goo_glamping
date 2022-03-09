from flask import Flask, render_template, request, jsonify
import config
import jwt
import hashlib
import datetime
from datetime import datetime, timedelta
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient(config.Mongo_key)
db = client.dbsparta

SECRET_KEY = config.SECRET_KEY

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def sign_up():
    return render_template('sign_up.html')

@app.route('/main')
def main():
    return render_template('review_list.html')

@app.route('/signup/save', methods=['POST'])
def sign_up_save():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pwcheck_receive = request.form['pwcheck_give']
    print(id_receive, pwcheck_receive, pwcheck_receive)
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  # 토큰을 건내줌.

        return jsonify({'result': 'success', 'token': token})
    else:  # 동일한 유저가 없으면,
        return jsonify({'result': 'fail', 'msg': '아이디/패스워드가 일치하지 않습니다.'})


###top10###
@app.route('/top10')
def top10():
    return render_template('top10.html')

@app.route('/top10/api', methods=['GET'])
def top10_api():
    top10_list = list(db.top10.find({},{'_id':False}))
    print(top10_list)
    return jsonify({'top10': top10_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)