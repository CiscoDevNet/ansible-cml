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


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: cml_lab
short_description: Create, update or delete a CML Lab
description:
  - Create, update or delete a CML Lab
author:
  - Steven Carter (@stevenca)
requirements:
  - virl2_client
version_added: '0.1.0'
options:
    lab:
        description: The name of the CML lab (CML_LAB)
        required: true
        type: str
    file:
        description: The name of the topology file to use.
        required: false
        type: str
    topology:
        description: The lab topology.
        required: false
        type: str
    state:
        description: The desired state of the lab
        required: false
        type: str
        choices: ['absent', 'present', 'started', 'stopped', 'wiped']
        default: present
    wait:
        description: Wait for lab virtual machines to boot before continuing
        required: false
        type: bool
        default: True
extends_documentation_fragment: cisco.cml.cml
"""

EXAMPLES = r"""
- name: Build the topology
  hosts: localhost
  gather_facts: no
  tags:
    - virl
    - network
  tasks:
    - name: Check for the lab file
      stat:
        path: "{{ cml_lab_file }}"
      register: stat_result
      delegate_to: localhost
      run_once: yes

    - assert:
        that:
          - stat_result.stat.exists
          - cml_host != ""
          - cml_username != ""
          - cml_password != ""
          - cml_lab != ""
        msg: "CML host, credentials, and topology file are required.  Verify the requirements in README are met."
      delegate_to: localhost
      run_once: yes

    - name: Create the lab
      cisco.cml.cml_lab:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        lab: "{{ cml_lab }}"
        state: present
        file: "{{ cml_lab_file }}"
      register: results

    - name: Refresh Inventory
      meta: refresh_inventory
"""

from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlModule, cml_argument_spec
from ansible.module_utils.basic import AnsibleModule, env_fallback
import os
import traceback


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = cml_argument_spec()
    argument_spec.update(state=dict(type='str',
                                    choices=['absent', 'present',
                                             'started', 'stopped', 'wiped'],
                                    default='present'),
                         lab=dict(type='str', required=True,
                                  fallback=(env_fallback, ['CML_LAB'])),
                         file=dict(type='str'),
                         topology=dict(type='str'),
                         wait=dict(type='bool', default=True))

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    cml = cmlModule(module)
    cml.result['changed'] = False
    labs = cml.client.find_labs_by_title(cml.params['lab'])
    if len(labs) > 0:
        lab = labs[0]
    else:
        lab = None

    if cml.params['state'] == 'present':
        if lab is None:
            if cml.params['topology']:
                lab = cml.client.import_lab(
                    cml.params['topology'], title=cml.params['lab'])
            elif cml.params['file']:
                if os.path.isabs(cml.params['file']):
                    topology_file = cml.params['file']
                else:
                    topology_file = os.getcwd() + '/' + cml.params['file']
                lab = cml.client.import_lab_from_path(
                    topology_file, title=cml.params['lab'])
            else:
                lab = cml.client.create_lab(title=cml.params['lab'])
            lab.title = cml.params['lab']
            cml.result['changed'] = True
    elif cml.params['state'] == 'started':
        if lab is None:
            if cml.params['topology']:
                lab = cml.client.import_lab(
                    cml.params['topology'], title=cml.params['lab'])
                lab.start(wait=cml.params['wait'])
            elif cml.params['file']:
                lab = cml.client.import_lab_from_path(
                    cml.params['file'], title=cml.params['lab'])
                lab.start(wait=cml.params['wait'])
            else:
                lab = cml.client.create_lab(title=cml.params['lab'])
                lab.start(wait=cml.params['wait'])
            lab.title = cml.params['lab']
            cml.result['changed'] = True
        elif lab.state() == "STOPPED":
            lab.start(wait=cml.params['wait'])
            cml.result['changed'] = True
    elif cml.params['state'] == 'absent':
        if lab:
            cml.result['changed'] = True
            if lab.state() == "STARTED":
                lab.stop(wait=True)
                lab.wipe(wait=True)
            elif lab.state() == "STOPPED":
                lab.wipe(wait=True)
            lab.remove()
    elif cml.params['state'] == 'stopped':
        if lab:
            if lab.state() == "STARTED":
                cml.result['changed'] = True
                lab.stop(wait=True)
    elif cml.params['state'] == 'wiped':
        if lab:
            if lab.state() == "STOPPED":
                cml.result['changed'] = True
                lab.wipe(wait=True)

    cml.exit_json(**cml.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
