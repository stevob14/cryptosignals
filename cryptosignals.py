import requests
import time

def coinpaprika_api():
    api = "https://api.coinpaprika.com/v1/tickers/"
    try:
        data = requests.get(api,timeout=5).json()
        return data
    except requests.exceptions.RequestException:
        return False
    except (ValueError):
        return False

def historical_price(id,start,end):
    api = "https://api.coinpaprika.com/v1/coins/" + id + "/ohlcv/historical?start=" + str(start) + "&end="+ str(end)
    try:
        data = requests.get(api,timeout=5).json()
        return data
    except requests.exceptions.RequestException:
        return False
    except (ValueError):
        return False


def bullish_filter(data):
    filtered_data = [x for x in data if x['rank'] < 101 and (x['quotes']['USD']['volume_24h_change_24h'] > 1 and x['quotes']['USD']['percent_change_24h'] > 1) or (x['quotes']['USD']['volume_24h_change_24h'] < 1 and x['quotes']['USD']['percent_change_24h'] < -1)]
    return filtered_data

def bearish_filter(data):
    filtered_data = [x for x in data if x['rank'] < 101 and (x['quotes']['USD']['volume_24h_change_24h'] > 1 and x['quotes']['USD']['percent_change_24h'] < -1) or (x['quotes']['USD']['volume_24h_change_24h'] < 1 and x['quotes']['USD']['percent_change_24h'] > 1)]
    return filtered_data

def relativeStrengthIndex(prices,n):
    RSI = []
    m = len(prices)
    avgGain = 0
    avgLoss = 0

    i = 0
    while i < 14:
        change = prices[i+1] - prices[i]
        if change >= 0:
            avgGain = change + avgGain
        else:
            avgLoss = avgLoss - change
        i+=1

    avgGain = avgGain/n
    avgLoss = avgLoss/n

    t = 14

    while t < m:
        smoothedrs = avgGain/avgLoss
        RSI.append(( 100 - 100/ (1+smoothedrs)))
        if t < m-1:
            change = prices[t+1] - prices[t]
        if change >= 0:
            avgGain = (avgGain * 13 + change) / n
            avgLoss = (avgLoss * 13) / n
        else:
            avgGain = (avgGain * 13) / n
            avgLoss = (avgLoss * 13 - change) / n
        t+=1

    return RSI

def exponentialMovingAverage(prices,n):
    m = len(prices)
    a = 2/(n+1)
    EMA = []
    EMA.append(prices[0])
    i = 1
    while i < m:
        EMA.append((a * prices[i]) + ((1 - a) * EMA[i - 1]))
        i+=1
    return EMA

days = 5219689;

data = coinpaprika_api()
bullishdata = bullish_filter(data)
bearishdata = bearish_filter(data)
all_data = bullishdata + bearishdata
for x in all_data:
    prices = []
    name = x['name']
    change = x['quotes']['USD']['percent_change_24h']
    volume = x['quotes']['USD']['volume_24h_change_24h']
    id = x['id']
    endunix = time.time()
    startunix = endunix - days

    historical = historical_price(id,int(startunix),int(endunix))
    for x in historical:
        prices.append( x['close'])

    trend = "N/A"
    ema8 = exponentialMovingAverage(prices,8)
    ema21 = exponentialMovingAverage(prices,21)

    current_8 = ema8.pop()
    current_21 = ema21.pop()
    previous_8 = ema8.pop()
    previous_21 = ema21.pop()


    if current_8 > current_21 and previous_8 < previous_21:
	    trend = "Upward Trend"

    if current_8 < current_21 and previous_8 > previous_21:
	    trend = "Downward Trend"

    if trend != "N/A":
        rsi = relativeStrengthIndex(prices,14)
        current_rsi = rsi.pop()
        print(name + "\nChange(24h):" + str(change) + "\nVolume(24h):" + str(volume)+ "\nRSI(14): " + str(current_rsi) + "\nTrend:" + trend +"\n----------------------")
