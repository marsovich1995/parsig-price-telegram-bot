import requests
import difflib
import json
import re
# from bs4 import BeautifulSoup
from conf import url_for_search
from my_html_parser import FindBookId

def similarity(s1, s2): #сранить две строки на соответвие 
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()
    
def get_id_by_url(url):
    url_full = 'http://webcache.googleusercontent.com/search?q=cache:' + url #url страницы из кэша Google
    # data = session.get(url, headers = headers)
    # print(url_full)
    html = requests.get(url_full, timeout=5) # загрузить страницу
    if html.status_code == 200:
        parser = FindBookId(html=html.text) # найт на странице Book id
        if parser.buk_id != None:
            return parser.buk_id
        else:
            raise IOError("book id in html no find")    
        # soup = BeautifulSoup(html.text, 'html.parser')
        # data_html=soup.find("div", class_="product-media-icon js__product_bookmarks_button")
        # data_html = data_html.attrs
        # return data_html.get('data-book-id')
    else: 
        raise IOError("host error")

def check_text(text):

    pattern_url = re.compile(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/*?') # обнаужить любой url
    pattern_id_book = re.compile(r'^\b\d{7}\b$') # обнаужить любой url
    url=pattern_url.findall(text.lower())
    id_book = pattern_id_book.findall(text)
    if url:
        return "url"
    elif id_book:
        return "id_book"
    else:
        return False 

def chek_url(url,params = False):
    # pattern_url = regex.compile(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/*?') # обнаужить любой url
    pattern = re.compile(r'(m\.chitai-gorod.ru\/catalog\/book\/\d+)|(www\.chitai-gorod.ru\/catalog\/book\/\d+)|(?<!(\.|\w))(chitai-gorod\.ru\/catalog\/book\/\d+)')
    pattern_id = re.compile(r'(?<=book\/)\d+')
    # pattern = regex.compile(r'chitai-gorod\.ru\/catalog\/book\/\d+')
    # wrong_url = pattern_url.findall(url.lower())
    text=pattern.findall(url.lower())
    if text:
       
       
        if params == 1:
            text=pattern_id.findall(str(text))
            return 'https://www.chitai-gorod.ru/catalog/book/' + text[0] + '/'
        else:
            return 1        
    
    # elif  wrong_url:
    #     # print("not faund")
    #     return 2
    else:
        return 0

def get_data_serch(name):

    data1 = {
    'index':'goods',
    'query':'?',
    'type':'hint',
    'per_page':'18',
    'get_count':'false'
    }

    data1['query'] =  str(name)
    # print(data1)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    }

    json2 = requests.post(url_for_search,data=data1, headers = headers, timeout=5)
    if json2.status_code == 200:
        return json.loads(json2.text)
    else:
        raise IOError("connect api error")

def get_similar_value(data, name, weight=0.6):
    try:
        n = len(data['hits']['hits'])
        answer = [0] * n
        for i in range(n):
            answer[i] = similarity(name, data['hits']['hits'][i]['_source']['name'])
            # print(answer)
            max_index = answer.index(max(answer))
    except:
        return None      
 
    if answer[max_index] >= weight:
        return max_index
    else: 
        return None

def get_exact_book(data, book_id): #поиск по точному совпадению
    try:
        n = len(data['hits']['hits'])
    except:
         return None   
    for i in range(n):
        if str(data['hits']['hits'][i]['_source']['book_id']) == str(book_id):
            return i
        else:
            return None
