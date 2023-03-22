import requests
from dag_utils import find_sources, order_sources
from address_book import AddressBook

class Deliberation:
    def __init__(self, address):
        self.contacts_messages = {}
        self.groups_messages = {}
        self.supporters = {}
        self.conditionals = {}
        self.address = address
        self.operations = {'MessageContact': self.message_contact,
                           'MessageGroup': self.message_group,
                           'Propose': self.message_group,
                           'Support': self.support,
                           'ConditionalSupport': self.flexible_support}
        self.read_deliberation()

    def execute(self, key, message):
        self.operations[message['operation']](key, message)

    def message_contact(self, key, message):
        first = message['functionals'][message['from']]
        second = message['functionals'][message['to']]
        if second < first:
            second = first
            first = message['functionals'][message['to']]
        if first not in self.contacts_messages:
            self.contacts_messages[first] = {}
        if second in self.contacts_messages[first]:
            self.contacts_messages[first][second].append(message)
        else:
            self.contacts_messages[first][second] = [message]

    def message_group(self, key, message):
        name = message['functionals'][message['to']]
        if name not in self.groups_messages:
            self.groups_messages[name] = {}
            self.groups_messages[name]['order'] = []
        self.groups_messages[name][key] = message
        self.groups_messages[name]['order'].append(key)

    def support(self, key, message):
        proposal = message['functionals'][message['proposal']]
        supporter = message['functionals'][message['supporter']]
        if proposal not in self.supporters:
            self.supporters[proposal] = set()
        self.supporters[proposal].add(supporter)

    def flexible_support(self, key, message):
        proposal = message['functionals'][message['proposal']]
        supporter = message['functionals'][message['supporter']]
        target_group = [message['functionals'][key] for key in message['from']]
        percent = message['percent']
        if proposal not in self.conditionals:
            self.conditionals[proposal] = {}
        self.conditionals[proposal][supporter] = {'from': target_group, 'percent': percent}

    def print(self):
        names = {}
        for first in self.contacts_messages:
            first_book = AddressBook(self.address, first)
            names[first] = first_book.get_contact(first)['name']
            for second in self.contacts_messages[first]:
                second_book = AddressBook(self.address, second)
                names[second] = second_book.get_contact(second)['name']
                print(f'{names[first]}-{names[second]}:')
                for message in self.contacts_messages[first][second]:
                    print(f'  {names[message["functionals"][message["from"]]]}: {message["message"]}')
        for group in self.groups_messages:
            group_book = AddressBook(self.address, group)
            names[group] = group_book.get_groups_list()[group]
            print(f'{names[group]}:')
            for key in self.groups_messages[group]['order']:
                message = self.groups_messages[group][key]
                sender = message["functionals"][message["from"]]
                sender_book = AddressBook(self.address, sender)
                names[sender] = sender_book.get_contact(sender)['name']
                if message['operation'] == 'Propose':
                    print(f'  {names[sender]} proposes: {message["message"]}')
                    supporters = self.supporters[key].copy() if key in self.supporters else set()
                    conditionals = list(self.conditionals[key].keys()) if key in self.conditionals else {}
                    changed = True
                    while changed:
                        changed = False
                        for swinger in conditionals:
                            condition = self.conditionals[key][swinger]
                            passed = [pass_key for pass_key in condition['from'] if pass_key in supporters]
                            ratio = len(passed)*100/len(condition['from'])
                            if ratio >= condition['percent']:
                                supporters.add(swinger)
                                conditionals.remove(swinger)
                                changed = True
                    print(f'    {len(supporters)} people supporting')
                else:
                    print(f'  {names[sender]}: {message["message"]}')

    def read_deliberation(self):
        reply = requests.get(f'{self.address}/dag',
                             params={'application': 'Deliberation'})
        (sources, transactions) = find_sources(reply.json())
        order = order_sources(sources, transactions)
        for tx_list in order:
            for key in tx_list:
                self.execute(transactions[key]['hash_code'], transactions[key]['content'])

    def get_groups_keys(self):
        return list(self.groups_messages.keys())

    def get_proposals(self, group):
        proposals = {}
        for key in self.groups_messages[group]['order']:
            if self.groups_messages[group][key]['operation'] == 'Propose':
                proposals[key] = self.groups_messages[group][key]
        return proposals
