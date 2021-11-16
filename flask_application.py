from flask import Flask, render_template
from werkzeug.routing import BuildError
from web3.exceptions import BlockNotFound

from blockchain import BlockChain, Account

bc = BlockChain()
app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    last_n = bc.block_factory().get_last_n_blocks(5)
    list_of_dicts = [dict(item) for item in last_n]
    return render_template('latest-blocks.html', display=list_of_dicts,
                           data=list_of_dicts)


@app.route('/index.html/<int:num_blocks>')
def index_val(num_blocks=20):
    last_n = bc.block_factory().get_last_n_blocks(num_blocks)
    list_of_dicts = [dict(item) for item in last_n]
    return render_template('latest-blocks.html', display=list_of_dicts,
                           data=list_of_dicts)


@app.route('/block/<int:page>')
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
            next_disabled=next_disabled
        )
    except BuildError:
        return render_template('ohno.html')


@app.route('/block/<int:page>/transactions/<int:tx>')
def txs_page(page, tx):
    block = bc.block_factory(page).get_block()
    for transaction in block['transactions']:
        if transaction['transactionIndex'] == tx:
            return render_template('transactions.html',
                                   txs=transaction,
                                   value=Account.normalize_balance(transaction['value']))


@app.route('/account/<string:account>')
def account(account):
    account_obj = Account(bc, account)
    balance = account_obj.get_balance()
    return render_template('account.html',
                           account=account_obj.account,
                           balance=balance)
