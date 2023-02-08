import requests
import sys
from address_book import AddressBook
from chat import Chat


port = sys.argv[1]
agent = sys.argv[2]

address = f'http://localhost:{port}'

main_menu = ['select an action:',
             '  1- message contact',
             '  2- message group',
             '  3- list messages',
             '  4- quit']


def message_contact():
    book = AddressBook(address)
    book.read_address_book()
    contacts = book.get_contacts_list()
    print('Select a contact:')
    for index, name in enumerate(contacts):
        print(f'  {index+1}- {name}')
    name = contacts[int(input())-1]
    print('type your message')
    message = input()
    payload = {'application': 'Chat',
               'operation': 'MessageContact',
               'from': agent,
               'to': name,
               'message': message}
    reply = requests.post(f'{address}/message', json=payload)
    contact_address = book.get_contact(name)
    requests.post(f'{contact_address}/transaction', json=[reply.json()])


def message_group():
    book = AddressBook(address)
    book.read_address_book()
    groups = book.get_groups_list()
    print('select a group:')
    for index, name in enumerate(groups):
        print(f'  {index+1}- {name}')
    name = groups[int(input())-1]
    print('type your message')
    message = input()
    payload = {'application': 'Chat',
               'operation': 'MessageGroup',
               'from': agent,
               'to': name,
               'message': message}
    reply = requests.post(f'{address}/message', json=payload)
    group = book.get_group_members(name)
    for contact in group:
        contact_address = book.get_contact(contact)
        requests.post(f'{contact_address}/transaction', json=[reply.json()])

def list_messages():
    chat = Chat(address)
    chat.read_chat()
    print(f'{agent} messages:')
    chat.print()

main_actions = [(message_contact, []), (message_group, []),
                (list_messages, []), (False, [])]

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