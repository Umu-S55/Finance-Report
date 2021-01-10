#! python3
# main.py - EPS/Revenueを取得するスクリプト


import re
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Kilo,Million,Billion変換
def KMB_Convert(moji):
    print('moji is{}'.format(moji))
    # moji_num = re.findall(r'[-+]?\d*\.\d+', moji)
    moji_num = re.findall(r'[-+]?[$]+\d*\.\d+', moji)
    moji_num[0] = moji_num[0].replace('$', '')
    print('moji num is{}'.format(moji_num))
    moji_unit = re.findall(r'[KMB]+', moji)
    moji_num = float(moji_num[0])
    if moji_unit:
        moji_unit = moji_unit[0]
    if 'K' in moji_unit:
        moji_num *= 1000
    elif 'M' in moji_unit:
        moji_num *= 1000000
    elif 'B' in moji_unit:
        moji_num *= 1000000000
    elif 'T' in moji_unit:
        moji_num *= 100000000000
    else:
        moji_num = moji_num
    return moji_num


# This Funcion is currently not working.
def Avoid_Page(URL):
    options = Options()
    # TODO: webページの取得
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    searchBtn = driver.find_element_by_id("px-captcha")
    cnt = 0
    while cnt <= 10000:
        webdriver.ActionChains(driver).click_and_hold(searchBtn).perform()
        time.sleep(0.001)
        cnt += 1


if __name__ == '__main__':
    # TODO: 検索対象のコードを読みこむ

    ticker_code = []
    tik = 'AAA'
    while True:
        print("Input Ticker Code (Ex:'AAPL'):")
        print("If you finish your input, please enter 'end'. ")
        tik = input()
        if tik == 'end':
            break
        ticker_code.append(tik)
    # TODO: コードの数だけ処理を繰り返す
    for code in ticker_code:
        URL = 'https://seekingalpha.com/symbol/' + code + '/' + 'earnings'
        URL2 = 'https://seekingalpha.com/symbol/' + code

        # TODO: データスクレイピング
        options = Options()
        # TODO: webページの取得
        driver = webdriver.Chrome(options=options)
        driver.get(URL2)
        # TODO: ロボット回避
        h1_tag = driver.find_elements_by_tag_name("h1")
        for h1_selector in h1_tag:
            print(h1_selector.text)
            if h1_selector.text == 'To continue, please prove you are not a robot':
                searchBtn = driver.find_element_by_id("px-captcha")
                cnt = 0
                while cnt <= 150:
                    webdriver.ActionChains(driver).click_and_hold(searchBtn).perform()
                    time.sleep(0.1)
                    cnt += 1

        time.sleep(5)
        link_elem = driver.find_element_by_link_text("Earnings")
        link_elem.click()
        time.sleep(5)
        # 決算時期取得
        row_period = driver.find_elements_by_class_name("title-period")
        actual_period = []
        if row_period:
            for period in row_period:
                actual_period.append(period.text[10:-1])
        print('period:{}'.format(actual_period))

        # EPS取得
        row_eps = driver.find_elements_by_class_name("eps")
        eps_actual_lst = []
        eps_estimate_lst = []
        eps_surprise_lst = []
        if row_eps:
            for eps in row_eps:
                actual_eps = re.findall(r'[-+]?[$]+\d*\.\d+[KMB]*', eps.text)
                actual_eps[0] = float(actual_eps[0].replace('$',''))
                actual_eps[1] = float(actual_eps[1].replace('$',''))
                actual_eps[1] = actual_eps[0] - actual_eps[1]
                eps_actual_lst.append(actual_eps[0])
                eps_estimate_lst.append(actual_eps[1])
                eps_surprise = 0
                eps_surprise = actual_eps[0] - actual_eps[1]
                print(eps_surprise)
                if eps_surprise < 0:
                    eps_surprise_lst.append((abs(eps_surprise)/abs(actual_eps[1])) * 100 * -1)
                else:
                    eps_surprise_lst.append((abs(eps_surprise)/abs(actual_eps[1])) * 100)
        print('EPS_Actual:{}'.format(eps_actual_lst))
        print('EPS_Estimate:{}'.format(eps_estimate_lst))
        print('EPS_Surprise:{}'.format(eps_surprise_lst))

        # Revenue(売上高)取得
        row_revenue = driver.find_elements_by_class_name("revenue")
        revenue_actual_lst = []
        revenue_estimate_lst = []
        revenue_surprise_lst = []
        if row_revenue:
            for revenue in row_revenue:
                revenue_lst = []
                actual_rev = re.findall(r'[-+]?[$]+\d*\.\d+[KMB]*', revenue.text)
                for rev in actual_rev:
                    revenue_lst.append(KMB_Convert(rev))
                print(revenue_lst)
                revenue_lst[1] = revenue_lst[0] - revenue_lst[1]
                revenue_surprise = 0
                revenue_surprise = revenue_lst[0] - revenue_lst[1]
                print(revenue_surprise)
                if revenue_surprise < 0:
                    revenue_lst.append((abs(revenue_surprise)/abs(revenue_lst[1])) * 100 * -1)
                else:
                    revenue_lst.append((abs(revenue_surprise)/abs(revenue_lst[1])) * 100)
                revenue_actual_lst.append(revenue_lst[0])
                revenue_estimate_lst.append(revenue_lst[1])
                revenue_surprise_lst.append(revenue_lst[2])
        print('Revenue Actual:{}'.format(revenue_actual_lst))
        print('Revenue Estimate:{}'.format(revenue_estimate_lst))
        print('Revenue Surprise:{}'.format(revenue_surprise_lst))

        # TODO: データ処理
        period_list = pd.Series(actual_period)
        eps_act_list = pd.Series(eps_actual_lst)
        eps_est_list = pd.Series(eps_estimate_lst)
        eps_sps_list = pd.Series(eps_surprise_lst)
        revenue_act_list = pd.Series(revenue_actual_lst)
        revenue_est_list = pd.Series(revenue_estimate_lst)
        revenue_sps_list = pd.Series(revenue_surprise_lst)

        finance_report_df = pd.concat([period_list,
                                       eps_act_list, eps_est_list, eps_sps_list,
                                       revenue_act_list, revenue_est_list, revenue_sps_list], axis=1)
        finance_report_df.columns=['Period', 'EPS(Actual)', 'EPS(Estimate)', 'EPS(Surprise)',
                                   'Revenue(Actual)', 'Revenue(Estimate)', 'Revenue(Surprise)']
        print(finance_report_df)
        # TODO: CSVファイルに結果を書き込み
        finance_report_df.to_csv('finance_report_{}.csv'.format(code),sep='\t',encoding='utf-16')
        driver.quit()
