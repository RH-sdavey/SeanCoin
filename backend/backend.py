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


def normalize_balance(balance: str) -> str:
    """Eth balances from web3 lib are in format 130328902193012.00000000 (for eg)
    where the actual balance would be 1.303....
    This method normalizes the balance by attempting to shift the . 18 places to the left
    (FIXME: must be a better way?)

    :param str balance: balance amount to normalize
    :return: normalized balance
    :rtype: str
    """
    balance = str(balance)
    if balance == "0":
        return balance
    if len(balance) < 18:
        len_diff = 18 - len(balance)
        balance = balance.zfill(18 + len_diff + 1)
    return f"{balance[:-18]}.{balance[-18:]}".rstrip("0")


def calc_val_of_all_transactions_in_blocks(list_of_blocks):
    total_per_block = [sum(val) for val in [[tx['value'] for tx in block['transactions']] for block in list_of_blocks]]
    total_val = normalize_balance(sum(total_per_block))
    return total_val, [normalize_balance(i) for i in total_per_block]


def calc_perc_of_transactions(list_of_blocks):
    total_txs = sum([len(block['transactions']) for block in list_of_blocks])
    for item in list_of_blocks:
        txs_len = len(item['transactions'])
        try:
            item['perc_of_total_trans'] = (txs_len / total_txs) * 100
        except ZeroDivisionError:
            item['perc_of_total_trans'] = 0
    return total_txs, list_of_blocks


def price_chart_info(name, crypto=False) -> dict:
    dec_place = 8 if crypto else 2
    start = dt.datetime(2019, 1, 1)
    end = dt.datetime.now()
    data = pdr.DataReader(name, 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))

    data = data.reset_index(level=[0])
    date_range = [item.strftime('%d %b %Y') for item in data['Date']]

    open_price = [round(item, dec_place) for item in data['Open'].to_list()]
    close = [round(item, dec_place) for item in data['Close'].to_list()]
    volume = [round(item, dec_place) for item in data['Volume'].to_list()]
    diff = [round(cl - op, dec_place) for op, cl in list(zip(open_price, close))]

    return {
        "name": name,
        "open": open_price,
        "close": close,
        "volume": volume,
        "diff": diff,
        "date_range": date_range
    }


def stonk_table_info(name):
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
    finance_data = parse_financial_data(stonk)

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
    return tab_data, finance_data


def parse_financial_data(stonk):
    return {
        "q_dates": [item['date'] for item in stonk.financials_data['earnings']['financialsChart']['quarterly']],
        "q_rev": [item['revenue'] for item in stonk.financials_data['earnings']['financialsChart']['quarterly']],
        "q_earn": [item['earnings'] for item in stonk.financials_data['earnings']['financialsChart']['quarterly']],
        "y_dates": [item['date'] for item in stonk.financials_data['earnings']['financialsChart']['yearly']],
        "y_rev": [item['revenue'] for item in stonk.financials_data['earnings']['financialsChart']['yearly']],
        "y_earn": [item['earnings'] for item in stonk.financials_data['earnings']['financialsChart']['yearly']],
        "q_est_earn": [item['estimate'] for item in stonk.financials_data['earnings']['earningsChart']['quarterly']],
        "q_actual_earn": [item['actual'] for item in stonk.financials_data['earnings']['earningsChart']['quarterly']],
        "q_date_earn": [item['date'] for item in stonk.financials_data['earnings']['earningsChart']['quarterly']],
    }
