
# Local path to google chrome bookmarks
import json, os
import pandas as pd

os.chdir(r'C:\\Users\\Takis\\Google Drive\\_projects_\\articles-scraping')
os.getcwd()

# ============================================================================================
# READ BOOKMARKS DATA AND PARSE INTO DF
# ============================================================================================

input_filename = os.getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Bookmarks"

f = open(input_filename, 'rb')
data = f.read()
f.close()
jj = json.loads(data)

# Iterate over folders in 'Other Bookmarks folder'
other_list = jj.get('roots').get('other').get('children')[:-1]
phone_list = jj.get('roots').get('synced').get('children')[:-1]

# len(other_list)
# other_list[0]

bk_dict = {'topic_folder':[],
           'name':[],
           'url':[]
           }

for i, b in enumerate(other_list,start=1):
    temp_topic_name = b.get("name")
    print(f'({i}) :: Topic Name :: {temp_topic_name}')
    temp_list_bmrks_in_a_topic = b.get('children')
    for j, tb in enumerate(temp_list_bmrks_in_a_topic,start=1):
        bk_dict['topic_folder'].append(temp_topic_name)
        bk_dict['name'].append(tb['name'])
        bk_dict['url'].append(tb['url'])

# df = pd.DataFrame(bk_dict)
# df.shape

# ============================================================================================
# Process BookMarks All together
# ============================================================================================

# create dictionary for mobile bookmarks
mblDict1 = { x['name'] : x['url'] for x in phone_list}
mblDict2 = { name : url for name, url in zip(bk_dict['name'],bk_dict['url'])}
mblDictConcat = {**mblDict1, **mblDict2}

# create df and extract domain
df = pd.DataFrame({'name' : list(mblDictConcat.keys()), 'url': list(mblDictConcat.values())})
import tldextract
df['domain'] = df.url.apply(lambda x : tldextract.extract(x).domain)

# write data to disk
df.to_csv('article_urls.csv')
domainList = ['towardsdatascience','medium']
dfsmall = df.loc[df.domain.isin(domainList),:]
dfsmall.to_csv('article_urls_medium.csv')
dfsmall.to_clipboard(index=False)

# candidate_domains = ['medium','towardsdatascience','analyticsvidhya','kdnuggets','machinelearningmastery','neo4j']
# df_main_domains = df.loc[df.domain.isin(candidate_domains),:].drop_duplicates()
# df_main_domains.shape
# df_main_domains.domain.value_counts()
# df_main_domains.to_clipboard()
# df_main_domains.to_pickle('./dfs/df_main_domains.pkl')


# ============================================================================================
# Apply Newspaper Goodies
# ============================================================================================

import json, os, time
import pandas as pd
import newspaper
from newspaper import Article
from datetime import datetime

def newspaper_wrapper(url):

    article_features = {}
    print(f'\nPrepare to parse url : {url}')
    try:
        start = time.time()
        article = Article(url)
        article.download()

        article.parse()
        article.nlp()

        article_features['title'] = article.title
        article_features['text'] = article.text
        article_features['keywords'] = article.keywords
        article_features['summary'] = article.summary
        article_features['language'] = article.meta_lang
        article_features['authors'] = article.authors
        article_features['publish_date'] = article.publish_date
        article_features['tags'] = article.tags
        article_features['images'] = article.images
        article_features['parsed_date'] = datetime.now()
        article_features['parse_duration'] = time.time()-start
        # article_features['links'] = article.extractor.get_urls(article.html)
        print(f"\nParsing for article titled : {article_features['title']}")
        print(f"\nParsing lasted : {article_features['parse_duration']}")

    except Exception as e:
        print(e)
        print(f'\nParsing for {url} failed')
        article_features = None
    finally:
        print(50*'=')
        return article_features

# --------------------------------------------------------------------------------------------
# APPROACH 1 : parse information as an additional df column
# --------------------------------------------------------------------------------------------

# url = 'https://medium.com/bigdatarepublic/machine-learning-for-predictive-maintenance-where-to-start-5f3b7586acfb'
# # url = 'https://www.kaggle.com/shahules/an-overview-of-encoding-techniques'
# # url = 'https://blog.quiltdata.com/repeatable-nlp-of-news-headlines-using-apache-airflow-newspaper3k-quilt-t4-vega-a0447af57032'
# np = newspaper_wrapper(url)
#
# df_main_domains_processed = dfsmall.copy()
# df_main_domains_processed['json'] = df_main_domains_processed.url.apply(newspaper_wrapper)
# df_main_domains_processed.to_clipboard()


# --------------------------------------------------------------------------------------------
# APPROACH 2 : create a new dataframe
# --------------------------------------------------------------------------------------------

start = time.time()
parsed_urls = []
for url in df.url:
    parsed_urls.append(newspaper_wrapper(url))

end = time.time()
print(f'Process took {end-start}')

legitData = [parsed for url,parsed in zip(dfsmall.url,parsed_urls) if url is not None and parsed is not None]
legitUrls = [url for url,parsed in zip(dfsmall.url,parsed_urls) if url is not None and parsed is not None]

parsedf = pd.DataFrame(legitData, index = legitUrls)
parsedf.index.name = 'url'
parsedf.isnull().sum()
parsedf.to_csv('parsed_article_urls_medium.csv')

loadcsv = pd.read_csv('parsed_article_urls_medium.csv')
loadcsv.shape
loadcsv.dtypes


###################################################################
# NEWSPAPER LIBRARY USAGE
###################################################################

# https://github.com/codelucas/newspaper
# pip install newspaper3k

from newspaper import Article
import nltk
# nltk.download('punkt')

# url = 'https://towardsdatascience.com/getting-started-with-apache-kafka-in-python-604b3250aa05'
# df_main_domains.url.values[101]
url = 'https://blog.quiltdata.com/repeatable-nlp-of-news-headlines-using-apache-airflow-newspaper3k-quilt-t4-vega-a0447af57032'
# url = df_main_domains.url.values[13]

article = Article(url)
article.download()
article.html

article.parse()
article.authors
article.publish_date
article.text
article.tags
article.images

article.nlp()
article.keywords
article.summary

links = article.extractor.get_urls(article.html)
#
# for x in links:
#     print(x)

###################################################################
# EXPLORE NEWSPAPER FUNCTIONALITY
###################################################################

import newspaper


def mypaper(paper):
    print('\nCATEGORIES :')
    for i, category in enumerate(paper.category_urls(),start=1):
        print(i, category)
    print('\nARTICLES :')
    for i,article in enumerate(paper.articles,start=1):
        print(i, article.url)
    print(f'\nTotal paper size : {paper.size()}')


capital_paper = newspaper.build('http://capital.gr',memoize_articles=False)
naftemporiki_paper = newspaper.build('https://www.naftemporiki.gr/',memoize_articles=False)


mdm_paper = newspaper.build('https://medium.com/topic/data-science/',memoize_articles=False)
tds_paper = newspaper.build('https://towardsdatascience.com',memoize_articles=False)
kdn_paper = newspaper.build('https://kdnuggets.com',memoize_articles=False)
avd_paper = newspaper.build('https://www.analyticsvidhya.com/blog',memoize_articles=False)

mypaper(mdm_paper)

###################################################################
# BS4 EXTRACT LINKS
###################################################################

import requests
import re
from bs4 import BeautifulSoup
soup = BeautifulSoup(article.html,'lxml')

analytics_vidhya_pattern = pattern = r'(https://www.analyticsvidhya.com/blog/201[0-9]/0?[0-9]{2})(/[a-zA-z-]*)(/.*)'

internal_links = []
for x in soup.find_all('a',href=re.compile(pattern)):
    inurl = x.get('href')
    matchlist = re.findall(pattern, inurl)
    if len(matchlist[0][2])<2:
        internal_links.append(inurl)

###################################################################
# SPACY ENTITY EXTRACTION
###################################################################

# https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da
import spacy
from spacy import displacy
from collections import Counter
# python -m spacy download en_core_web_sm
import en_core_web_sm
nlp = en_core_web_sm.load()

text = article.text

doc = nlp(text)
print([(X.text, X.label_) for X in doc.ents])

items = [x.text for x in doc.ents]
TOP_N_KEYWORDS = 5
Counter(items).most_common(TOP_N_KEYWORDS)
spacy_keywords = [x.lower() for x,_ in Counter(items).most_common(TOP_N_KEYWORDS)]
keywords_total = list(set(spacy_keywords + article.keywords))

( len(keywords_total) - len(article.keywords) )/ len(article.keywords)
len(article.keywords)

# sentences = [x for x in doc.sents]
# print(sentences[20])
# displacy.render(nlp(str(sentences[20])), jupyter=True, style='ent')


###################################################################
# NLTK ENTITY EXTRACTION
###################################################################

import nltk
from nltk.tag import StanfordNERTagger

print('NTLK Version: %s' % nltk.__version__)
#
# stanford_ner_tagger = StanfordNERTagger(
#     'stanford_ner/' + 'classifiers/english.muc.7class.distsim.crf.ser.gz',
#     'stanford_ner/' + 'stanford-ner-3.9.2.jar'
# )
#
# results = stanford_ner_tagger.tag(article.split())
#
# print('Original Sentence: %s' % (article))
# for result in results:
#     tag_value = result[0]
#     tag_type = result[1]
#     if tag_type != 'O':
#         print('Type: %s, Value: %s' % (tag_type, tag_value))