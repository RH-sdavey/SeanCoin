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
        last_n = []
        latest_b_num = self.blockchain.web3.eth.get_block_number()
        for i in range(n):
            block = self.blockchain.web3.eth.getBlock(latest_b_num - i, full_transactions=full_transactions)
            json_block = json.loads(json.dumps(block, cls=HexJsonEncoder))
            last_n.append(json_block)
        return last_n


class Account:
    def __init__(self, blockchain: BlockChain, account=None):
        self.blockchain = blockchain
        self.account = account
        self.balance = self.get_balance()

    @staticmethod
    def normalize_balance(balance: str) -> str:
        """

        :param balance:
        :return:
        """
        if balance == "0":
            return balance
        if len(balance) < 18:
            len_diff = 18 - len(balance)
            balance = balance.zfill(18 + len_diff + 1)
        return f"{balance[:-18]}.{balance[-18:]}"

    def get_balance(self) -> str:
        """
        TODO
        :param account:
        :return:
        """
        balance = str(self.blockchain.web3.eth.get_balance(self.account))
        return self.normalize_balance(balance)























