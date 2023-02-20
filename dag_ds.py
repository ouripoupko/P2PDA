import hashlib
from datetime import datetime
import requests
from threading import Lock

class DagDataStructure:
    def __init__(self):
        self.lock = Lock()
        self.transactions = {}
        self.sources = []

    def __iter__(self):
        return iter(self.transactions.values())

    def __getitem__(self, item):
        return self.transactions[item]

    def store_transaction(self, transaction):
        with self.lock:
            for functional in transaction['content']['functionals']:
                if functional not in self.transactions:
                    reply = requests.get(f'{transaction["content"]["owner"]}/dag',
                                         params={'hash_code': functional})
                    self.store_transaction(reply.json())
            hash_code = transaction['hash_code']
            self.transactions[hash_code] = transaction
            if hash_code not in self.sources:
                self.sources.append(hash_code)

    def create_transaction(self, content):
        with self.lock:
            content['timestamp'] = datetime.now().strftime('%Y%m%d%H%M%S%f')
            hash_code = hashlib.sha256(str(content).encode('utf-8')).hexdigest()
            transaction = {'content': content,
                           'hash_code': hash_code,
                           'ordinals': self.sources}
            self.transactions[hash_code] = transaction
            self.sources = [hash_code]
        return self.transactions[hash_code]
