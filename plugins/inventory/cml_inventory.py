from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
from virl2_client import ClientLibrary
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_text

DOCUMENTATION = r'''
    name: cml
    plugin_type: inventory
    short_description: Returns Inventory from the CML server
    description:
        - Retrieves inventory from the CML server
    options:
        plugin:
            description: Name of the plugin
            required: true
            choices: ['cml']
        host:
            description: FQDN of the target host
            required: false
        username:
            description: user credential for target system
            required: false
        password:
            description: user pass for the target system
            required: false
        lab:
            description: The name of the cml lab
            required: false
        group:
            description: The name of group in which to put nodes
            required: false
        validate_certs:
            description: certificate validation
            required: false
            choices: ['yes', 'no']
'''


class InventoryModule(BaseInventoryPlugin):

    NAME = 'cisco.cml.cml_inventory'

    def __init__(self):
        super(InventoryModule, self).__init__()

        # from config
        self.username = None
        self.password = None
        self.host = None
        self.lab = None
        self.group = None

    def verify_file(self, path):

        if super(InventoryModule, self).verify_file(path):
            endings = ('cml.yaml', 'cml.yml')
            if any((path.endswith(ending) for ending in endings)):
                return True
        display.debug("cml inventory filename must end with 'cml.yml' or 'cml.yaml'")
        return False

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        # config = self._read_config_data(self, path)
        self._read_config_data(path)

        # if NOT using _read_config_data you should call set_options directly,
        # to process any defined configuration for this plugin,
        # if you dont define any options you can skip
        # self.set_options()

        if 'CML_HOST' in os.environ and len(os.environ['CML_HOST']):
            self.host = os.environ['CML_HOST']
        else:
            self.host = self.get_option('host')

        self.display.vvv("cml.py - CML_HOST: {0}".format(self.host))

        if 'CML_USERNAME' in os.environ and len(os.environ['CML_USERNAME']):
            self.username = os.environ['CML_USERNAME']
        else:
            self.username = self.get_option('username')

        self.display.vvv("cml.py - CML_USERNAME: {0}".format(self.username))

        if 'CML_PASSWORD' in os.environ and len(os.environ['CML_PASSWORD']):
            self.password = os.environ['CML_PASSWORD']
        else:
            self.password = self.get_option('password')

        if 'CML_LAB' in os.environ and len(os.environ['CML_LAB']):
            self.lab = os.environ['CML_LAB']
        else:
            self.lab = self.get_option('lab')

        self.display.vvv("cml.py - CML_LAB: {0}".format(self.lab))

        if not self.lab:
            self.display.vvv("No lab defined.  Nothing to do.")
            return

        self.group = self.get_option('group')
        if self.group is None:
            self.group = 'cml_hosts'

        self.display.vvv("cml.py - Group: {0}".format(self.group))

        self.inventory.set_variable('all', 'cml_host', self.host)
        self.inventory.set_variable('all', 'cml_username', self.username)
        self.inventory.set_variable('all', 'cml_password', self.password)
        self.inventory.set_variable('all', 'cml_lab', self.lab)

        url = 'https://{0}'.format(self.host)
        try:
            client = ClientLibrary(url, username=self.username, password=self.password, ssl_verify=False)
        except:
            raise AnsibleParserError('Unable to log into {0}'.format(url))

        labs = (client.find_labs_by_title(self.lab))
        if not labs:
            return

        try:
            group = self.inventory.add_group(self.group)
        except AnsibleError as e:
            raise AnsibleParserError("Unable to add group %s: %s" % (group, to_text(e)))
        group_dict = {}

        lab = labs[0]
        lab.sync()
        for node in lab.nodes():
            self.inventory.add_host(node.label, group=self.group)
            cml = {
                'state': node.state,
                'image_definition': node.image_definition,
                'node_definition': node.node_definition,
                'cpus': node.cpus,
                'ram': node.ram,
                'config': node.config,
                'data_volume': node.data_volume,
            }
            interface_list = []
            ansible_host = None
            for interface in node.interfaces():
                if interface.discovered_ipv4 and not ansible_host:
                    ansible_host = interface.discovered_ipv4[0]
                interface_dict = {
                    'name': interface.label,
                    'state': interface.state,
                    'ipv4_addresses': interface.discovered_ipv4,
                    'ipv6_addresses': interface.discovered_ipv6,
                    'mac_address': interface.discovered_mac_address
                }
                interface_list.append(interface_dict)
            cml.update({'interfaces': interface_list})
            if ansible_host:
                self.inventory.set_variable(node.label, 'ansible_host', ansible_host)
            self.inventory.set_variable(node.label, 'cml_facts', cml)
            self.display.vvv("Adding {0}({1}) to group {2}, state: {3}, ansible_host: {4}".format(
                node.label, node.node_definition, self.group, node.state, ansible_host))
            # Group by node_definition
            if node.node_definition not in group_dict:
                try:
                    group_dict[node.node_definition] = self.inventory.add_group(node.node_definition)
                except AnsibleError as e:
                    raise AnsibleParserError("Unable to add group %s: %s" % (group, to_text(e)))
            self.inventory.add_host(node.label, group=node.node_definition)
