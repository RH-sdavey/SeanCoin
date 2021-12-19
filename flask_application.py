import datetime

import pandas as pd
from flask import Flask, render_template

from werkzeug.routing import BuildError
from web3.exceptions import BlockNotFound

from backend import lib
from backend.media_scraper import StonkMedia
from backend.stonk import Stonk
from backend.blockchain import BlockChain, Account
from backend.backend import (
    normalize_balance,
    calc_perc_of_transactions,
    calc_val_of_all_transactions_in_blocks,
)

bc = BlockChain()
seanCoin = Flask(__name__)


@seanCoin.context_processor
def all_crypto():
    return dict(all_crypto=lib.all_crypto)


@seanCoin.route('/')
@seanCoin.route('/index.html')
@seanCoin.route('/index.html/<int:num_blocks>')
def index(num_blocks=5):
    last_n = bc.block_factory().get_last_n_blocks(num_blocks)
    all_n_blocks = [dict(item) for item in last_n]
    total_transactions, all_n_blocks = calc_perc_of_transactions(all_n_blocks)
    return render_template(
        'block/latest-blocks.html',
        data=all_n_blocks,
        total_transactions=total_transactions,
        total_val=calc_val_of_all_transactions_in_blocks(all_n_blocks),
        enumerate=enumerate,
        fromtimestamp=datetime.datetime.fromtimestamp,
        strftime=datetime.datetime.strftime
    )


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
            'block/block.html',
            block_obj=block,
            txs=txs,
            normalize_balance=normalize_balance,
            block_hash=block['hash'],
            block_number=block['number'],
            next_disabled=next_disabled,
            trans_len=len(txs),
            fromtimestamp=datetime.datetime.fromtimestamp,
            strftime=datetime.datetime.strftime
        )
    except BuildError:
        return render_template('ohno.html')


@seanCoin.route('/block/<int:page>/transactions/<int:tx>')
def txs_page(page, tx):
    block = bc.block_factory(page).get_block()
    for transaction in block['transactions']:
        if transaction['transactionIndex'] == tx:
            return render_template(
                'block/transactions.html',
                txs=transaction,
                value=normalize_balance(transaction['value'])
            )


@seanCoin.route('/account/<string:account>')
def account(account):
    account_obj = Account(bc, account)
    return render_template(
        'block/account.html',
        account=account_obj.account,
        balance=normalize_balance(account_obj.balance)
    )


@seanCoin.route("/coin-charts/<coin>")
def coin_charts(coin):
    # pass_dict = pandas_price_data(coin, crypto=True)
    return "ok"
    # return render_template(
    #     "crypto/crypto_charts.html",
    #     data=pass_dict
    # )


@seanCoin.route("/stonk-charts/<stonk>")
def stonk_charts(stonk):
    stonk_obj = Stonk(stonk)
    return render_template(
        "stonk/stonk_charts.html",
        stonk_obj=stonk_obj,
        stonk=stonk,
        getattr=getattr
    )


@seanCoin.route("/stonk_info/<stonk>")
def stonk_info(stonk):
    stonk_obj = Stonk(stonk)
    if not lib.stonk_object:
        lib.stonk_object = stonk_obj
    elif not lib.stonk_object == stonk_obj:
        lib.stonk_object = stonk_obj

    s_media = StonkMedia(stonk)
    return render_template(
        "stonk/stonk_info.html",
        stonk=stonk,
        stonk_obj=stonk_obj,
        stonk_media=s_media,
    )


if __name__ == '__main__':
    seanCoin.run(debug=False)
