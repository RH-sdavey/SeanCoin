from flask import Flask, render_template

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
    block = bc.block_factory(page).get_block()
    txs = block['transactions']
    return render_template('block.html',
                           block_obj=block,
                           txs=txs,
                           block_hash=block['hash'],
                           block_number=block['number'])


@app.route('/block/<int:page>/transactions/<int:tx>')
def txs_page(page, tx):
    block = bc.block_factory(page).get_block()
    for transaction in block['transactions']:
        if transaction['transactionIndex'] == tx:
            return render_template('transactions.html', txs=transaction)


@app.route('/account/<string:account>')
def account(account):
    account = Account(bc, account)
    balance = account.get_balance()
    return render_template('account.html',
                           account=account.account,
                           balance=balance)
