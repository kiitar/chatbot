# -*- coding: utf-8 -*-
import os
import optparse
import pickle
import fasttext
import json
import connectDB
import utilityMethod
import numpy

from flask import Flask, request, g
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

default_port = 5000

parser = optparse.OptionParser()
parser.add_option("-P", "--port",
                  help="Port for the Flask app " + "[default %s]" % default_port, default=default_port)
options, _ = parser.parse_args()

app = Flask(__name__)
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    app.config['SECRET_KEY'] = 'banana ai secret key #@'
auth = HTTPBasicAuth()
# api = Api(app)

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

utilityMethod.initiate()

@app.route('/')
def Home():
    return jsonify({})


@app.route('/message/<m>')
# @auth.login_required
def Message(m):
    multi = True if request.args.get('multi') else False
    if m is None or m == "":
        return jsonify("missing message!")
    result = utilityMethod.test(m, multi)
    print('res : ',result)
    return json.dumps(result, cls=MyEncoder , ensure_ascii=False).encode('utf8')
    # return jsonify({**result})


@app.route('/train/')
# @auth.login_required
def Train():
    m = request.args.get('m')
    i = request.args.get('i')
    if m is None or m == "" or i is None or i == "":
        return jsonify("missing message or intent!")
    utilityMethod.train(m, i)
    return jsonify("trained")


@app.route('/delete/')
# @auth.login_required
def Delete():
    m = request.args.get('m')
    i = request.args.get('i')
    if m is None or m == "":
        return jsonify("missing message!")
    if i is None or i == "":
        i = ""
    utilityMethod.delete(m, i)
    return jsonify("deleted")

# dev func


@app.route('/loadexpession/')
def LoadExpression():
    res = utilityMethod.load_expression_json()
    return jsonify(res)


@app.route('/loadwordintent/')
def LoadWordIntent():
    res = utilityMethod.load_word_intent()
    return jsonify(res)


@app.route('/retest/')
# @auth.login_required
def ReTest():
    res = utilityMethod.retest()
    return jsonify(res)

# word-intent


@app.route('/word/<w>')
# @auth.login_required
def WordIntent(w):
    # get intent i for word w
    rows = connectDB.db_select(
        "select word, intent from word_intent where word = %s ", [w])
    intent = []
    for row in rows:
        intent.append(row[1].strip())
    return jsonify(intent)


@app.route('/word/')
# @auth.login_required
def WordIntentList():
    # list all intent
    i = request.args.get('i')
    if i is None or i == "":
        rows = connectDB.db_select(
            "select word, intent from word_intent order by intent ", [])
    else:
        rows = connectDB.db_select(
            "select word, intent from word_intent where intent = %s ", [i])
    # store to dict
    i_dict = {}
    for row in rows:
        word = row[0].strip()
        intent = row[1].strip()
        if intent not in i_dict:
            i_dict[intent] = []
        i_dict[intent].append(word)
    # reconstruct
    print(i_dict)
    ret = []
    for intent in i_dict:
        ii = {'intent': intent, 'words': []}
        ii['words'] = i_dict[intent]
        ret.append(ii)
    return jsonify(ret)


@app.route('/word/', methods=['POST'])
# @auth.login_required
def WordIntentListPost():
    # add word w intent i
    w = request.form.get('w')
    i = request.form.get('i')
    if w is None or w == "" or i is None or i == "":
        return jsonify("Missing word or intent!")

    rows = utilityMethod.searchWord(w)
    result = utilityMethod.upsertWordIntent(rows, w, i)
    print("tar test word")
    print(result)
    # return jsonify(result)
    return jsonify({'tar':'word'})


@app.route('/word/delete/<w>')
# @auth.login_required
def DeleteWordIntent(w):
    # delete word w
    i = request.args.get('i')
    if i is None or i == "":
        connectDB.db_exec("delete from word_intent where word = %s;", [w])
    else:
        connectDB.db_exec(
            "delete from word_intent where word = %s and intent = %s;", [w, i])
    return jsonify("deleted")


@app.route('/word/add/')
# @auth.login_required
def AddWordIntent():
    # add word w intent i
    w = request.args.get('w')
    i = request.args.get('i')
    if w is None or w == "" or i is None or i == "":
        return jsonify("Missing word or intent!")
    rows = utilityMethod.searchWord(w)
    result = utilityMethod.upsertWordIntent(rows, w, i)
    return jsonify(result)


@app.route('/list/<q>')
# @auth.login_required
def trainWordList(q):
    result = []
    ql = '%'+q+'%'
    rows = connectDB.db_select(
        'select message, keywords, intent from train_set where message like %s or intent like %s', [ql, ql])
    for row in rows:
        message = row[0].strip()
        keywords = row[1].strip()
        intent = row[2].strip()
        result.append({
            'message': message,
            'intent': intent,
            'keyword': keywords
        })
    return jsonify(result)
# auth


@auth.verify_password
def verify_password(token, password):
    # first try to authenticate by token
    user = None
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        rows = connectDB.db_select(
            "select id, username from users where id = %s ;", (data['id'],))
        user = {'id': rows[0][0], 'username': rows[0][1].strip()}
    except SignatureExpired:
        print("SignatureExpired")  # valid token, but expired
    except BadSignature:
        print("BadSignature")  # invalid token
    if not user:
        # try to authenticate with username/password
        rows = connectDB.db_select("select id, username, password from users where username = %s limit 1;",
                                   (token,))
        # verify password
        if len(rows) == 0 or not pwd_context.verify(password, rows[0][2].strip()):
            print("no user " + token)
            return False
        user = {'id': rows[0][0], 'username': rows[0][1].strip()}
    g.user = user
    s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
    return jsonify({'user': user['username'], 'duration': 3600,
                    'token': s.dumps({'id': user['id']}).decode('ascii')})

# class UserAuthen(Resource):
#   def get(self):
#     u = request.args.get('u')
#     p = request.args.get('p')
#     r = verify_password(u, p)
#     if not r:
#       return jsonify("authen error!")
#     else:
#       return r

# user


@app.route('/user/')
# @auth.login_required
def User():
    return jsonify({'data': 'Hello, %s!' % g.user['username']})


@app.route('/user/logout')
def UserLogout():
    return("Logout", 401)


if __name__ == '__main__':
    # app.run(host='localhost' , port=int(options.port))
    app.run(host='0.0.0.0' , port=5000)
    #app.run(port=int(options.port))
