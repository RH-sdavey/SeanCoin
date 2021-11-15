"""A stateful event scanner for Ethereum-based blockchains using Web3.py.

With the stateful mechanism, you can do one batch scan or incremental scans,
where events are added wherever the scanner left off.
"""

import datetime
import time
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Callable, List, Iterable

from web3 import Web3
from web3.contract import Contract
from web3.datastructures import AttributeDict
from web3.exceptions import BlockNotFound
from web3._utils.filters import construct_event_filter_params
from web3._utils.events import get_event_data
from eth_abi.codec import ABICodec

logger = logging.getLogger(__name__)


class EventScannerState(ABC):
    """Application state that remembers what blocks we have scanned in the case of crash."""

    @abstractmethod
    def get_last_scanned_block(self) -> int:
        """Number of the last block we have scanned on the previous cycle.
        :return: 0 if no blocks scanned yet
        """

    @abstractmethod
    def start_chunk(self, block_number: int, chunk_size: int):
        """Scanner is about to ask data of multiple blocks over JSON-RPC. Start a database session if needed."""

    @abstractmethod
    def end_chunk(self, block_number: int):
        """Scanner finished a number of blocks. Persistent any data in your state now."""

    @abstractmethod
    def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> object:
        """Process incoming events. This function takes raw events from Web3, transforms them to your application
         internal format, then saves them in a database or some other state.
        :param block_when: When this block was mined
        :param event: Symbolic dictionary of the event data
        :return: Internal state structure that is the result of event transformation.
        """

    @abstractmethod
    def delete_data(self, since_block: int) -> int:
        """Delete any data since this block was scanned.Purges any potential minor reorg data."""


class EventScanner:
    """Scan blockchain for events and try not to abuse JSON-RPC API too much.
    Can be used for real-time scans, as it detects minor chain reorganisation and rescans.
    Unlike the easy web3.contract.Contract, this scanner can scan events from multiple contracts at once.
    """
    def __init__(self, web3: Web3, contract: Contract, state: EventScannerState, events: List, filters: {},
                 max_chunk_scan_size: int = 10000, max_request_retries: int = 30, request_retry_seconds: float = 3.0):
        """
        :param contract: Contract
        :param events: List of web3 Event we scan
        :param filters: Filters passed to getLogs
        :param max_chunk_scan_size: JSON-RPC API limit in the number of blocks we query.
        :param max_request_retries: How many times we try to reattempt a failed JSON-RPC call
        :param request_retry_seconds: Delay between failed requests to let JSON-RPC server to recover
        """
        self.NUM_BLOCKS_RESCAN_FOR_FORKS = None
        self.token_address = None
        self.logger = logger
        self.contract = contract
        self.web3 = web3
        self.state = state
        self.events = events
        self.filters = filters

        self.min_scan_chunk_size = 10  # 12 s/block = 120 seconds period
        self.max_scan_chunk_size = max_chunk_scan_size
        self.max_request_retries = max_request_retries
        self.request_retry_seconds = request_retry_seconds

        # Factor how fast we increase the chunk size if results are found
        # # (slow down scan after starting to get hits)
        self.chunk_size_decrease = 0.5
        # Factor how was we increase chunk size if no results found
        self.chunk_size_increase = 2.0

    @property
    def address(self):
        return self.token_address

    def get_block_timestamp(self, block_num) -> datetime.datetime or None:
        """Get Ethereum block timestamp"""
        try:
            block_info = self.web3.eth.getBlock(block_num)
        except BlockNotFound:
            return None
        last_time = block_info["timestamp"]
        return datetime.datetime.utcfromtimestamp(last_time)

    def get_suggested_scan_start_block(self):
        """Get where we should start to scan for new token events. If there are no prior scans, start from block 1.
        Otherwise, start from the last end block minus ten blocks. We rescan the last ten scanned blocks in the case
        there were forks to avoid miscounting due to minor single block works (happens once in a hour in Ethereum).
        """
        end_block = self.get_last_scanned_block()
        return max(1, end_block - self.NUM_BLOCKS_RESCAN_FOR_FORKS) if end_block else 1

    def get_suggested_scan_end_block(self):
        """Get the last mined block on Ethereum chain we are following."""
        # Do not scan all the way to the final block, as this block might not be mined yet
        return self.web3.eth.blockNumber - 1

    def get_last_scanned_block(self) -> int:
        return self.state.get_last_scanned_block()

    def delete_potentially_forked_block_data(self, after_block: int):
        """Purge old data in the case of blockchain reorganisation."""
        self.state.delete_data(after_block)

    def scan_chunk(self, start_block, end_block) -> Tuple[int, datetime.datetime, list]:
        """Read and process events between to block numbers.
        Dynamically decrease the size of the chunk if the case JSON-RPC server pukes out.
        :return: tuple(actual end block number, when this block was mined, processed events)
        """

        block_timestamps = {}
        get_block_timestamp = self.get_block_timestamp

        # Cache block timestamps to reduce some RPC overhead
        # Real solution might include smarter models around block
        def get_block_when(block_num):
            if block_num not in block_timestamps:
                block_timestamps[block_num] = get_block_timestamp(block_num)
            return block_timestamps[block_num]

        all_processed = []
        for event_type in self.events:
            # Callable that takes care of the underlying web3 call
            def _fetch_events(_start_block, _end_block):
                return _fetch_events_for_all_contracts(self.web3,
                                                       event_type,
                                                       self.filters,
                                                       from_block=_start_block,
                                                       to_block=_end_block)

            end_block, events = _retry_web3_call(
                _fetch_events,
                start_block=start_block,
                end_block=end_block,
                retries=self.max_request_retries,
                delay=self.request_retry_seconds)

            for evt in events:
                idx = evt["logIndex"]  # Integer of the log index position in the block, null when its pending
                assert idx is not None, "Somehow tried to scan a pending block"
                block_number = evt["blockNumber"]

                # Get UTC time when this event happened (block mined timestamp)
                block_when = get_block_when(block_number)
                logger.debug("Processing event %s, block:%d count:%d", evt["event"], evt["blockNumber"])
                processed = self.state.process_event(block_when, evt)
                all_processed.append(processed)
        end_block_timestamp = get_block_when(end_block)
        return end_block, end_block_timestamp, all_processed

    def estimate_next_chunk_size(self, current_chuck_size: int, event_found_count: int):
        """Try to figure out optimal chunk size. Our scanner might need to scan the whole blockchain for all events
        Currently Ethereum JSON-API does not have an API to tell when a first event occured in a blockchain
        and our heuristics try to accelerate block fetching (chunk size) until we see the first event.
        """

        if event_found_count > 0:
            current_chuck_size = self.min_scan_chunk_size
        else:
            current_chuck_size *= self.chunk_size_increase
        current_chuck_size = max(self.min_scan_chunk_size, current_chuck_size)
        current_chuck_size = min(self.max_scan_chunk_size, current_chuck_size)
        return int(current_chuck_size)

    def scan(self, start_block, end_block, start_chunk_size=20, prog_callback=Optional[Callable]) -> Tuple[list, int]:
        """Perform a token balances scan.
        Assumes all balances in the database are valid before start_block (no forks sneaked in).
        :param start_block: The first block included in the scan
        :param end_block: The last block included in the scan
        :param start_chunk_size: How many blocks we try to fetch over JSON-RPC on the first attempt
        :param prog_callback: If this is an UI application, update the progress of the scan
        :return: [All processed events, number of chunks used]
        """
        assert start_block <= end_block
        current_block = start_block
        chunk_size = start_chunk_size
        last_scan_duration = last_logs_found = 0
        total_chunks_scanned = 0

        all_processed = []
        while current_block <= end_block:
            self.state.start_chunk(current_block, chunk_size)
            estimated_end_block = current_block + chunk_size
            logger.debug(
                f"Scanning token transfers for blocks: {current_block} - {estimated_end_block}, chunk size {chunk_size}"
                f", last chunk scan took {last_scan_duration}, last logs found {last_logs_found}")

            start = time.time()
            actual_end_block, end_block_timestamp, new_entries = self.scan_chunk(current_block, estimated_end_block)
            current_end = actual_end_block
            last_scan_duration = time.time() - start
            all_processed += new_entries

            if prog_callback:
                prog_callback(start_block, end_block, current_block, end_block_timestamp, chunk_size, len(new_entries))

            chunk_size = self.estimate_next_chunk_size(chunk_size, len(new_entries))
            current_block = current_end + 1
            total_chunks_scanned += 1
            self.state.end_chunk(current_end)
        return all_processed, total_chunks_scanned


def _retry_web3_call(func, start_block, end_block, retries, delay) -> Tuple[int, list]:
    """A custom retry loop to throttle down block range. If our JSON-RPC server cannot serve all incoming `eth_getLogs`
     in a single request, we retry and throttle down block range for every retry.
    :param func: A callable that triggers Ethereum JSON-RPC, as func(start_block, end_block)
    :param start_block: The initial start block of the block range
    :param end_block: The initial start block of the block range
    :param retries: How many times we retry
    :param delay: Time to sleep between retries
    """
    for i in range(retries):
        try:
            return end_block, func(start_block, end_block)
        except Exception as e:
            # Assume this is HTTPConnectionPool(host='localhost', port=8545): Read timed out. (read timeout=10)
            # from Go Ethereum. This translates to the error "context was cancelled" on the server side:
            # https://github.com/ethereum/go-ethereum/issues/20426
            if i < retries - 1:
                logger.warning(f"Retrying events for block range {start_block} - {end_block} ({end_block-start_block})"
                               f" failed with {e}, retrying in {delay} seconds")

                end_block = start_block + ((end_block - start_block) // 2)
                time.sleep(delay)
                continue
            else:
                logger.warning("Out of retries")
                raise


def _fetch_events_for_all_contracts(web3, event, argument_filters: dict, from_block: int, to_block: int) -> Iterable:
    """Get events using eth_getLogs API. This method is detached from any contract instance.
    It can be safely called against nodes which do not provide `eth_newFilter` API.
    """
    if from_block is None:
        raise TypeError("Missing mandatory keyword argument to getLogs: fromBlock")
    abi = event._get_event_abi()

    # More information here https://eth-abi.readthedocs.io/en/latest/index.html
    codec: ABICodec = web3.codec

    # More information here:
    # https://github.com/ethereum/web3.py/blob/e176ce0793dafdd0573acc8d4b76425b6eb604ca/web3/_utils/filters.py#L71
    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        codec,
        address=argument_filters.get("address"),
        argument_filters=argument_filters,
        fromBlock=from_block,
        toBlock=to_block
    )

    logger.debug(f"Querying eth_getLogs with the following parameters: {event_filter_params}")
    logs = web3.eth.get_logs(event_filter_params)
    all_events = []
    for log in logs:
        # More information how processLog works here
        # https://github.com/ethereum/web3.py/blob/fbaf1ad11b0c7fac09ba34baff2c256cffe0a148/web3/_utils/events.py#L200
        evt = get_event_data(codec, abi, log)
        all_events.append(evt)
    return all_events


if __name__ == "__main__":
    import sys
    import json
    from web3.providers.rpc import HTTPProvider

    # https://pypi.org/project/tqdm/
    from tqdm import tqdm

    # https://etherscan.io/token/0x9b6443b0fb9c241a7fdac375595cea13e6b7807a
    RCC_ADDRESS = "0xbbbbca6a901c926f240b89eacb641d8aec7aeafd"

    ABI = """[
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": true,
                    "name": "from",
                    "type": "address"
                },
                {
                    "indexed": true,
                    "name": "to",
                    "type": "address"
                },
                {
                    "indexed": false,
                    "name": "value",
                    "type": "uint256"
                }
            ],
            "name": "Transfer",
            "type": "event"
        }
    ]
    """

    class JSONifiedState(EventScannerState):
        """Store the state of scanned blocks and all events."""

        def __init__(self):
            self.state = None
            self.fname = "test-state.json"
            self.last_save = 0

        def reset(self):
            """Create initial state of nothing scanned."""
            self.state = {
                "last_scanned_block": 0,
                "blocks": {},
            }

        def restore(self):
            """Restore the last scan state from a file."""
            try:
                self.state = json.load(open(self.fname, "rt"))
                print(f"Restored the state, previously {self.state['last_scanned_block']} blocks have been scanned")
            except (IOError, json.decoder.JSONDecodeError):
                print("State starting from scratch")
                self.reset()

        def save(self):
            """Save everything we have scanned so far in a file."""
            with open(self.fname, "wt") as f:
                json.dump(self.state, f)
            self.last_save = time.time()

        def get_last_scanned_block(self):
            """The number of the last block we have stored."""
            return self.state["last_scanned_block"]

        def delete_data(self, since_block):
            """Remove potentially reorganised blocks from the scan data."""
            for block_num in range(since_block, self.get_last_scanned_block()):
                if block_num in self.state["blocks"]:
                    del self.state["blocks"][block_num]

        def start_chunk(self, block_number, chunk_size):
            pass

        def end_chunk(self, block_number):
            """Save at the end of each block, so we can resume in the case of a crash or CTRL+C"""
            # Next time the scanner is started we will resume from this block
            self.state["last_scanned_block"] = block_number

            # Save the database file for every minute
            if time.time() - self.last_save > 60:
                self.save()

        def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> str:
            """Record a ERC-20 transfer in our database."""

            log_index = event.logIndex  # Log index within the block
            txhash = event.transactionHash.hex()  # Transaction hash
            block_number = event.blockNumber

            # Convert ERC-20 Transfer event to our files internal format
            args = event["args"]
            transfer = {
                "from": args["from"],
                "to": args.to,
                "value": args.value,
                "timestamp": block_when.isoformat(),
            }

            if block_number not in self.state["blocks"]:
                self.state["blocks"][block_number] = {}

            block = self.state["blocks"][block_number]
            if txhash not in block:
                self.state["blocks"][block_number][txhash] = {}

            self.state["blocks"][block_number][txhash][log_index] = transfer
            return f"{block_number}-{txhash}-{log_index}"

    def run():
        if len(sys.argv) < 2:
            print("Usage: eventscanner.py http://your-node-url")
            sys.exit(1)
        api_url = sys.argv[1]

        logging.basicConfig(level=logging.INFO)
        provider = HTTPProvider(api_url)
        provider.middlewares.clear()
        web3 = Web3(provider)
        abi = json.loads(ABI)
        ERC20 = web3.eth.contract(abi=abi)

        # Restore/create our persistent state
        state = JSONifiedState()
        state.restore()

        scanner = EventScanner(
            web3=web3,
            contract=ERC20,
            state=state,
            events=[ERC20.events.Transfer],
            filters={"address": Web3.toChecksumAddress(RCC_ADDRESS)},
            max_chunk_scan_size=10000
        )

        # Assume we might have scanned the blocks all the way to the last Ethereum block
        # that mined a few seconds before the previous scan run ended.
        chain_reorg_safety_blocks = 10
        scanner.delete_potentially_forked_block_data(state.get_last_scanned_block() - chain_reorg_safety_blocks)

        # Scan from [last block scanned] - [latest ethereum block]
        start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, 0)
        end_block = scanner.get_suggested_scan_end_block()
        blocks_to_scan = end_block - start_block

        print(f"Scanning events from blocks {start_block} - {end_block}")

        start = time.time()
        with tqdm(total=blocks_to_scan) as progress_bar:
            def _update_progress(start, end, current, current_block_timestamp, chunk_size, events_count):
                if current_block_timestamp:
                    formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
                else:
                    formatted_time = "no block time available"
                progress_bar.set_description(f"Current block: {current} ({formatted_time}), blocks in a scan batch:"
                                             f" {chunk_size}, events processed in a batch {events_count}")
                progress_bar.update(chunk_size)

            # Run the scan
            result, total_chunks_scanned = scanner.scan(start_block, end_block, prog_callback=_update_progress)

        state.save()
        duration = time.time() - start
        print(f"Scanned total {len(result)} Transfer events, in {duration} seconds,"
              f" total {total_chunks_scanned} chunk scans performed")
    run()
