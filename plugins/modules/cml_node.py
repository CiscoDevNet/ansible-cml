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
module: cml_node
short_description: Create, update or delete a node in a CML Lab
description:
  - Create, update or delete a node in a CML Lab
author:
  - Steven Carter (@stevenca)
requirements:
  - virl2_client
version_added: '0.1.0'
options:
    state:
        description: The desired state of the node
        required: false
        type: str
        choices: ['absent', 'present', 'started', 'stopped', 'wiped']
        default: present
    lab:
        description: The name of the CML lab (CML_LAB)
        required: true
        type: str
    name:
        description: The name of the node
        required: true
        type: str

    node_definition:
        description: The node definition of this node
        required: false
        type: str

    image_definition:
        description: The image definition of this node
        required: false
        type: str

    config:
        description: The day0 configuration of this node
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
extends_documentation_fragment: cisco.cml.cml
"""

EXAMPLES = r"""
- name: Start the CML nodes
  hosts: cml_hosts
  connection: local
  gather_facts: no
  tasks:
    - name: Generating day0 config
      set_fact:
        day0_config: "{{ lookup('template', cml_config_template) }}"
      when: cml_config_template is defined

    - name: Start Node
      cisco.cml.cml_node:
        name: "{{ inventory_hostname }}"
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        state: started
        image_definition: "{{ cml_image_definition | default(omit) }}"
        config: "{{ day0_config | default(omit) }}"
"""

import traceback
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlModule, cml_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = cml_argument_spec()
    argument_spec.update(
        state=dict(type='str', choices=['absent', 'present', 'started', 'stopped', 'wiped'], default='present'),
        name=dict(type='str', required=True),
        lab=dict(type='str', required=True, fallback=(env_fallback, ['CML_LAB'])),
        node_definition=dict(type='str'),
        image_definition=dict(type='str'),
        config=dict(type='str'),
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

    node = cml.get_node_by_name(lab, cml.params['name'])
    if cml.params['state'] == 'present':
        if node is None:
            node = lab.create_node(label=cml.params['name'], node_definition=cml.params['node_definition'])
            cml.result['changed'] = True
    elif cml.params['state'] == 'started':
        if node is None:
            cml.fail_json("Node must be created before it is started")
        if node.state not in ['STARTED', 'BOOTED']:
            if node.state == 'DEFINED_ON_CORE' and cml.params['config']:
                node.config = cml.params['config']
            if cml.params['image_definition']:
                node.image_definition = cml.params['image_definition']
            if cml.params['wait'] is False:
                lab.wait_for_covergence = False
            node.start()
            cml.result['changed'] = True
    elif cml.params['state'] == 'stopped':
        if node is None:
            cml.fail_json("Node must be created before it is stopped")
        if node.state not in ['STOPPED', 'DEFINED_ON_CORE']:
            if cml.params['wait'] is False:
                lab.wait_for_covergence = False
            node.stop()
            cml.result['changed'] = True
    elif cml.params['state'] == 'wiped':
        if node is None:
            cml.fail_json("Node must be created before it is wiped")
        if node.state not in ['DEFINED_ON_CORE']:
            node.wipe(wait=cml.params['wait'])
            cml.result['changed'] = True
    cml.exit_json(**cml.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
