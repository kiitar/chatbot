# -*- coding: utf-8 -*-
import os
import json
import connectDB
from pythainlp.tokenize import word_tokenize
from pythainlp.keywords import find_keyword

def tokenize(m):
  tokens = word_tokenize(m,engine='newmm')
  # kws = find_keyword(tokens,lentext=1)
  # kws = list(kws.keys())
  kws = tokens
  # print(kws)
  if(len(kws) == 0):
    kws = [m]
  return kws

def load_expression_json():
  fname = "train_set.data.json"
  data = json.load(open(fname))
  count = 0
  for d in data['data']:
    m = d['text'].strip()
    i = d['entities'][0]['value'].strip().strip('\"')
    # print("m " + m + " i " + i)
    kws = tokenize(m)
    count += 1
    connectDB.db_exec("insert into train_set (message, keywords, intent) values (%s, %s, %s)",
      (m, ' '.join(kws), i))
  print("loaded " + str(count) + " messages.")

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
      # print(w + " " + i)
      count += 1
      connectDB.db_exec("insert into word_intent (word, intent) values (%s, %s)", (w, i))
    # else:
      # print(w + " no intent")
  print("loaded " + str(count) + " words.")

load_expression_json()
load_word_intent()