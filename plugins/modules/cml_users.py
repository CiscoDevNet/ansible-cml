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
module: cml_users
short_description: Manage CML Users
description:
  - Manage CML Users
author:
  - Yoshitaka Nagami (@exjobo)
requirements:
  - virl2_client
version_added: '0.1.0'
extends_documentation_fragment: cisco.cml.cml
options:
    name:
        description:
            - Name of the user to create, remove or modify.
        type: str
        required: true
    fullname:
        description:
            - Full Name of the user to create, remove or modify.
        type: str
    user_pass:
        description:
            - Desired password.
        type: str
    state:
        description:
            - Whether the account should exist or not, taking action if the state is different from what is stated.
        type: str
        choices: [ absent, present ]
        default: present
    admin:
        description:
            - Whether to create admin user.
        type: bool
        default: no
    groups:
        description:
            - List of groups user will be added to.
        type: list
        elements: str
    description:
        description:
            - Optionally sets the description of user account.
        type: str
"""
EXAMPLES = r"""
- name: Manage users
  hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - name: Add users to the CML instance
      cisco.cml.cml_users:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        name: "first_user"
        user_pass: "password"
        admin: yes
        state: "present"

    - name: Remove users from the CML instance
      cisco.cml.cml_users:
        host: "{{ cml_host }}"
        user: "{{ cml_username }}"
        password: "{{ cml_password }}"
        name: "old_user"
        state: "absent"
"""

import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.cisco.cml.plugins.module_utils.cml_utils import cmlModule, cml_argument_spec

try:
    import requests
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_REQUESTS = True


def get_userid(cml):
    try:
        userid = cml.client.user_management.user_id(cml.params['name'])
        return userid
    except requests.exceptions.RequestException as e:
        if e.response.status_code == 404:
            return None
        else:
            cml.fail_json(name=cml.params['name'], msg=e, rc=-1)


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = cml_argument_spec()
    argument_spec.update(name=dict(type='str', required=True),
                         fullname=dict(type='str', default=""),
                         user_pass=dict(type='str', no_log=True),
                         state=dict(type='str', default='present', choices=['absent', 'present']),
                         admin=dict(type='bool', default=False),
                         groups=dict(type='list', elements='str', default=[]),
                         description=dict(type='str', default=""),
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
    cml.result['changed'] = False
    cml.result['name'] = cml.params['name']
    cml.result['state'] = cml.params['state']
    userid = get_userid(cml)

    if not HAS_REQUESTS:
        # Needs: from ansible.module_utils.basic import missing_required_lib
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    if cml.params['state'] == 'present':
        if userid is None:
            if module.check_mode:
                module.exit_json(changed=True)
            module.debug('Create user %s' % cml.params['name'])
            try:
                cml.client.user_management.create_user(
                    username=cml.params['name'],
                    pwd=cml.params['user_pass'],
                    fullname=cml.params['fullname'],
                    description=cml.params['description'],
                    admin=cml.params['admin'],
                    groups=cml.params['groups'],
                )
                cml.result['changed'] = True
            except requests.exceptions.RequestException as e:
                cml.fail_json(name=cml.params['name'], msg=e, rc=-1)
    elif cml.params['state'] == 'absent':
        if userid is not None:
            if module.check_mode:
                module.exit_json(changed=True)
            try:
                cml.client.user_management.delete_user(userid)
                cml.result['changed'] = True
            except requests.exceptions.RequestException as e:
                cml.fail_json(name=cml.params['name'], msg=e, rc=-1)

    cml.exit_json(**cml.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
