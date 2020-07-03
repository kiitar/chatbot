# -*- coding: utf-8 -*-
from pythainlp.tokenize.newmm import mmcut
from pythainlp.corpus.thaiword import get_data
import simplebayes
import nltk.tag
import dill
#from pythainlp.corpus.thaiword import get_data
import nltk.tag
sentences=input("text : ")
with open('patterns-classify-word-thai.data', 'rb') as in_strm:
      patterns = dill.load(in_strm)
in_strm.close()
with open('bayes-classify-word-thai.data', 'rb') as in_strm:
      bayes = dill.load(in_strm)
in_strm.close()
with open('classify-word-thai.data', 'rb') as in_strm:
      tagger = dill.load(in_strm)
in_strm.close()
r=tagger(sentences)
print(r)
print(bayes.score(' '.join(mmcut(sentences,[i[0] for i in patterns]+get_data())))) # บอกความน่าจะเป็นของ tag