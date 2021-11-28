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
        print(f"total_transactions: {total_txs}")
        print(f"txs_len: {txs_len}")
        print(f"perc_calc: {(txs_len / total_txs) * 100}")
        print(f"perc_item: {item['perc_of_total_trans']}")
    return total_txs, list_of_dicts


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
            return render_template('transactions.html',
                                   txs=transaction,
                                   value=Account.normalize_balance(transaction['value']))


@seanCoin.route('/account/<string:account>')
def account(account):
    account_obj = Account(bc, account)
    balance = account_obj.get_balance()
    return render_template('account.html',
                           account=account_obj.account,
                           balance=balance)


@seanCoin.route("/price-charts")
def price_charts():
    return render_template("price_charts.html")
