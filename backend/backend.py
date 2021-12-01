import datetime as dt

import pandas_datareader as pdr
import yfinance_ez as yf


all_crypto = {
    "eth": "ETH-USD",
    "btc": 'BTC-USD',
    "lrc": 'LRC-USD',
    "bnb": 'BNB-USD',
    "usdt": 'USDT-USD',
    "sol": 'SOL1-USD',
    "ada": 'ADA-USD',
    "dot": 'DOT1-USD',
    "doge": 'DOGE-USD',
    "shib": 'SHIB-USD',
    "ltc": 'LTC-USD',
    "matic": 'MATIC-USD',
    "mana": 'MANA-USD',
}


def calc_perc_of_transactions(list_of_dicts):
    total_txs = calc_total_transactions(list_of_dicts)
    for item in list_of_dicts:
        txs_len = len(item['transactions'])
        try:
            item['perc_of_total_trans'] = (txs_len / total_txs) * 100
        except ZeroDivisionError:
            item['perc_of_total_trans'] = 0
    return total_txs, list_of_dicts


def create_pass_dict(name):
    start = dt.datetime(2020, 1, 1)
    end = dt.datetime.now()
    data = pdr.DataReader(name, 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))

    data = data.reset_index(level=[0])
    date_range = [item.strftime('%d %b %Y') for item in data['Date']]
    open_price = [int(round(item, 2)) for item in data['Open'].to_list()]
    close = [int(round(item, 2)) for item in data['Close'].to_list()]
    volume = [int(round(item, 2)) for item in data['Volume'].to_list()]
    diff = [int(round(cl - op, 2)) for op, cl in list(zip(open_price, close))]

    return {
        "name": name,
        "open": open_price,
        "close": close,
        "volume": volume,
        "diff": diff,
        "date_range": date_range
    }


def create_tab_info(name):
    tab_data = {
        "company_columns": {},
        "current_stock_columns": {},
        "historical_stock_columns": {},
        "financials_columns": {},
        "dividend_split_columns": {},
        "holders_columns": {},
        "logo": {}
    }
    company_columns = [
        'sector',
        'fullTimeEmployees',
        'longBusinessSummary',
        'website',
        'industry',
        'currency',
        'exchangeTimezoneName'
    ]
    current_stock_columns = [
        'currentPrice',
        'previousClose'
        'open',
        'dayLow',
        'dayHigh',
        'volume',
        'floatShares',
        'sharesOutstanding',
        'sharesShort',
        'shortRatio'
    ]
    historical_stock_columns = [
        'fiftyDayAverage',
        'twoHundredDayAverage',
        'fiftyTwoWeekHigh',
        'fiftyTwoWeekLow',
        'averageVolume10days',
        'impliedSharesOutstanding'
    ]
    financials_columns = [
        'marketCap',
        'totalCash',
        'totalDebt',
        'totalCashPerShare',
        'totalRevenue',
        'revenuePerShare',
        'grossProfits',
        'forwardPE',
        'profitMargins',
        'revenueGrowth',
        'operatingMargins',
        'freeCashflow',
        'debtToEquity'
    ]
    dividend_split_columns = [
        'lastDividendValue',
        'lastSplitFactor'
    ]
    holders_columns = [
        'heldPercentInstitutions',
        'heldPercentInsiders'
    ]
    logo_columns = ['logo_url']

    stonk = yf.Ticker(name)

    for key, value in stonk.info.items():
        if key in company_columns:
            tab_data["company_columns"][key] = value
        if key in current_stock_columns:
            tab_data["current_stock_columns"][key] = value
        if key in historical_stock_columns:
            tab_data["historical_stock_columns"][key] = value
        if key in financials_columns:
            tab_data["financials_columns"][key] = value
        if key in dividend_split_columns:
            tab_data["dividend_split_columns"][key] = value
        if key in holders_columns:
            tab_data["holders_columns"][key] = value
        if key in logo_columns:
            tab_data["logo"][key] = value
    return tab_data


def calc_total_transactions(list_of_dicts):
    total_txs = 0
    for item in list_of_dicts:
        txs_len = len(item['transactions'])
        total_txs += txs_len
    return total_txs