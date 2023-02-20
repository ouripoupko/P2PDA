import requests
import sys
from address_book import AddressBook

port = sys.argv[1]
agent = sys.argv[2]

address = f'http://localhost:{port}'

main_menu = ['select an action:',
             '  1- contact menu',
             '  2- group menu',
             '  3- share records',
             '  4- list address book',
             '  5- quit']

contact_menu = ['contact menu:',
                '  1- create',
                '  2- delete',
                '  3- modify']

group_menu = ['group menu:',
              '  1- create',
              '  2- delete',
              '  3- modify']

modify_group_menu = ['select modify action:',
              '  1- add member',
              '  2- remove member']


def create_contact():
    print('Enter name of contact:')
    name = input()
    print('enter address of contact:')
    contact_address = input()
    requests.post(f'{address}/message', json={'owner': address,
                                              'application': 'SocialNetwork',
                                              'operation': 'CreateContact',
                                              'functionals': [],
                                              'name': name,
                                              'address': contact_address})

def delete_contact():
    book = AddressBook(address)
    contacts = book.get_contacts_list()
    keys = list(contacts.keys())
    print('select contact to delete:')
    for index, key in enumerate(keys):
        print(f'  {index+1}- {contacts[key]}')
    key = keys[int(input())-1]
    requests.post(f'{address}/message', json={'owner': address,
                                              'application': 'SocialNetwork',
                                              'operation': 'DeleteContact',
                                              'functionals': [key],
                                              'contact': 0})

def modify_contact():
    book = AddressBook(address)
    contacts = book.get_contacts_list()
    keys = list(contacts.keys())
    print('select contact to modify:')
    for index, key in enumerate(keys):
        print(f'  {index+1}- {contacts[key]}')
    key = keys[int(input())-1]
    print('enter new address:')
    contact_address = input()
    requests.post(f'{address}/message', json={'owner': address,
                                              'application': 'SocialNetwork',
                                              'operation': 'UpdateContact',
                                              'functionals': [key],
                                              'contact': 0,
                                              'address': contact_address})

def create_group():
    book = AddressBook(address)
    contacts = book.get_contacts_list()
    keys = list(contacts.keys())
    indexes = set()
    while True:
        print('select contacts to group (0 to continue):')
        for index, key in enumerate(keys):
            if index not in indexes:
                print(f'  {index + 1}- {contacts[key]}')
        selection = int(input())
        if selection:
            indexes.add(selection-1)
            print([contacts[keys[index]] for index in indexes if index in range(len(contacts))])
        else:
            break
    if indexes:
        print('Enter name of group:')
        name = input()
        members = [keys[index] for index in indexes if index in range(len(keys))]
        requests.post(f'{address}/message', json={'owner': address,
                                                  'application': 'SocialNetwork',
                                                  'operation': 'CreateGroup',
                                                  'functionals': members,
                                                  'name': name,
                                                  'contacts': [*range(len(members))]})

def delete_group():
    book = AddressBook(address)
    groups = book.get_groups_list()
    keys = list(groups.keys())
    print('select group to delete:')
    for index, key in enumerate(keys):
        print(f'  {index+1}- {groups[key]}')
    key = keys[int(input())-1]
    requests.post(f'{address}/message', json={'owner': address,
                                              'application': 'SocialNetwork',
                                              'operation': 'DeleteGroup',
                                              'functionals': [key],
                                              'group': 0})

def add_member():
    book = AddressBook(address)
    groups = book.get_groups_list()
    keys = list(groups.keys())
    print('select group to modify:')
    for index, key in enumerate(keys):
        print(f'  {index+1}- {groups[key]}')
    group = keys[int(input())-1]
    members = book.get_group_members(group)
    contacts = book.get_contacts_list()
    contact_keys = list(contacts.keys())
    print('select contact to add:')
    for index, key in enumerate(contact_keys):
        if key not in members:
            print(f'  {index + 1}- {contacts[key]}')
    contact = contact_keys[int(input())-1]
    requests.post(f'{address}/message', json={'owner': address,
                                              'application': 'SocialNetwork',
                                              'operation': 'ModifyGroupAdd',
                                              'functionals': [group, contact],
                                              'group': 0,
                                              'contact': 1})

def remove_member():
    book = AddressBook(address)
    groups = book.get_groups_list()
    keys = list(groups.keys())
    print('select group to modify:')
    for index, key in enumerate(keys):
        print(f'  {index+1}- {groups[key]}')
    group = keys[int(input())-1]
    members = book.get_group_members(group)
    member_keys = list(members.keys())
    print('select member to remove:')
    for index, key in enumerate(member_keys):
        print(f'  {index + 1}- {members[key]}')
    member = member_keys[int(input())-1]
    requests.post(f'{address}/message', json={'owner': address,
                                              'application': 'SocialNetwork',
                                              'operation': 'ModifyGroupRemove',
                                              'functionals': [group, member],
                                              'group': 0,
                                              'member': 1})

def share_records():
    reply = requests.get(f'{address}/dag')
    transactions = reply.json()
    while True:
        for tx in transactions:
            print(tx['content'])
        print('select a filter (Enter to continue)')
        tx_filter = input()
        if tx_filter == '':
            break
        values = list({tx['content'][tx_filter] for tx in transactions if tx_filter in tx['content']})
        selected_values = set()
        while True:
            print('select values (0 to continue):')
            for index, value in enumerate(values):
                if value not in selected_values:
                    print(f'  {index+1}- {value}')
            selection = int(input())
            if selection:
                selected_values.add(values[selection-1])
                print(selected_values)
            else:
                break
        transactions = [tx
                        for tx in transactions
                        if tx_filter in tx['content'] and tx['content'][tx_filter] in selected_values]
    book = AddressBook(address)
    contacts = book.get_contacts_list()
    contact_keys = list(contacts.keys())
    print('select contact to share with:')
    for index, key in enumerate(contact_keys):
        print(f'  {index+1}- {contacts[key]}')
    key = contact_keys[int(input())-1]
    recipient = book.get_contact(key)
    share_address = recipient['address']
    requests.post(f'{share_address}/transaction', json=transactions)

def list_address_book():
    book = AddressBook(address)
    print(f'{agent} address book:')
    book.print()

contact_actions = [(create_contact, []), (delete_contact, []), (modify_contact, [])]
modify_group_actions = [(add_member, []), (remove_member, [])]
group_actions = [(create_group, []), (delete_group, []), (modify_group_menu, modify_group_actions)]
main_actions = [(contact_menu, contact_actions), (group_menu, group_actions),
                (share_records, []), (list_address_book,[]), (False, [])]

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
