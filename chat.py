import requests
from dag_utils import reverse_dag, order_dag

class Chat:
    def __init__(self, address):
        self.contacts_messages = {}
        self.groups_messages = {}
        self.address = address
        self.operations = {'MessageContact': self.message_contact,
                           'MessageGroup': self.message_group}

    def execute(self, message):
        self.operations[message['operation']](message)

    def message_contact(self, message):
        first = message['from']
        second = message['to']
        if second < first:
            second = first
            first = message['to']
        if first not in self.contacts_messages:
            self.contacts_messages[first] = {}
        if second in self.contacts_messages[first]:
            self.contacts_messages[first][second].append(message)
        else:
            self.contacts_messages[first][second] = [message]

    def message_group(self, message):
        name = message['to']
        if name in self.groups_messages:
            self.groups_messages[name].append(message)
        else:
            self.groups_messages[name] = [message]


    def print(self):
        for first in self.contacts_messages:
            for second in self.contacts_messages[first]:
                print(f'{first}-{second}:')
                for message in self.contacts_messages[first][second]:
                    print(f'  {message["from"]}: {message["message"]}')
        for group in self.groups_messages:
            print(f'{group}:')
            for message in self.groups_messages[group]:
                print(f'  {message["from"]}: {message["message"]}')


    def read_chat(self):
        reply = requests.get(f'{self.address}/dag')
        (sinks, reverse, transactions) = reverse_dag(reply.json())
        order = order_dag(sinks, reverse)
        for tx_list in order:
            for key in tx_list:
                transaction = transactions[key]['content']
                if transaction['application'] == 'Chat':
                    self.execute(transaction)
