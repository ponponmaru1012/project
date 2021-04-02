import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.request as req

'''Headless設定'''
options = Options()
options.binary_location = '../headless/python/bin/headless-chromium'
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")

'''ブラウザの起動と検索ページへの移動'''
browser = webdriver.Chrome(executable_path="../headless/python/bin/chromedriver", options=options)
URL = 'https://etsuran.mlit.go.jp/TAKKEN/kensetuKensaku.do'
browser.get(URL)
time.sleep(3)


'''検索条件の指定と検索実行'''
#表示件数の指定(50件表示)
disp_num_select = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[4]/div/div[6]/div[3]/select')
select = Select(disp_num_select)
frm1 = select.select_by_index(4)
#検索都道府県の指定
pref_select = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[4]/div/div[5]/div[2]/select[2]')
select = Select(pref_select)
frm2 = select.select_by_index(0) #とりあえず北海道でテスト
button = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[4]/div/div[6]/div[5]/img')
button.click()
print('地域を{0}で選択し検索を実行しました'.format(frm2.text))


'''検索結果として表示されるurlとhtmlをリストで取得'''
#検索結果ページ数の取得
page_num = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[6]/div[3]/select')
lst = page_num.text.split('/')

for i in lst[1]:
    #ページ移動
    page_num_select = Select(page_num)
    to_page = page_num_select.select_by_index(i)
    
    #検索結果ページのurlを取得
    current_url = browser.current_url
    response = req.urlopen(current_url)
    
    #ページ内<a>タグ全取得からの不要ページの<a>タグ除外
    parse_html = BeautifulSoup(response, 'html.parser')
    list_all = parse_html.find_all('a') 
    #前から9個後ろ1個の<a>タグが不要
    list_all_a = list_all[9:] #前から9個
    url_list = list_all_a[:-1] #後から1個
    
    html_list = []
    
    for i in url_list:
        html = req.get(url_list[i])
        html_list[i] = BeautifulSoup(html.text, 'html.parser')
        
    df_url_html = pd.Dataframe({'URL':url_list, 'HTML':html_list})
    df_url_html.to_csv('samp.csv')
    