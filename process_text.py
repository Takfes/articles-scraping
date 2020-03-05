
from time import time
from collections import Counter
import pprint

import re
import stop_words
import string

import sqlite3
import pandas as pd
from pandas import DataFrame, Series
import numpy as np

# nltk
import nltk
# nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer

# sklearn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.datasets import fetch_20newsgroups

# gensim
import gensim
from gensim import corpora
from gensim import models
from gensim.corpora.dictionary import Dictionary
from gensim.parsing.preprocessing import STOPWORDS

import pandas as pd
import spacy
from spacy import displacy
import os
os.chdir(r'C:\\Users\\Takis\\Google Drive\\_projects_\\articles-scraping')


raw = pd.read_csv('parsed_article_urls_medium.csv')
raw.shape
raw.isnull().sum()

df01 = raw.copy()
df01.dropna(subset=['text']).shape
df01.dropna(subset=['text']).isnull().sum()
df01.dropna(subset=['text'], inplace=True)
df01['str_lenght'] = df01.text.apply(lambda x : len(x))

df01.to_clipboard()

# ============================================================================================
# spaCy Usage
# ============================================================================================

# https://spacy.io/usage/spacy-101#features
# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_core_web_lg")

text1 = df01.text.iloc[0]
text2 = df01.text.iloc[10]

df01.to_clipboard()

doc = nlp("Apple is not looking at buying U.K. startup for $1 billion")
doc2 = nlp("Microsoft is attmpting to sell Greek startup for $10 million")
doc.similarity(doc2)

# # https://spacy.io/usage/visualizers
# displacy.serve(doc, style="ent", port=6789)

dir(doc)
doc.text
doc.vector
list(doc.sents)

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop)

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)

for token in doc:
    print(token.text, token.has_vector, token.vector_norm, token.is_oov)


noun_chunks = list(doc.noun_chunks)

dir(token)
token.text
token.sentiment

token.vector
doc.vector

len(token.vector)
len(doc.vector)

# ============================================================================================
# Text Preprocessing and model building
# ============================================================================================


import gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize


# def prep_corpus(series):
#     # helper
#     RE_PUNCTUATION = '|'.join([re.escape(x) for x in string.punctuation])
#     stopwords = set(STOPWORDS)
#     lemmatizer = WordNetLemmatizer()
#
#     # PREPROCESSING
#     body0 = series.str.lower().str.replace(RE_PUNCTUATION, ' ').str.strip().str.split()
#     body1 = body0.apply(lambda tokens: [token for token in tokens if token not in stopwords])
#     body2 = body1.apply(lambda tokens: [lemmatizer.lemmatize(token) for token in tokens])
#
#     # corpus for analysis
#     corpus = [" ".join(x) for x in body2]
#     return corpus
#
# corpus = prep_corpus(df01.text)
#
# train_corpus = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[i]) for i, _d in enumerate(corpus)]


def read_corpus(text_iter, tokens_only=False):
    for i, line in enumerate(text_iter):
        tokens = gensim.utils.simple_preprocess(line)
        if tokens_only:
            yield tokens
        else:
            yield gensim.models.doc2vec.TaggedDocument(tokens, [i])

train_corpus = list(read_corpus(df01.text))
test_corpus = list(read_corpus(df01.text, tokens_only=True))


max_epochs = 500
vec_size = 100
alpha = 0.025
window = 20
epochs = 100

model = Doc2Vec(size=vec_size,
                alpha=alpha,
                epochs=epochs,
                min_count=5,
                window=window,
                min_alpha=0.00025,
                dm=1)

model.build_vocab(train_corpus)

model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

ranks = []
second_ranks = []
for doc_id in range(len(train_corpus)):
    inferred_vector = model.infer_vector(train_corpus[doc_id].words)
    sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
    rank = [docid for docid, sim in sims].index(doc_id)
    ranks.append(rank)
    second_ranks.append(sims[1])

import collections
counter = collections.Counter(ranks)
print(counter)

import random
doc_id = random.randint(0, len(train_corpus) - 1)

# Pick a random document from the test corpus and infer a vector from the model
doc_id = random.randint(0, len(train_corpus) - 1)
doc_id = 188

inferred_vector = model.infer_vector(train_corpus[doc_id][0])
sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))

# df01.iloc[doc_id].text[:1000]
' '.join(train_corpus[doc_id].words)[:1000]


# Find top3 most similar
print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
for label, index in [('TOP', 1), ('SECOND', 2), ('THIRD', 3)]:
    print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(train_corpus[sims[index][0]].words)[:1000]))


# Compare and print the most/median/least similar documents from the train corpus
# print('Test Document ({}): «{}»\n'.format(doc_id, ' '.join(train_corpus[doc_id])))
print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
for label, index in [('MOST', 1), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
    print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(train_corpus[sims[index][0]].words)[:1000]))



# ============================================================================================
# Text Transformers
# ============================================================================================

# https://kavita-ganesan.com/tfidftransformer-tfidfvectorizer-usage-differences/#.XmBdlqgzaiN

