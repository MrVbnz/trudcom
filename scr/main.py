import urllib.parse
import requests
import time
import re
import pandas as pd
import csv
import string
import base64
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

stop_words = stopwords.words("russian")
stop_words.extend(stopwords.words("english"))
spec_chars = string.punctuation + '\n\xa0«»\t—…'

def add_words(words, word_list):
    for word in words:
        if word in stop_words or word.find('span') != -1:
            continue
        if word in word_list:
            word_list[word] += 1
        else:
            word_list[word] = 1

def remove_chars_from_text(text, chars):
    return ''.join([ch for ch in text if ch not in chars])

def parse_indeed():
    main_url = 'https://russia.trud.com'
    vacancies_url = 'jobs/'
    q = 'administrator_baz_dannih'  # Задаем интересующее название вакансии
    url = main_url + '/' + vacancies_url + q;
    print(url)
    word_list = {"":0}
    for page in range(1,150):
        word_list = parse_vacancy_links(url+'/page/'+str(page), word_list)
    link_list_to_csv(word_list,q)

def get_content(url):
    return requests.get(url).content.decode()

def parse_vacancy_links(url, word_list):
    print(url)
    cnt = get_content(url) 
    find_urls = re.compile(r"class=\"item-description\">(.*?)<!")
    matches = find_urls.finditer(cnt, re.MULTILINE)    
    for match in matches:
        text = match.group(1)
        text = text.lower()
        text = remove_chars_from_text(text, spec_chars)
        text = remove_chars_from_text(text, string.digits)
        add_words(text.split(), word_list)
    return word_list

def link_list_to_csv(link_list, q):
    counter = 0
    with open(q+'_desc.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["word", "count"])
        srt = {k: v for k, v in sorted(link_list.items(), key=lambda item: -item[1])}
        for a in srt.keys():
            writer.writerow([a,str(srt[a])])
            counter = counter + 1

parse_indeed()
