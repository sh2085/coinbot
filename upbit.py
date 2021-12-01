import datetime
import time
from ast import literal_eval
from operator import itemgetter

import pyupbit
import pandas as pd

import matplotlib.pyplot as plt

access = 'Check Your Access key'
secret = 'Check Your Secret key'

upbit = pyupbit.Upbit(access, secret)


def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * 0.35
    print('today_open = '+ str(today_open) + ' yes_high = ' + str(yesterday_high) + ' yes_low = ' + str(yesterday_low)  + ' target = ' + str(target))
    return target

def get_target_price_1h(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    lasthour = df.iloc[-2]

    print(df.iloc[-2])
    hour_open = lasthour['close']
    hour_high = lasthour['high']
    hour_low = lasthour['low']
    target = hour_open + (hour_high - hour_low) * 0.35
    print('today_open = '+ str(hour_open) + ' yes_high = ' + str(hour_high) + ' yes_low = ' + str(hour_low)  + ' target = ' + str(target))
    return target


def buy_crypto_currency(data, ticker):
    krw = upbit.get_balance(ticker = "KRW")
    if krw > 300000:
        info = upbit.buy_market_order(ticker, 300000)
        print('buy!!' + str(ticker))
        data['is_buy'] = True;
        data['buying_time'] = datetime.datetime.now()

def sell_crypto_currency(data, ticker):
    print('Sell!!' + str(ticker))
    unit = upbit.get_balance(ticker=ticker)
    upbit.sell_market_order(ticker, unit)
    data['target_price'] = 9999999999;
    data['is_buy'] = False
    data['selling_time'] = datetime.datetime.now()
    del(data['avg_buy_price'])

def sell_crypto_currency_all():
    my_balance = upbit.get_balances()

    for item in my_balance:
        if str(item['currency']) == 'KRW' or str(item['currency']) == 'USDT':
            continue

        ticker = str(item['unit_currency'] )+ '-' + str(item['currency'])
        unit = upbit.get_balance(ticker=ticker)
        upbit.sell_market_order(ticker, unit)
        print('Sell!! Coin = ' + str(ticker) + ' unit = ' + str(unit))

def get_yesterday_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(5).mean()
    print('MA5 = ' + str(ma[-2]))
    return ma[-2]

def get_total_24h_price():
    volume_list.clear()
    krw_ticker = pyupbit.get_tickers(fiat="KRW")
    for ticker in krw_ticker:
        url = "https://api.upbit.com/v1/ticker"
        querystring = {"markets": ticker}
        response = pyupbit.requests.request("GET", url, params=querystring)
        df = pd.read_json(response.text)
        volume_list.append({'coin': ticker, 'total_24h_price': df["acc_trade_price_24h"].iloc[0]})
        time.sleep(0.1)

    data = sorted(volume_list, key=itemgetter('total_24h_price'), reverse=True)
    print(data)
    del data[15:]

    return data

def updateCoin(data):
    for i, coin in enumerate(data):
        target_price = get_target_price(coin['coin'])
        # target_price = get_target_price_1h(coin['coin'])
        data[i]['target_price'] = target_price
        data[i]['is_buy'] = False
        time.sleep(0.05)
        #data[i]['ma5'] = get_yesterday_ma5(coin['coin'])

now = datetime.datetime.now()
time_24h = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1, hours=9)
time_3h = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(hours=3)
volume_list = []

data = get_total_24h_price()
updateCoin(data)
while True:
    try:
        now = datetime.datetime.now()

        if time_3h < now < time_3h + datetime.timedelta(seconds=10):
            time_3h = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(hours=3)
            data = get_total_24h_price()
            updateCoin(data)

        if time_24h < now < time_24h + datetime.timedelta(seconds=10):
            sell_crypto_currency_all()
            time_24h = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1, hours=9)
            data = get_total_24h_price()
            updateCoin(data)

        for i, coin in enumerate(data):
            balance = upbit.get_balances()

            current_price = pyupbit.get_current_price(coin['coin'])
            data[i]['current_price'] = current_price
            print(data[i])
            for item in balance:
                if item['currency'] == str(coin['coin']).split('-')[1]:
                    data[i]['avg_buy_price'] = (item['avg_buy_price'])
                    data[i]['is_buy'] = True

            if data[i]['is_buy'] == False and data[i]['current_price'] > data[i]['target_price'] :
                buy_crypto_currency(data[i], coin['coin'])
                continue

            if data[i]['is_buy'] == True:
                if data[i]['current_price'] < float(data[i]['avg_buy_price']) * 0.975 or data[i]['current_price'] >= float(data[i]['avg_buy_price']) * 1.07:
                    sell_crypto_currency(data[i], coin['coin'])

            time.sleep(0.05)
    except:
        print("에러 발생")

# df = pyupbit.get_ohlcv("KRW-BORA", interval='minute30')
# # 30개의 이동평균 계산
# ma30 = df['close'].rolling(30).mean()
# ma = pd.DataFrame(ma30)
# #ma.plot.line()
# #plt.show()
#
# #print(ma)
#
# while True:
#     url = "https://api.upbit.com/v1/candles/minutes/5"
#
#     querystring = {"market": "KRW-BORA", "count": "100"}
#
#     response = pyupbit.requests.request("GET", url, params=querystring)
#
#     data = response.json()
#
#     df = pd.DataFrame(data)
#
#     df = df['trade_price'].iloc[::-1]
#
#     ma9 = df.rolling(window=10).mean()
#     ma26 = df.rolling(window=30).mean()
#     price = pyupbit.get_current_price("KRW-BORA")
#
#     df_ma9 = pd.DataFrame(ma9)
#     df_ma30 = pd.DataFrame(ma30)
#
#     df_ma9.plot.line()
#     df_ma30.plot.line()
#
#     print('단기 이동평균선 10: ', round(ma9.iloc[-1], 2))
#     print('장기 이동평균선 30: ', round(ma26.iloc[-1], 2))
#     print('현재 가격: ', price)
#     print('')
#
#     plt.show()
#     time.sleep(10)
