#とあるサイトからスクレイピングを行いhtmlを取得し、csvにしてlambdaからs3へアップロード
from selenium import webdriver
import json
import time
import datetime
import csv
import boto3
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

def lambda_handler(event, context):
    
    '''ブラウザの定義と移動'''
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=880x996")
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")
    options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1')
    options.binary_location = "/opt/python/bin/headless-chromium"
    URL = "https://etsuran.mlit.go.jp/TAKKEN/kensetuKensaku.do"
    browser = webdriver.Chrome("/opt/python/bin/chromedriver", options=options)
    browser.get(URL)
    time.sleep(3)
    
    
    '''検索条件の指定と検索の実行'''
    #表示件数の指定
    disp_num_select = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[4]/div/div[6]/div[3]/select')
    select = Select(disp_num_select)
    select.select_by_index(4) #50件に設定
    
    #検索都道府県の指定
    pref_select = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[4]/div/div[5]/div[2]/select[2]')
    select = Select(pref_select)
    select.select_by_index(1) #北海道が1、沖縄が47のように引数を指定
    
    #検索実行
    button = browser.find_element_by_xpath('/html/body/form/div/div[2]/div[4]/div/div[6]/div[5]/img')
    button.click()
    
    
    '''メインロジック開始'''
    obj_html_list = []
    
    '''
    #ページネーターを使って全件取得ループ
    pagenator = browser.find_element_by_id('pageListNo1')
    pagenator_select = Select(pagenator)
    pagenator_list = [i.text for i in pagenator_select.options] #ページネーターの名前リストを作成
    for item in pagenator_list:
        pagenator = browser.find_element_by_id('pageListNo1')
        pagenator_select = Select(pagenator)
        pagenator_select.select_by_visible_text(item)
    !件数多く、Lambdaのセッション切れになってしまうため、サンプル50件で動かす!(全件取得はコメントアウトしてるコードも使う)
    '''
    
    
    #画面に表示されている建設業者50件のリンク先を取得
    list_all = browser.find_elements_by_tag_name('a')
    list_all_a = list_all[8:] #前から8個削除
    list_all_b = list_all_a[:-1] #後ろから一個削除
    link_name_list = [i.text for i in list_all_b] #リンク名のリストを作成
    
    #目的階層へ行きhtml取得しブラウザバック
    for item in link_name_list:
        obj= browser.find_element_by_link_text(item)
        obj.click()
        obj_html_list.append(browser.page_source)
        browser.back()
        browser.implicitly_wait(7)
            
    '''メインロジック終了'''
    
    
    '''csvファイルに書き出してS3へアップロード'''
    #ユニークな日時をファイル名に指定し、リストをcsvファイルに
    now = datetime.datetime.now()
    file_path_and_name = '/tmp/' + now.strftime('%Y%m%d_%H%M%S') + '.csv'
    with open(file_path_and_name, "w") as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(obj_html_list)
        
    #csvファイルをS3へアップロード
    backet_name = ''
    savepath = now.strftime('%Y%m%d_%H%M%S') + '.csv' #バケット直下にファイルを保存
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(file_path_and_name, baket_name, savepath)
    
    
    return
    #return json.dumps(obj_html_list, default=str, ensure_ascii=False)
