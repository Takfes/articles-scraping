

import json, os, time
import pandas as pd
import tldextract

import newspaper
from newspaper import Article
from datetime import datetime

import numpy as np
import dask.dataframe as dd
import multiprocessing

os.chdir(r'C:\\Users\\Takis\\Google Drive\\_projects_\\articles-scraping')
os.getcwd()

def make_url_data():
    input_filename = os.getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Bookmarks"

    f = open(input_filename, 'rb')
    data = f.read()
    f.close()

    other_list = jj.get('roots').get('other').get('children')[:-1]
    phone_list = jj.get('roots').get('synced').get('children')[:-1]


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

    df = pd.DataFrame(bk_dict)
    df['domain'] = df.url.apply(lambda x: tldextract.extract(x).domain)
    return df


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
        print(f"\nParsing for article with title : {article_features['title']}")
        print(f"\nParsing lasted : {article_features['parse_duration']}")

    except Exception as e:
        print(e)
        print(f'\nParsing for {url} failed')
        article_features = None
    finally:
        print(50*'=')
        return article_features


df_urls = make_url_data()
df_urls.shape

############################################
# SUBSET DATA
############################################

candidate_domains = ['medium','towardsdatascience','analyticsvidhya','kdnuggets','machinelearningmastery','neo4j']
df_main_domains = df_urls.loc[df_urls.domain.isin(candidate_domains),:].drop_duplicates()
df_main_domains.shape

gg = newspaper_wrapper('https://medium.com/datathings/the-magic-of-lstm-neural-networks-6775e8b540cd')
type(gg)

df_sample = df_main_domains.head(100)

############################################
# RUN EXPERIMENT DASK VS PANDAS
############################################

from dask.distributed import Client
client = Client()
client
# client.restart()


# ==============================================
# DASK
# ==============================================
start1 = time.time()
df_sample['parsed_data'] = dd.from_pandas(df_sample, npartitions=4*multiprocessing.cpu_count()).\
    map_partitions(lambda df : df.apply((lambda row : newspaper_wrapper(row.url)),axis=1)).\
    compute(scheduler='processes')
end1 = time.time()

# pandas
start2 = time.time()
df_sample['parsed_data_pandas'] = df_sample.url.apply(lambda x : newspaper_wrapper(x))
end2 = time.time()


# df_sample['parsed_data'] = df_sample.parsed_data.apply(lambda x : json.dumps(x))

print(f'DASK Process took {end1 - start1}')
print(f'PANDAS Process took {end2 - start2}')

df_sample.to_parquet('df.parquet.gzip',compression='gzip')
df_sample.to_csv("df_sample.csv",index=False)
# df.to_parquet('df.parquet.gzip',compression='gzip')