import hashlib
from datetime import datetime

class DagDataStructure:
    def __init__(self):
        self.transactions = {}
        self.sources = []

    def __iter__(self):
        return iter(self.transactions.values())

    def store_transaction(self, transaction):
        hash_code = transaction['hash_code']
        self.transactions[hash_code] = transaction
        if hash_code not in self.sources:
            self.sources.append(hash_code)

    def create_transaction(self, content):
        content['timestamp'] = datetime.now().strftime('%Y%m%d%H%M%S%f')
        hash_code = hashlib.sha256(str(content).encode('utf-8')).hexdigest()
        transaction = {'content': content,
                       'hash_code': hash_code,
                       'pointers': self.sources}
        self.transactions[hash_code] = transaction
        self.sources = [hash_code]
        return self.transactions[hash_code]
