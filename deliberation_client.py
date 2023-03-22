import requests
import sys
from address_book import AddressBook
from deliberation import Deliberation


class DeliberationClient:
    def __init__(self, port, name):
        self.port = port
        self.agent = name
        self.agent_key = None
        self.address = f'http://localhost:{port}'

    def identify_myself(self):
        book = AddressBook(self.address)
        contacts = book.get_contacts_list()
        contact_keys = list(contacts.keys())
        print('Who are you:')
        for index, key in enumerate(contact_keys):
            print(f'  {index+1}- {contacts[key]}')
        self.agent_key = contact_keys[int(input())-1]
        print(f'Your name is {contacts[self.agent_key]}')

    def message_contact(self):
        book = AddressBook(self.address)
        contacts = book.get_contacts_list()
        contact_keys = list(contacts.keys())
        print('Select a contact:')
        for index, key in enumerate(contact_keys):
            print(f'  {index+1}- {contacts[key]}')
        key = contact_keys[int(input())-1]
        print('type your message')
        message = input()
        payload = {'owner': self.address,
                   'application': 'Deliberation',
                   'operation': 'MessageContact',
                   'functionals': [self.agent_key, key],
                   'from': 0,
                   'to': 1,
                   'message': message}
        reply = requests.post(f'{self.address}/message', json=payload)
        contact_address = book.get_contact(key)['address']
        requests.post(f'{contact_address}/transaction', json=[reply.json()])


    def message_group(self):
        book = AddressBook(self.address)
        groups = book.get_groups_list()
        group_keys = list(groups.keys())
        print('select a group:')
        for index, key in enumerate(group_keys):
            print(f'  {index+1}- {groups[key]}')
        key = group_keys[int(input())-1]
        print('type your message')
        message = input()
        payload = {'owner': self.address,
                   'application': 'Deliberation',
                   'operation': 'MessageGroup',
                   'functionals': [self.agent_key, key],
                   'from': 0,
                   'to': 1,
                   'message': message}
        reply = requests.post(f'{self.address}/message', json=payload)
        group = book.get_group_members(key)
        for contact in group:
            contact_address = book.get_contact(contact)['address']
            requests.post(f'{contact_address}/transaction', json=[reply.json()])

    def propose(self):
        book = AddressBook(self.address)
        groups = book.get_groups_list()
        group_keys = list(groups.keys())
        print('select a group:')
        for index, key in enumerate(group_keys):
            print(f'  {index+1}- {groups[key]}')
        key = group_keys[int(input())-1]
        print('type your proposal')
        message = input()
        payload = {'owner': self.address,
                   'application': 'Deliberation',
                   'operation': 'Propose',
                   'functionals': [self.agent_key, key],
                   'from': 0,
                   'to': 1,
                   'message': message}
        reply = requests.post(f'{self.address}/message', json=payload)
        group = book.get_group_members(key)
        for contact in group:
            contact_address = book.get_contact(contact)['address']
            requests.post(f'{contact_address}/transaction', json=[reply.json()])

    def support(self):
        deliberation = Deliberation(self.address)
        group_keys = deliberation.get_groups_keys()
        print('select a group:')
        for index, key in enumerate(group_keys):
            book = AddressBook(self.address, key)
            name = book.get_group(key)['name']
            print(f'  {index+1}- {name}')
        selected_group_key = group_keys[int(input())-1]
        proposals = deliberation.get_proposals(selected_group_key)
        proposal_keys = list(proposals.keys())
        for index, key in enumerate(proposal_keys):
            print(f'  {index+1}- {proposals[key]["message"]}')
        proposal = proposal_keys[int(input())-1]
        book = AddressBook(self.address, selected_group_key)
        members = book.get_group_members(selected_group_key)
        print('select your support:')
        print('  1- full support')
        print('  2- conditional support')
        option = int(input())
        reply = {}
        if option == 1:
            payload = {'owner': self.address,
                       'application': 'Deliberation',
                       'operation': 'Support',
                       'functionals': [proposal, self.agent_key],
                       'proposal': 0,
                       'supporter': 1}
            reply = requests.post(f'{self.address}/message', json=payload)
        elif option == 2:
            keys = list(members.keys())
            indexes = set()
            while True:
                print('select relevant members (0 to continue):')
                for index, key in enumerate(keys):
                    if index not in indexes:
                        print(f'  {index + 1}- {members[key]}')
                selection = int(input())
                if selection:
                    indexes.add(selection - 1)
                    print([members[keys[index]] for index in indexes if index in range(len(members))])
                else:
                    break
            print('enter your support threshold (from 0 to 100):')
            percent = int(input())
            payload = {'owner': self.address,
                       'application': 'Deliberation',
                       'operation': 'ConditionalSupport',
                       'functionals': [proposal, self.agent_key]+[keys[key] for key in indexes],
                       'proposal': 0,
                       'supporter': 1,
                       'from': [*range(2,2+len(indexes))],
                       'percent': percent}
            reply = requests.post(f'{self.address}/message', json=payload)
        for contact in members:
            contact_address = book.get_contact(contact)['address']
            requests.post(f'{contact_address}/transaction', json=[reply.json()])

    def list_deliberation(self):
        deliberation = Deliberation(self.address)
        print(f'{self.agent} deliberation:')
        deliberation.print()

    def run(self):
        main_menu = ['select an action:',
                     '  1- identify myself',
                     '  2- message contact',
                     '  3- message group',
                     '  4- propose a proposal',
                     '  5- support a proposal',
                     '  6- list deliberation',
                     '  7- quit']
        main_actions = [(self.identify_myself, []),
                        (self.message_contact, []), (self.message_group, []),
                        (self.propose, []), (self.support, []),
                        (self.list_deliberation, []), (False, [])]
        next_menu = main_menu
        actions = main_actions
        while next_menu:
            if isinstance(next_menu, list):
                for command in next_menu:
                    print(command)
                (next_menu, actions) = actions[int(input())-1]
            elif callable(next_menu):
                next_menu()
                next_menu = True
            elif next_menu:
                next_menu = main_menu
                actions = main_actions

DeliberationClient(sys.argv[1], sys.argv[2]).run()
