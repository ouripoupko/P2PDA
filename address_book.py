import requests
from dag_utils import find_sources, order_sources

class AddressBook:
    def __init__(self, address, key = None):
        self.contacts = {}
        self.groups = {}
        self.address = address
        self.operations = {'CreateContact': self.create_contact,
                           'DeleteContact': self.delete_contact,
                           'UpdateContact': self.update_contact,
                           'CreateGroup': self.create_group,
                           'DeleteGroup': self.delete_group,
                           'ModifyGroupAdd': self.add_member,
                           'ModifyGroupRemove': self.remove_member}
        self.read_address_book(key)

    def execute(self, key, message):
        self.operations[message['operation']](key, message)

    def create_contact(self, key, message):
        if key in self.contacts:
            print('contact already exists')
        else:
            self.contacts[key] = {'name': message['name'],
                                  'address': message['address']}

    def delete_contact(self, key, message):
        index = message['contact']
        hash_code = message['functionals'][index]
        if hash_code in self.contacts:
            del self.contacts[hash_code]
        else:
            print('missing contact to delete')

    def update_contact(self, key, message):
        index = message['contact']
        hash_code = message['functionals'][index]
        if hash_code in self.contacts:
            self.contacts[key] = self.contacts[hash_code]
            self.contacts[key]['address'] = message['address']
            del self.contacts[hash_code]
        else:
            print('missing contact to update')

    def create_group(self, key, message):
        indexes = message['contacts']
        keys = [message['functionals'][index] for index in indexes]
        if key in self.groups:
            print('group already exists')
        else:
            self.groups[key] = {'name': message['name'], 'members': []}
            for member in keys:
                if member in self.contacts:
                    self.groups[key]['members'].append(member)

    def delete_group(self, key, message):
        index = message['group']
        hash_code = message['functionals'][index]
        if hash_code in self.groups:
            del self.groups[hash_code]
        else:
            print('missing group to delete')

    def add_member(self, key, message):
        contact_index = message['contact']
        contact_key = message['functionals'][contact_index]
        group_index = message['group']
        group_key = message['functionals'][group_index]
        if group_key in self.groups:
            if contact_key in self.contacts:
                self.groups[key] = self.groups[group_key]
                self.groups[key]['members'].append(contact_key)
                del self.groups[group_key]
            else:
                print('missing contact to add')
        else:
            print('missing group to modify')

    def remove_member(self, key, message):
        contact_index = message['member']
        contact_key = message['functionals'][contact_index]
        group_index = message['group']
        group_key = message['functionals'][group_index]
        if group_key in self.groups:
            if contact_key in self.groups[group_key]['members']:
                self.groups[key] = self.groups[group_key]
                self.groups[key]['members'].remove(contact_key)
                del self.groups[group_key]
            else:
                print('missing member to remove')
        else:
            print('missing group to modify')

    def print(self):
        print('  contacts:')
        for contact in self.contacts.values():
            print(f'    {contact["name"]}: {contact["address"]}')
        print('  groups:')
        for group in self.groups.values():
            members = [self.contacts[key]['name'] for key in group['members'] if key in self.contacts]
            print(f'    {group["name"]}: {members}')

    def get_contacts_list(self):
        return {key: self.contacts[key]['name'] for key in self.contacts}

    def get_contact(self, key):
        return self.contacts[key]

    def get_groups_list(self):
        return {key: self.groups[key]['name'] for key in self.groups}

    def get_group(self, key):
        return self.groups[key]

    def get_group_members(self, key):
        return {contact_key: self.contacts[contact_key]['name']
                for contact_key in self.groups[key]['members']
                if contact_key in self.contacts}

    def read_address_book(self, key):
        reply = requests.get(f'{self.address}/dag',
                             params={'application': 'SocialNetwork',
                                     'source': key})
        (sources, transactions) = find_sources(reply.json())
        order = order_sources(sources, transactions)
        for tx_list in order:
            for key in tx_list:
                self.execute(transactions[key]['hash_code'], transactions[key]['content'])
