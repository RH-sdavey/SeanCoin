import yfinance_ez as yf



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





