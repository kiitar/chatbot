import optparse
import pickle
import fasttext
import psycopg2
import json
import connectDB

from pythainlp.tokenize import word_tokenize
from pythainlp.keywords import find_keyword
from gensim.models import FastText

model_file = 'model.vec'
training_file = 'train_data_2.fixed.csv'
tmp_training_file = 'tmp_train_2.txt'
test_out_file = 'test_out.csv'
intent_hash = {}
classifier = None


def initiate():
    global model_file
    global classifier
    global training_file
    global tmp_training_file
    print("initiating boot sequence...")
    load_classifier()
    print("ready")


def tokenize(m):
    wordignore = [' ', '?', '.', '*', ';', '-']
    tokens = word_tokenize(m, engine='newmm')
    # kws = find_keyword(tokens,lentext=1)
    # kws = list(kws.keys())
    kws = [w for w in tokens if w not in wordignore]
    print(kws)
    if(len(kws) == 0):
        kws = [m]
    return kws


def load_classifier():
    global classifier
    global tmp_training_file
    epoch = 10
    # write training file
    rows = connectDB.db_select(
        "select message, keywords, intent from train_set;", [])
    count = 0
    with open(tmp_training_file, "w") as t_f:
        for e in range(0, epoch):
            for row in rows:
                l = '__label__' + \
                    row[2].strip().replace(" ", "_;") + \
                    ' __label__' + row[1].strip() + "\n"
                t_f.write(l)
                count += 1
    # reload classifier
    if count > 0:
        #classifier = fasttext.train_supervised(tmp_training_file, 'class', label_prefix='__label__', pretrained_vectors='model.vec')
        classifier = fasttext.train_supervised(input="tmp_train_2.txt", lr=1 )
        classifier.save_model("model.bin")
    #return count

def load_expression_json():
    fname = "train_set.data.json"
    data = json.load(open(fname))
    count = 0
    for d in data['data']:
        m = d['text'].strip()
        i = d['entities'][0]['value'].strip().strip('\"')
        print("m " + m + " i " + i)
        kws = tokenize(m)
        count += 1
        connectDB.db_exec("insert into train_set (message, keywords, intent) values (%s, %s, %s)",
                          (m, ' '.join(kws), i))
    load_classifier()
    return("loaded " + str(count) + " messages.")


def load_word_intent():
    fname = "word_intent.data.csv"
    f = open(fname, "r")
    lines = f.read()
    lines = lines.split("\n")
    count = 0
    for line in lines:
        line = line.strip()
        l = line.split(',')
        w = l[0]
        if len(l) > 1 and l[1] != '':
            i = l[1]
            print(w + " " + i)
            count += 1
            connectDB.db_exec(
                "insert into word_intent (word, intent) values (%s, %s)", (w, i))
        else:
            print(w + " no intent")
    return("loaded " + str(count) + " words.")


def train(m, i):
    global classifier
    global tmp_training_file
    tokens = word_tokenize(m, engine='newmm')
    kws = tokenize(m)
    i = i.strip().strip('\"')
    # store to db
    connectDB.db_exec("insert into train_set (message, keywords, intent) values (%s, %s, %s)",
                      (m, ' '.join(kws), i))
    load_classifier()


def test(m, multi):
    global classifier
    kws = tokenize(m)
    classifier = fasttext.load_model("model.bin")
    c = classifier.predict([" ".join(kws)] , k= 1 )
    #c = classifier.predict([" ".join(kws)], k=-1, threshold=0.5)
    #c = classifier.predict_proba([" ".join(kws)], k=1)
    # select maximum confident
    max_conf = 0
    max_int = ''
    max_idx = 0
    idx = 0
    words = []
    intend = c[0][0][0].replace("__label__", "")
    intend = intend.replace("_;", " ")
    conf = c[1][0][0]
    if conf > max_conf:
        max_int = intend
        max_conf = conf
        max_idx = idx

    print(max_idx)

    if multi is True:
        for key in kws:
            rows = searchWord(key)
            words = defindWords(words, rows, key) if rows != "empty" else words

    result = {
        'found': " ".join(kws),
        'intent': max_int,
        'confidence': max_conf,
        'words': words
    }

    if multi is False:
        result.pop('words')

    #print(result)

    print("query: " + m + " found: " + " ".join(kws) + " word: " + kws[max_idx] + " intent: " + max_int + " confidence: " + str(max_conf))
    return result


def defindWords(words, rows, key):
    for row in rows:
        w_i = row[0].strip()
        if w_i != 'stopword' and w_i != 'noword':
            words.append({
                'message': key,
                'class': w_i
            })
    return words


def searchWord(m):
    rows = connectDB.db_select(
        "select distinct intent from word_intent where word = %s ", [m])
    if len(rows) > 0:
        return(rows)
    else:
        return("empty")


def delete(m, i):
    if i != "":
        connectDB.db_exec(
            "delete from train_set where message = %s and intent = %s ", [m, i])
    else:
        connectDB.db_exec("delete from train_set where message = %s ", [m])
    load_classifier()


def retest():
    global classifier
    global tmp_training_file
    print("testing trained data...")
    # write training file
    rows = connectDB.db_select(
        "select message, keywords, intent from train_set;", [])
    count = 0
    total = 0
    for row in rows:
        m = row[0].strip()
        i = row[2].strip()
        res = test(m, False)
        r_i = res['intent']
        r_f = res['found']
        r_c = res['confidence']
        print("m: '" + m + "' i: '" + i + "' r: '" +
              r_i + "' f: '" + r_f + "' c: " + str(r_c))
        total += 1
        if i == r_i:
            count += 1
        else:
            print("wrong! expexted: " + i + " got: " + r_i)
        print("-------------------------------")
    rate = (count/total)*100
    print("result, total: " + str(total) + " correct: " +
          str(count) + " percent: " + str(rate))
    result = {
        'total': str(total),
        'correct': str(count),
        'percent': str(rate)
    }
    return result


def upsertWordIntent(r, w, i):
    if(r == "empty"):
        connectDB.db_exec(
            "insert into word_intent (word, intent) values( %s, %s);", [w, i])
    else:
        connectDB.db_exec(
            "update word_intent set intent = %s where word = %s;", [i, w])
    return "added"
