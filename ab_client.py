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
    requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                              'operation': 'CreateContact',
                                              'name': name,
                                              'address': contact_address})

def delete_contact():
    book = AddressBook(address)
    book.read_address_book()
    contacts = book.get_contacts_list()
    print('select contact to delete:')
    for index, name in enumerate(contacts):
        print(f'  {index+1}- {name}')
    name = contacts[int(input())-1]
    requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                              'operation': 'DeleteContact',
                                              'name': name})

def modify_contact():
    book = AddressBook(address)
    book.read_address_book()
    contacts = book.get_contacts_list()
    print('select contact to modify:')
    for index, name in enumerate(contacts):
        print(f'  {index+1}- {name}')
    name = contacts[int(input())-1]
    print('enter new address:')
    contact_address = input()
    requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                              'operation': 'UpdateContact',
                                              'name': name,
                                              'address': contact_address})

def create_group():
    book = AddressBook(address)
    book.read_address_book()
    contacts = book.get_contacts_list()
    indexes = set()
    while True:
        print('select contacts to group (0 to continue):')
        for index, name in enumerate(contacts):
            if index not in indexes:
                print(f'  {index + 1}- {name}')
        selection = int(input())
        if selection:
            indexes.add(selection-1)
            print([contacts[index] for index in indexes if index in range(len(contacts))])
        else:
            break
    if indexes:
        print('Enter name of group:')
        name = input()
        members = [contacts[index] for index in indexes if index in range(len(contacts))]
        requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                                  'operation': 'CreateGroup',
                                                  'name': name,
                                                  'members': members})

def delete_group():
    book = AddressBook(address)
    book.read_address_book()
    groups = book.get_groups_list()
    print('select group to delete:')
    for index, name in enumerate(groups):
        print(f'  {index+1}- {name}')
    name = groups[int(input())-1]
    requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                              'operation': 'DeleteGroup',
                                              'name': name})

def add_member():
    book = AddressBook(address)
    book.read_address_book()
    groups = book.get_groups_list()
    print('select group to modify:')
    for index, name in enumerate(groups):
        print(f'  {index+1}- {name}')
    group_name = groups[int(input())-1]
    members = book.get_group_members(group_name)
    contacts = book.get_contacts_list()
    print('select contact to add:')
    for index, name in enumerate(contacts):
        if name not in members:
            print(f'  {index + 1}- {name}')
    contact_name = contacts[int(input())-1]
    requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                              'operation': 'ModifyGroupAdd',
                                              'name': group_name,
                                              'contact_name': contact_name})

def remove_member():
    book = AddressBook(address)
    book.read_address_book()
    groups = book.get_groups_list()
    print('select group to modify:')
    for index, name in enumerate(groups):
        print(f'  {index+1}- {name}')
    group_name = groups[int(input())-1]
    members = book.get_group_members(group_name)
    print('select member to remove:')
    for index, name in enumerate(members):
        print(f'  {index + 1}- {name}')
    contact_name = members[int(input())-1]
    requests.post(f'{address}/message', json={'application': 'SocialNetwork',
                                              'operation': 'ModifyGroupRemove',
                                              'name': group_name,
                                              'member_name': contact_name})

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
    book.read_address_book()
    contacts = book.get_contacts_list()
    print('select contact to share with:')
    for index, name in enumerate(contacts):
        print(f'  {index+1}- {name}')
    name = contacts[int(input())-1]
    share_address = book.get_contact(name)
    requests.post(f'{share_address}/transaction', json=transactions)

def list_address_book():
    book = AddressBook(address)
    book.read_address_book()
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

# delete, modify
# interpret output