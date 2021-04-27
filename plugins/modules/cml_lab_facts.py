#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlModule, cml_argument_spec

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: cml_lab_facts
short_description: Get facts about a CML Lab
description:
  - Get facts about a CML Lab
author:
  - Steven Carter
requirements:
  - virl2_client
version_added: '0.1.0'
options:
    lab:
        description: The name of the CML lab
        required: false
        type: string
        default: 'env: CML_LAB'
        env:
            - name: CML_LAB
    validate_certs:
        description: certificate validation
        required: false
        choices: ['yes', 'no']
extends_documentation_fragment: cisco.cml.cml
"""
EXAMPLES = r"""
- name: Check initial topology connectivity
  hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - name: Get facts about a lab in CML
      cisco.cml.cml_lab_facts:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
      register: results

    - debug:
        var: results
"""


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = cml_argument_spec()
    argument_spec.update(lab=dict(type='str', required=True), )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    cml = cmlModule(module)
    cml_facts = {}
    labs = cml.client.find_labs_by_title(cml.params['lab'])
    if len(labs):
        # Just take the first lab until we figure out how we want
        # to handle duplicates
        lab = labs[0]
        lab.sync()
        cml_facts['details'] = lab.details()
        cml_facts['nodes'] = {}
        for node in lab.nodes():
            cml_facts['nodes'][node.label] = {
                'state': node.state,
                'image_definition': node.image_definition,
                'node_definition': node.node_definition,
                'cpus': node.cpus,
                'ram': node.ram,
                'config': node.config,
                'data_volume': node.data_volume,
                'tags': node.tags(),
                'interfaces': {}
            }
            ansible_host = None
            for interface in node.interfaces():
                if interface.discovered_ipv4 and not ansible_host:
                    ansible_host = interface.discovered_ipv4[0]
                cml_facts['nodes'][node.label]['interfaces'][interface.label] = {
                    'state': interface.state,
                    'ipv4_addresses': interface.discovered_ipv4,
                    'ipv6_addresses': interface.discovered_ipv6,
                    'mac_address': interface.discovered_mac_address,
                    'is_physical': interface.is_physical,
                    'readbytes': interface.readbytes,
                    'readpackets': interface.readpackets,
                    'writebytes': interface.writebytes,
                    'writepackets': interface.writepackets                    
                }
            cml_facts['nodes'][node.label]['ansible_host'] = ansible_host
    cml.result['cml_facts'] = cml_facts
    cml.exit_json(**cml.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
