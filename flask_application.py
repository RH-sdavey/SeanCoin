import datetime as dt
from decimal import Decimal

import pandas
import pandas_datareader as pdr
from flask import Flask, render_template
from werkzeug.routing import BuildError
from web3.exceptions import BlockNotFound
from blockchain import BlockChain, Account

bc = BlockChain()
seanCoin = Flask(__name__)


def calc_total_transactions(list_of_dicts):
    total_txs = 0
    for item in list_of_dicts:
        txs_len = len(item['transactions'])
        total_txs += txs_len
    return total_txs


def calc_perc_of_transactions(list_of_dicts):
    total_txs = calc_total_transactions(list_of_dicts)
    for item in list_of_dicts:
        txs_len = len(item['transactions'])
        try:
            item['perc_of_total_trans'] = (txs_len / total_txs) * 100
        except ZeroDivisionError:
            item['perc_of_total_trans'] = 0
    return total_txs, list_of_dicts

# def calculate_open_close_diff(crypto):
#     for


@seanCoin.route('/')
@seanCoin.route('/index.html')
def index():
    num_blocks = 5
    last_n = bc.block_factory().get_last_n_blocks(num_blocks)
    list_of_dicts = [dict(item) for item in last_n]
    total_transactions, list_of_dicts = calc_perc_of_transactions(list_of_dicts)
    return render_template('latest-blocks.html',
                           data=list_of_dicts,
                           total_transactions=total_transactions)


@seanCoin.route('/index.html/<int:num_blocks>')
def index_val(num_blocks=20):
    last_n = bc.block_factory().get_last_n_blocks(num_blocks)
    list_of_dicts = [dict(item) for item in last_n]
    total_transactions, list_of_dicts = calc_perc_of_transactions(list_of_dicts)
    return render_template('latest-blocks.html',
                           data=list_of_dicts,
                           total_transactions=total_transactions)


@seanCoin.route('/block/<int:page>')
def block_page(page):
    latest_block = bc.block_factory().get_block()
    try:
        block = bc.block_factory(page).get_block()
    except BlockNotFound:
        return render_template('ohno.html')
    next_disabled = True if latest_block.block['number'] < block.block['number'] else False
    txs = block['transactions']
    try:
        return render_template(
            'block.html',
            block_obj=block,
            txs=txs,
            normalize_balance=Account.normalize_balance,
            block_hash=block['hash'],
            block_number=block['number'],
            next_disabled=next_disabled,
            trans_len=len(txs)
        )
    except BuildError:
        return render_template('ohno.html')


@seanCoin.route('/block/<int:page>/transactions/<int:tx>')
def txs_page(page, tx):
    block = bc.block_factory(page).get_block()
    for transaction in block['transactions']:
        if transaction['transactionIndex'] == tx:
            return render_template(
                'transactions.html',
                txs=transaction,
                value=Account.normalize_balance(transaction['value'])
            )


@seanCoin.route('/account/<string:account>')
def account(acc_id):
    account_obj = Account(bc, acc_id)
    balance = account_obj.get_balance()
    return render_template(
        'account.html',
        account=account_obj.account,
        balance=balance
    )


@seanCoin.route("/price-charts")
def price_charts():
    start = dt.datetime(2020, 1, 1)
    end = dt.datetime.now()
    date_range = pandas.date_range(start, end - dt.timedelta(days=1), freq='d').strftime("%d %b %Y").tolist()

    eth = pdr.DataReader('ETH-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    btc = pdr.DataReader('BTC-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    lrc = pdr.DataReader('LRC-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    bnb= pdr.DataReader('BNB-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    usdt = pdr.DataReader('USDT-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    sol = pdr.DataReader('SOL1-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    ada = pdr.DataReader('ADA-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    dot = pdr.DataReader('DOT1-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    doge = pdr.DataReader('DOGE-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    shib = pdr.DataReader('SHIB-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    ltc = pdr.DataReader('LTC-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    matic = pdr.DataReader('MATIC-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))
    mana = pdr.DataReader('MANA-USD', 'yahoo', start.strftime("%d %b %Y"), end.strftime("%d %b %Y"))

    open_prices = {
        "eth": eth['Open'].to_list(),
        "btc": btc['Open'].to_list(),
        "lrc": lrc['Open'].to_list(),
        "bnb": bnb['Open'].to_list(),
        "usdt": usdt['Open'].to_list(),
        "sol": sol['Open'].to_list(),
        "ada": ada['Open'].to_list(),
        "dot": dot['Open'].to_list(),
        "doge": doge['Open'].to_list(),
        "shib": shib['Open'].to_list(),
        "ltc": ltc['Open'].to_list(),
        "matic": matic['Open'].to_list(),
        "mana": mana['Open'].to_list()
    }

    closing_prices = {
        "eth": eth['Close'].to_list(),
        "btc": btc['Close'].to_list(),
        "lrc": lrc['Close'].to_list(),
        "bnb": bnb['Close'].to_list(),
        "usdt": usdt['Close'].to_list(),
        "sol": sol['Close'].to_list(),
        "ada": ada['Close'].to_list(),
        "dot": dot['Close'].to_list(),
        "doge": doge['Close'].to_list(),
        "shib": shib['Close'].to_list(),
        "ltc": ltc['Close'].to_list(),
        "matic": matic['Close'].to_list(),
        "mana": mana['Close'].to_list()
    }

    volume = {
        "eth": eth['Volume'].to_list(),
        "btc": btc['Volume'].to_list(),
        "lrc": lrc['Volume'].to_list(),
        "bnb": bnb['Volume'].to_list(),
        "usdt": usdt['Volume'].to_list(),
        "sol": sol['Volume'].to_list(),
        "ada": ada['Volume'].to_list(),
        "dot": dot['Volume'].to_list(),
        "doge": doge['Volume'].to_list(),
        "shib": shib['Volume'].to_list(),
        "ltc": ltc['Volume'].to_list(),
        "matic": matic['Volume'].to_list(),
        "mana": mana['Volume'].to_list()
    }

    open_close_diff = {
        "eth": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['eth'], closing_prices['eth']))],
        "btc": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['btc'], closing_prices['btc']))],
        "lrc": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['lrc'], closing_prices['lrc']))],
        "bnb": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['bnb'], closing_prices['bnb']))],
        "usdt": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['usdt'], closing_prices['usdt']))],
        "sol": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['sol'], closing_prices['sol']))],
        "ada": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['ada'], closing_prices['ada']))],
        "dot": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['dot'], closing_prices['dot']))],
        "doge": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['doge'], closing_prices['doge']))],
        "shib": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['shib'], closing_prices['shib']))],
        "ltc": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['ltc'], closing_prices['ltc']))],
        "matic": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['matic'], closing_prices['matic']))],
        "mana": [str(Decimal(cl) - Decimal(op)) for op, cl in list(zip(open_prices['mana'], closing_prices['mana']))],
    }

    return render_template("price_charts.html",
                           date_range=date_range,
                           closing_prices=closing_prices,
                           volume=volume,
                           open_close_diff=open_close_diff)
