import datetime as dt

import pandas_datareader as pdr
import yfinance_ez as yf

from stonk import Stonk


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


def pandas_price_data(name, crypto=False) -> dict:
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


def yfinance_data(name):
    yf_stonk = yf.Ticker(name)
    stonk = Stonk(name, **{**yf_stonk.info, **yf_stonk.financials_data})
    return stonk


def div_and_split(stonk):
    yf_stonk = yf.Ticker(stonk)
    hist = yf_stonk.get_history(period=yf.TimePeriods.FiveYears)
    return yf_stonk.dividends.to_dict(), yf_stonk.splits.to_dict()

