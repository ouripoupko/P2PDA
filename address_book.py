class AddressBook:
    def __init__(self):
        self.contacts = {}
        self.groups = {}
        self.operations = {'CreateContact': self.create_contact,
                           'DeleteContact': self.delete_contact,
                           'UpdateContact': self.update_contact,
                           'CreateGroup': self.create_group,
                           'DeleteGroup': self.delete_group,
                           'ModifyGroupAdd': self.add_member,
                           'ModifyGroupRemove': self.remove_member}

    def execute(self, message):
        self.operations[message['operation']](message)

    def create_contact(self, message):
        if message['name'] in self.contacts:
            print('contact already exists')
        else:
            self.contacts[message['name']] = message['address']

    def delete_contact(self, message):
        if message['name'] in self.contacts:
            del self.contacts[message['name']]
        else:
            print('missing contact to delete')

    def update_contact(self, message):
        if message['name'] in self.contacts:
            self.contacts[message['name']] = message['address']
        else:
            print('missing contact to update')

    def create_group(self, message):
        name = message['name']
        members = message['members']
        if name in self.groups:
            print('group already exists')
        else:
            self.groups[name] = []
            for member in members:
                if member in self.contacts:
                    self.groups[name].append(member)

    def delete_group(self, message):
        if message['name'] in self.groups:
            del self.groups[message['name']]
        else:
            print('missing group to delete')

    def add_member(self, message):
        if message['name'] in self.groups:
            if message['contact_name'] in self.contacts:
                self.groups[message['name']].append(message['contact_name'])
            else:
                print('missing contact to add')
        else:
            print('missing group to modify')

    def remove_member(self, message):
        if message['name'] in self.groups:
            if message['member_name'] in self.groups[message['name']]:
                self.groups[message['name']].remove(message['member_name'])
            else:
                print('missing member to remove')
        else:
            print('missing group to modify')

    def print(self):
        print('  contacts:')
        for contact in self.contacts:
            print(f'    {contact}: {self.contacts[contact]}')
        print('  groups:')
        for group in self.groups:
            print(f'    {group}: {self.groups[group]}')

    def get_contacts_list(self):
        return list(self.contacts.keys())

    def get_contact(self, name):
        return self.contacts[name]

    def get_groups_list(self):
        return list(self.groups.keys())

    def get_group_members(self, group):
        return self.groups[group]
