from flask import Flask, render_template, request, jsonify
import config
import hashlib
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient(config.Mongo_key)
db = client.dbsparta

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def sign_up():
    return render_template('sign_up.html')

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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
