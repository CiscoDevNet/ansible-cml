#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: cml_link_node
short_description: Create, update or delete a link between two nodes in a CML Lab
description:
  - Create, update or delete a link between two nodes in a CML Lab
  - Establishes a link between two nodes
  - Node names need to be specified to create the link
  - Node links can be updated to point to different nodes: node1->node2 is changed to node1->node3
  - Node links can be deleted
  - Note: when updating, all three nodes must be specified 
author:
  - Paul Pajerski (@ppajersk)
requirements:
  - virl2_client
version_added: '0.1.0'
options:
    action:
        description: The desired action to take with the link
        required: false
        type: str
        choices: ['create', 'update', 'delete']
        default: create

    lab:
        description: The name of the CML lab (CML_LAB)
        required: true
        type: str

    source_node:
        description: The name of the first node
        required: true
        type: str

    destination_node:
        description: The name of the second node
        required: true
        type: str    

    update_node:
        description: The name of the third node, this node is only used in update commands
        where if provided alongside the update action, will update the link between source_node and destination_node
        to link between source_node and update_node
        required: false
        type: str    

    x:
        description: X coordinate on topology canvas
        required: false
        type: int

    y:
        description: Y coordinate on topology canvas
        required: false
        type: int

    tags:
        description: List of tags
        required: false
        type: list
        elements: str

    wait:
        description: Wait for lab virtual machines to boot before continuing
        required: false
        type: bool
        default: False
"""

EXAMPLES = r"""
- name: Link two CML nodes
  hosts: cml_hosts
  connection: local
  gather_facts: no
  tasks:
    - name: Link nodes
      cisco.cml.cml_link_node:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        source_node: "{{ source_node }}"
        destination_node: "{{ destination_node }}"
        action: create

- name: Update a link between two CML nodes
  hosts: cml_hosts
  connection: local
  gather_facts: no
  tasks:
    - name: Link nodes
      cisco.cml.cml_link_node:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        source_node: "{{ source_node }}"
        destination_node: "{{ destination_node }}"
        update_node: "{{ update_node }}"
        action: update

- name: Delete a link between two CML nodes
  hosts: cml_hosts
  connection: local
  gather_facts: no
  tasks:
    - name: Link nodes
      cisco.cml.cml_link_node:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        source_node: "{{ source_node }}"
        destination_node: "{{ destination_node }}"
        action: delete
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlModule, cml_argument_spec

def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = cml_argument_spec()
    argument_spec.update(
        lab=dict(type='str', required=True, fallback=(env_fallback, ['CML_LAB'])),
        action=dict(type='str', required=True),
        source_node=dict(type='str', required=True),
        destination_node=dict(type='str', required=True),
        update_node=dict(type='str', required=False),
        tags=dict(type='list', elements='str'),
        x=dict(type='int'),
        y=dict(type='int'),
        wait=dict(type='bool', default=False),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    cml = cmlModule(module)

    labs = cml.client.find_labs_by_title(cml.params['lab'])
    if len(labs) > 0:
        lab = labs[0]
    else:
        cml.fail_json("Cannot find lab {0}".format(cml.params['lab']))

    # get both nodes by name
    source_node = cml.get_node_by_name(lab, cml.params['source_node'])
    destination_node = cml.get_node_by_name(lab, cml.params['destination_node'])
    update_node = cml.get_node_by_name(lab, cml.params['update_node'])

    if source_node == None or destination_node == None:
        cml.fail_json("One or more nodes cannot be found. Nodes need to be created before a link can be established")
        cml.exit_json(**cml.result)
        return
    
    link = cml.get_link_by_nodes(lab, source_node, destination_node)

    if cml.params['action'] == 'create':
        if link == None: # if the link does not exist
            link = lab.connect_two_nodes(source_node, destination_node) 
            cml.result['changed'] = True
        else:
            cml.fail_json("Link between nodes already exists") 
    elif cml.params['action'] == 'update':
        if link is not None:
            if update_node is not None: # only need to check if update_node is none here
                lab.remove_link(link) # remove current link
                link = lab.connect_two_nodes(source_node, update_node) # create new link
                cml.result['changed'] = True
            else:
               cml.fail_json("update_node cannot be found or does not exist")     
        else:
            cml.fail_json("Link between nodes does not exist")      
    elif cml.params['action'] == 'delete':
        if link is not None:
            lab.remove_link(link) # remove current link
            cml.result['changed'] = True
        else:
            cml.fail_json("Link between nodes does not exist") 
    cml.exit_json(**cml.result)

def main():
    run_module()

if __name__ == '__main__':
    main()    
