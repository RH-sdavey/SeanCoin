import json

from hexbytes import HexBytes

from web3 import Web3
from web3.datastructures import AttributeDict


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        elif isinstance(obj, AttributeDict):
            return dict(obj)
        return super().default(obj)


class BlockChain:

    def __init__(self):
        self.infura_url = "https://mainnet.infura.io/v3/4bb671976f9b4d6caa45bd6556b5c2d3"
        self.web3 = None
        self._established = "False"
        self.connect().return_blockchain()

    def __repr__(self):
        return f"BlockChain({self.infura_url})"

    def connect(self):
        """

        :return:
        """
        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))
        return self

    def established(self):
        """

        :return:
        """
        self._established = self.web3.isConnected()
        if not self._established:
            exit("Connecting to Ethereum Blockchain failed, please check manually")
        return self._established

    def return_blockchain(self):
        """

        :return:
        """
        if self.established():
            return self

    def block_factory(self, block=None):
        """

        :param block:
        :return:
        """
        return Block(self, block)


class Block:
    """Object representing one block instance from the whole BlockChain, defaults to latest block"""

    def __init__(self, blockchain: BlockChain, block=None):
        self.blockchain = blockchain
        self.block_lookup = block if block else "latest"
        self.block = None

    def __getitem__(self, item):
        return self.block[item]

    def get_block(self, full_transactions=True):
        """returns one block instance, defaults to latest block in the blockchain        """

        self.block_lookup = int(self.block_lookup) if self.block_lookup != "latest" else self.block_lookup
        obj = dict(self.blockchain.web3.eth.get_block(block_identifier=self.block_lookup,
                                                      full_transactions=full_transactions))
        # pattern used here --> jsonloads(json.dumps(cls=HexJsonEncoder)) because some of the nested values used
        # in a block dict object are complicated hashes that are not dealt with well by json library.
        # json.dumps(attributeDict) (uses HexJsonEncoder as a metaclass to resolve the hashes) -> str
        # json.loads(str) -> dict
        self.block = json.loads(json.dumps(obj, cls=HexJsonEncoder))
        return self

    def get_last_n_blocks(self, n, full_transactions=True):
        """
        TODO
        :param full_transactions:
        :return:
        """
        last_50 = []
        latest_b_num = self.blockchain.web3.eth.get_block_number()
        for i in range(n):
            block = self.blockchain.web3.eth.getBlock(latest_b_num - i, full_transactions=full_transactions)
            json_block = json.loads(json.dumps(block, cls=HexJsonEncoder))
            last_50.append(json_block)
        return last_50

    def transaction_factory(self, index):
        """

        :return:
        """
        return Transaction(self, index)


class Transaction:
    """Object representing one transaction instance from a Block"""

    def __init__(self, block: Block, txs_index):
        self.block = block
        self.txs_index = txs_index


#         def get_transactions(self):
#             return self.outer_instance['transactions']
#
#         def get_transaction_count(self):
#             return self.outer_instance.blockchain.get_block_transaction_count(self.outer_instance['number'])
#
#         def get_trans_ids_by_block_id(self, block_id):
#             try:
#                 return self.outer_instance.get_block(block_id)['transactions']
#             except (BlockNotFound, ValueError) as e:
#                 raise Exception("Block ID does not exist, or invalid ID format:\n", e)
#
#         def get_trans_by_index(self, index):
#             for transact in self.transactions:
#                 if transact['transactionIndex'] == index:
#                     return transact


bc = BlockChain()
last_40 = bc.block_factory().get_last_n_blocks(5)






















