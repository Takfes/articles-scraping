
import requests, json
from datetime import datetime
import pandas as pd

#TODO : atm the search only return up to 10 items
def tds(search_parameter):

    URL = "https://medium.com/_/api/collections/towards-data-science/search?q={search_parameter}"
    pURL = URL.format(search_parameter=search_parameter.replace(" ", "%20"))
    r = requests.get(pURL)

    rtext = r.text[16:]
    reply = json.loads(rtext)
    posts = reply.get('payload').get('posts')

    articles = {}

    for x in posts:
        id = x.get('id')
        articles[id] = {}
        articles[id]['title'] = x.get('title')
        articles[id]['subtitle'] = x.get('virtuals').get('subtitle')
        articles[id]['totalClapCount'] = x.get('virtuals').get('totalClapCount')
        articles[id]['slug'] = x.get('slug')
        articles[id]['id'] = x.get('id')
        articles[id]['uniqueSlug'] = x.get('uniqueSlug')
        articles[id]['createdAt'] = datetime.fromtimestamp(int(str(x.get('createdAt'))[:10]))
        articles[id]['updatedAt'] = datetime.fromtimestamp(int(str(x.get('updatedAt'))[:10]))
        articles[id]['url'] = 'https://towardsdatascience.com/' + articles[id]['uniqueSlug']

    return articles

kk = tds('scrapy')
tt = pd.DataFrame.from_dict(kk, orient='index').sort_values(by=['totalClapCount'],ascending=False)
tt.to_clipboard(index=False)
tt.shape

tt.title
