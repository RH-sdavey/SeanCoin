from flask import Flask, render_template

from werkzeug.routing import BuildError
from web3.exceptions import BlockNotFound

from backend.blockchain import BlockChain, Account
from backend.backend import (
    normalize_balance,
    calc_perc_of_transactions,
    calc_val_of_all_transactions_in_blocks,
    price_chart_info,
    stonk_table_info,
    all_crypto as ac
)


bc = BlockChain()
seanCoin = Flask(__name__)


@seanCoin.context_processor
def all_crypto():
    return dict(all_crypto=ac)


@seanCoin.route('/')
@seanCoin.route('/index.html')
@seanCoin.route('/index.html/<int:num_blocks>')
def index(num_blocks=5):
    last_n = bc.block_factory().get_last_n_blocks(num_blocks)
    all_n_blocks = [dict(item) for item in last_n]
    total_transactions, all_n_blocks = calc_perc_of_transactions(all_n_blocks)
    return render_template(
        'latest-blocks.html',
        data=all_n_blocks,
        total_transactions=total_transactions,
        total_val=calc_val_of_all_transactions_in_blocks(all_n_blocks),
        enumerate=enumerate
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
            'block.html',
            block_obj=block,
            txs=txs,
            normalize_balance=normalize_balance,
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
                value=normalize_balance(transaction['value'])
            )


@seanCoin.route('/account/<string:account>')
def account(account):
    account_obj = Account(bc, account)
    return render_template(
        'account.html',
        account=account_obj.account,
        balance=normalize_balance(account_obj.balance)
    )


@seanCoin.route("/coin-charts/<coin>")
def coin_charts(coin):
    pass_dict = price_chart_info(coin, crypto=True)
    return render_template(
        "crypto_base.html",
        data=pass_dict
    )


@seanCoin.route("/stonk-charts/<stonk>")
def stonk_charts(stonk):
    pass_dict = price_chart_info(stonk)
    tab_data, finance_data = stonk_table_info(stonk)
    return render_template(
        "stonk_charts.html",
        data=pass_dict,
        tab_data=tab_data,
        finance_data=finance_data
    )
